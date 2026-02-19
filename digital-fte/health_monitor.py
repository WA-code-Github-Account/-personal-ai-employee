#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Monitor - System Health Monitoring for AI Employee
Checks agent status, vault accessibility, and logs health every 5 minutes
"""

import os
import psutil
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from skills.vault_skill import read_file, write_file, list_folder

# Roman Urdu: Configuration aur global variables
VAULT_PATH = "D:/AI_Workspace/AI_Employee_Vault"
DIGITAL_FTE_PATH = "D:/AI_Workspace_bronze_silver_gold_platinum/digital-fte"
HEALTH_LOG = "health_monitor.log"
HEALTH_REPORT_PATH = "Inbox/health_report.md"
CHECK_INTERVAL_SECONDS = 300  # Roman Urdu: 5 minutes
AGENT_NAME = "Health-Monitor"

# Roman Urdu: Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(HEALTH_LOG),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    System Health Monitor for AI Employee
    Roman Urdu: AI Employee ke liye system health monitor
    """

    def __init__(self, vault_path=None, check_interval=None):
        """
        Initialize Health Monitor
        Roman Urdu: Health Monitor ko initialize karna
        
        Args:
            vault_path (str): Path to vault directory
            check_interval (int): Health check interval in seconds
        """
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.check_interval = check_interval or CHECK_INTERVAL_SECONDS
        self.digital_fte_path = Path(DIGITAL_FTE_PATH)
        
        # Roman Urdu: Agent files to monitor
        self.agent_files = [
            "cloud_agent.py",
            "local_agent.py",
            "agent.py"
        ]
        
        # Roman Urdu: Critical paths to check
        self.critical_paths = [
            self.vault_path,
            self.vault_path / "Inbox",
            self.vault_path / "In_Progress",
            self.vault_path / "Needs_Action",
            self.vault_path / "Needs_Action" / "cloud",
            self.vault_path / "Needs_Action" / "local",
            self.vault_path / "Pending_Approval",
            self.vault_path / "Done"
        ]
        
        # Roman Urdu: Monitoring state
        self.is_running = False
        self.monitor_thread = None
        self.last_check_time = None
        self.health_issues = []
        
        logger.info(f"Health Monitor initialized. Check interval: {self.check_interval}s")

    def check_vault_accessibility(self):
        """
        Check if vault is accessible and writable
        Roman Urdu: Vault accessibility aur writability check karna
        
        Returns:
            dict: Vault status with details
        """
        status = {
            "accessible": True,
            "writable": True,
            "issues": []
        }
        
        # Roman Urdu: Vault existence check
        if not self.vault_path.exists():
            status["accessible"] = False
            status["writable"] = False
            status["issues"].append(f"Vault path does not exist: {self.vault_path}")
            logger.error(f"Vault not accessible: {self.vault_path}")
            return status
        
        # Roman Urdu: Vault readability check
        try:
            list(str(self.vault_path))
        except PermissionError:
            status["accessible"] = False
            status["issues"].append("Vault is not readable (permission denied)")
            logger.error("Vault is not readable")
        
        # Roman Urdu: Vault writability check
        try:
            test_file = self.vault_path / ".health_check_test"
            test_file.write_text("test")
            test_file.unlink()
        except (PermissionError, OSError):
            status["writable"] = False
            status["issues"].append("Vault is not writable (permission denied)")
            logger.error("Vault is not writable")
        
        # Roman Urdu: Critical subdirectories check
        for path in self.critical_paths:
            if not path.exists():
                status["issues"].append(f"Missing critical directory: {path.name}")
                logger.warning(f"Critical directory missing: {path}")
        
        # Roman Urdu: Disk space check
        try:
            import shutil
            total, used, free = shutil.disk_usage(str(self.vault_path))
            free_gb = free / (1024 ** 3)
            
            if free_gb < 1:  # Roman Urdu: Less than 1GB
                status["issues"].append(f"Low disk space: {free_gb:.2f}GB free")
                logger.warning(f"Low disk space: {free_gb:.2f}GB")
        except Exception as e:
            status["issues"].append(f"Could not check disk space: {str(e)}")
        
        logger.info(f"Vault accessibility check complete: {len(status['issues'])} issues")
        return status

    def check_agent_status(self):
        """
        Check if Cloud and Local agents are running
        Roman Urdu: Cloud aur Local agents ka status check karna
        
        Returns:
            dict: Agent status with details
        """
        status = {
            "cloud_agent": {
                "exists": False,
                "running": False,
                "pid": None
            },
            "local_agent": {
                "exists": False,
                "running": False,
                "pid": None
            },
            "issues": []
        }
        
        # Roman Urdu: Agent files existence check
        for agent_file in self.agent_files:
            agent_path = self.digital_fte_path / agent_file
            if agent_path.exists():
                if "cloud" in agent_file:
                    status["cloud_agent"]["exists"] = True
                elif "local" in agent_file:
                    status["local_agent"]["exists"] = True
            else:
                if "cloud" in agent_file:
                    status["cloud_agent"]["exists"] = False
                    status["issues"].append(f"Cloud agent file missing: {agent_file}")
                elif "local" in agent_file:
                    status["local_agent"]["exists"] = False
                    status["issues"].append(f"Local agent file missing: {agent_file}")
        
        # Roman Urdu: Running processes check
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info.get('cmdline', []) or [])
                    
                    # Roman Urdu: Cloud agent process check
                    if 'cloud_agent.py' in cmdline or 'cloud_agent' in cmdline.lower():
                        status["cloud_agent"]["running"] = True
                        status["cloud_agent"]["pid"] = proc.info['pid']
                    
                    # Roman Urdu: Local agent process check
                    if 'local_agent.py' in cmdline or 'local_agent' in cmdline.lower():
                        status["local_agent"]["running"] = True
                        status["local_agent"]["pid"] = proc.info['pid']
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            status["issues"].append(f"Could not check processes: {str(e)}")
            logger.warning(f"Process check failed: {str(e)}")
        
        # Roman Urdu: Agent status warnings
        if status["cloud_agent"]["exists"] and not status["cloud_agent"]["running"]:
            status["issues"].append("Cloud agent file exists but not running")
            logger.warning("Cloud agent not running")
        
        if status["local_agent"]["exists"] and not status["local_agent"]["running"]:
            status["issues"].append("Local agent file exists but not running")
            logger.warning("Local agent not running")
        
        logger.info(f"Agent status check complete: {len(status['issues'])} issues")
        return status

    def check_system_resources(self):
        """
        Check system resources (CPU, Memory, Disk)
        Roman Urdu: System resources check karna
        
        Returns:
            dict: System resource status
        """
        status = {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_available_gb": 0.0,
            "disk_percent": 0.0,
            "issues": []
        }
        
        try:
            # Roman Urdu: CPU usage check
            status["cpu_percent"] = psutil.cpu_percent(interval=1)
            if status["cpu_percent"] > 90:
                status["issues"].append(f"High CPU usage: {status['cpu_percent']}%")
                logger.warning(f"High CPU usage: {status['cpu_percent']}%")
            
            # Roman Urdu: Memory usage check
            memory = psutil.virtual_memory()
            status["memory_percent"] = memory.percent
            status["memory_available_gb"] = memory.available / (1024 ** 3)
            
            if status["memory_percent"] > 90:
                status["issues"].append(f"High memory usage: {status['memory_percent']}%")
                logger.warning(f"High memory usage: {status['memory_percent']}%")
            
            # Roman Urdu: Disk usage check
            disk = psutil.disk_usage(str(self.vault_path))
            status["disk_percent"] = disk.percent
            
            if status["disk_percent"] > 90:
                status["issues"].append(f"High disk usage: {status['disk_percent']}%")
                logger.warning(f"High disk usage: {status['disk_percent']}%")
                
        except Exception as e:
            status["issues"].append(f"Could not check system resources: {str(e)}")
            logger.error(f"System resource check failed: {str(e)}")
        
        logger.info(f"System resources check complete: {len(status['issues'])} issues")
        return status

    def check_log_files(self):
        """
        Check agent log files for recent errors
        Roman Urdu: Agent log files mein recent errors check karna
        
        Returns:
            dict: Log file status
        """
        status = {
            "logs_checked": 0,
            "recent_errors": 0,
            "error_details": [],
            "issues": []
        }
        
        log_files = [
            self.digital_fte_path / "agent.log",
            self.digital_fte_path / "health_monitor.log",
            self.digital_fte_path / "error_recovery.log"
        ]
        
        # Roman Urdu: Current time se 1 hour pehle ka time
        one_hour_ago = datetime.now().timestamp() - 3600
        
        for log_file in log_files:
            if log_file.exists():
                status["logs_checked"] += 1
                
                try:
                    # Roman Urdu: Last 100 lines check karna
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-100:]
                        
                        for line in lines:
                            if 'ERROR' in line or 'CRITICAL' in line:
                                # Roman Urdu: Timestamp parse karna (simple check)
                                status["recent_errors"] += 1
                                status["error_details"].append({
                                    "file": log_file.name,
                                    "line": line.strip()[:200]
                                })
                except Exception as e:
                    status["issues"].append(f"Could not read log {log_file.name}: {str(e)}")
        
        # Roman Urdu: Error threshold check
        if status["recent_errors"] > 10:
            status["issues"].append(f"High error rate: {status['recent_errors']} errors in logs")
            logger.warning(f"High error rate detected: {status['recent_errors']} errors")
        
        logger.info(f"Log files check complete: {status['recent_errors']} recent errors")
        return status

    def run_health_check(self):
        """
        Run complete health check
        Roman Urdu: Complete health check chalana
        
        Returns:
            dict: Complete health status
        """
        logger.info("Running complete health check...")
        
        # Roman Urdu: All checks run karna
        vault_status = self.check_vault_accessibility()
        agent_status = self.check_agent_status()
        system_status = self.check_system_resources()
        log_status = self.check_log_files()
        
        # Roman Urdu: Overall health calculation
        total_issues = (
            len(vault_status["issues"]) +
            len(agent_status["issues"]) +
            len(system_status["issues"]) +
            len(log_status["issues"])
        )
        
        if total_issues == 0:
            overall_health = "HEALTHY"
        elif total_issues <= 3:
            overall_health = "WARNING"
        else:
            overall_health = "CRITICAL"
        
        # Roman Urdu: Health report compile karna
        health_report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "overall_health": overall_health,
            "total_issues": total_issues,
            "vault": vault_status,
            "agents": agent_status,
            "system": system_status,
            "logs": log_status
        }
        
        self.last_check_time = datetime.now()
        self.health_issues = (
            vault_status["issues"] +
            agent_status["issues"] +
            system_status["issues"] +
            log_status["issues"]
        )
        
        logger.info(f"Health check complete: {overall_health} ({total_issues} issues)")
        return health_report

    def generate_health_report(self, health_data=None):
        """
        Generate markdown health report
        Roman Urdu: Markdown health report generate karna
        
        Args:
            health_data (dict): Health data from run_health_check()
            
        Returns:
            str: Path to generated report
        """
        if not health_data:
            health_data = self.run_health_check()
        
        # Roman Urdu: Report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"health_report_{timestamp}.md"
        report_path = self.vault_path / HEALTH_REPORT_PATH
        
        # Roman Urdu: Report directory ensure karna
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Roman Urdu: Markdown report content
        content = f"""---
type: health_report
generated_at: {health_data['timestamp']}
overall_health: {health_data['overall_health']}
total_issues: {health_data['total_issues']}
---

# AI Employee Health Report

**Generated:** {health_data['timestamp']}
**Overall Status:** {health_data['overall_health']}
**Total Issues:** {health_data['total_issues']}

---

## Vault Status

| Check | Status |
|-------|--------|
| Accessible | {'✓' if health_data['vault']['accessible'] else '✗'} |
| Writable | {'✓' if health_data['vault']['writable'] else '✗'} |

### Vault Issues
{chr(10).join(f'- {issue}' for issue in health_data['vault']['issues']) or 'No issues'}

---

## Agent Status

| Agent | Exists | Running | PID |
|-------|--------|---------|-----|
| Cloud Agent | {'✓' if health_data['agents']['cloud_agent']['exists'] else '✗'} | {'✓' if health_data['agents']['cloud_agent']['running'] else '✗'} | {health_data['agents']['cloud_agent']['pid'] or 'N/A'} |
| Local Agent | {'✓' if health_data['agents']['local_agent']['exists'] else '✗'} | {'✓' if health_data['agents']['local_agent']['running'] else '✗'} | {health_data['agents']['local_agent']['pid'] or 'N/A'} |

### Agent Issues
{chr(10).join(f'- {issue}' for issue in health_data['agents']['issues']) or 'No issues'}

---

## System Resources

| Resource | Usage | Status |
|----------|-------|--------|
| CPU | {health_data['system']['cpu_percent']:.1f}% | {'⚠️ HIGH' if health_data['system']['cpu_percent'] > 90 else '✓ OK'} |
| Memory | {health_data['system']['memory_percent']:.1f}% ({health_data['system']['memory_available_gb']:.2f}GB free) | {'⚠️ HIGH' if health_data['system']['memory_percent'] > 90 else '✓ OK'} |
| Disk | {health_data['system']['disk_percent']:.1f}% | {'⚠️ HIGH' if health_data['system']['disk_percent'] > 90 else '✓ OK'} |

### System Issues
{chr(10).join(f'- {issue}' for issue in health_data['system']['issues']) or 'No issues'}

---

## Log Analysis

- **Logs Checked:** {health_data['logs']['logs_checked']}
- **Recent Errors:** {health_data['logs']['recent_errors']}

### Recent Errors
{chr(10).join(f'- [{err["file"]}] {err["line"]}' for err in health_data['logs']['error_details'][:10]) or 'No recent errors'}

### Log Issues
{chr(10).join(f'- {issue}' for issue in health_data['logs']['issues']) or 'No issues'}

---

## All Issues Summary

{chr(10).join(f'- {issue}' for issue in self.health_issues) or 'No issues detected. System is healthy! ✓'}

---

*Report generated by Health Monitor - Platinum Tier*
"""
        
        # Roman Urdu: Report file write karna
        success = write_file(str(report_path), content)
        
        if success:
            logger.info(f"Health report generated: {report_path}")
            return str(report_path)
        else:
            logger.error(f"Failed to generate health report: {report_path}")
            return None

    def _monitoring_loop(self):
        """
        Internal monitoring loop (runs in background thread)
        Roman Urdu: Internal monitoring loop (background thread mein chalta hai)
        """
        logger.info("Health monitoring loop started")
        
        while self.is_running:
            try:
                # Roman Urdu: Health check run karna
                health_data = self.run_health_check()
                
                # Roman Urdu: Report generate karna
                self.generate_health_report(health_data)
                
                # Roman Urdu: Critical issues par alert
                if health_data['overall_health'] == 'CRITICAL':
                    logger.critical("CRITICAL health issues detected! Immediate attention required.")
                    self._create_critical_alert(health_data)
                elif health_data['overall_health'] == 'WARNING':
                    logger.warning("WARNING: Health issues detected")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            
            # Roman Urdu: Sleep for check interval
            time.sleep(self.check_interval)
        
        logger.info("Health monitoring loop stopped")

    def _create_critical_alert(self, health_data):
        """
        Create critical alert file
        Roman Urdu: Critical alert file banana
        
        Args:
            health_data (dict): Health data with critical issues
        """
        alert_path = self.vault_path / "Inbox" / "CRITICAL_ALERT.md"
        
        content = f"""---
type: critical_alert
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
severity: CRITICAL
---

# ⚠️ CRITICAL HEALTH ALERT

**Time:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Critical Issues Detected

{chr(10).join(f'- {issue}' for issue in self.health_issues)}

## Immediate Actions Required

1. Review system resources (CPU, Memory, Disk)
2. Check agent processes
3. Verify vault accessibility
4. Review error logs

---
*Generated by Health Monitor*
"""
        
        write_file(str(alert_path), content)
        logger.critical(f"Critical alert created: {alert_path}")

    def start_monitoring(self):
        """
        Start background health monitoring
        Roman Urdu: Background health monitoring start karna
        
        Returns:
            bool: True if started successfully
        """
        if self.is_running:
            logger.warning("Health monitoring is already running")
            return False
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("Health monitoring started (background thread)")
        return True

    def stop_monitoring(self):
        """
        Stop background health monitoring
        Roman Urdu: Background health monitoring stop karna
        
        Returns:
            bool: True if stopped successfully
        """
        if not self.is_running:
            logger.warning("Health monitoring is not running")
            return False
        
        self.is_running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        logger.info("Health monitoring stopped")
        return True

    def get_current_status(self):
        """
        Get current monitoring status
        Roman Urdu: Current monitoring status lena
        
        Returns:
            dict: Current status
        """
        return {
            "is_running": self.is_running,
            "last_check": self.last_check_time.strftime("%Y-%m-%d %H:%M:%S") if self.last_check_time else None,
            "check_interval": self.check_interval,
            "current_issues": len(self.health_issues),
            "issues": self.health_issues
        }


def main():
    """
    Main function to demonstrate Health Monitor capabilities
    Roman Urdu: Health Monitor capabilities ko demonstrate karna
    """
    print("=" * 60)
    print("Health Monitor - System Health Monitoring")
    print("=" * 60)
    
    # Initialize monitor
    monitor = HealthMonitor()
    
    # Demo: Run single health check
    print("\n[Demo] Running Health Check:")
    health_data = monitor.run_health_check()
    print(f"  Overall Health: {health_data['overall_health']}")
    print(f"  Total Issues: {health_data['total_issues']}")
    
    # Demo: Vault status
    print("\n[Demo] Vault Status:")
    print(f"  Accessible: {'✓' if health_data['vault']['accessible'] else '✗'}")
    print(f"  Writable: {'✓' if health_data['vault']['writable'] else '✗'}")
    
    # Demo: Agent status
    print("\n[Demo] Agent Status:")
    print(f"  Cloud Agent - Exists: {'✓' if health_data['agents']['cloud_agent']['exists'] else '✗'}, Running: {'✓' if health_data['agents']['cloud_agent']['running'] else '✗'}")
    print(f"  Local Agent - Exists: {'✓' if health_data['agents']['local_agent']['exists'] else '✗'}, Running: {'✓' if health_data['agents']['local_agent']['running'] else '✗'}")
    
    # Demo: System resources
    print("\n[Demo] System Resources:")
    print(f"  CPU: {health_data['system']['cpu_percent']:.1f}%")
    print(f"  Memory: {health_data['system']['memory_percent']:.1f}%")
    print(f"  Disk: {health_data['system']['disk_percent']:.1f}%")
    
    # Demo: Generate report
    print("\n[Demo] Generating Health Report:")
    report_path = monitor.generate_health_report(health_data)
    print(f"  Report: {report_path}")
    
    # Demo: Start monitoring
    print("\n[Demo] Starting Background Monitoring (10 seconds):")
    monitor.start_monitoring()
    time.sleep(10)
    monitor.stop_monitoring()
    print("  Monitoring stopped")
    
    # Demo: Current status
    print("\n[Demo] Current Status:")
    status = monitor.get_current_status()
    print(f"  Is Running: {status['is_running']}")
    print(f"  Last Check: {status['last_check']}")
    print(f"  Current Issues: {status['current_issues']}")
    
    print("\n" + "=" * 60)
    print("Health Monitor demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
