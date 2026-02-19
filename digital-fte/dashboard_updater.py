#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Updater - Platinum Tier
Updates Obsidian Dashboard with live status from agents
Roman Urdu: Obsidian Dashboard ko live status se update karna
"""

import os
from datetime import datetime
from pathlib import Path
from skills.vault_skill import read_file, write_file, list_folder

# Roman Urdu: Configuration
VAULT_PATH = "D:/AI_Workspace/AI_Employee_Vault"
DASHBOARD_FILE = "Dashboard.md"


def count_files(folder_path):
    """
    Count markdown files in a folder
    Roman Urdu: Folder mein markdown files ginna
    """
    path = Path(folder_path)
    if not path.exists():
        return 0
    
    count = 0
    for file in path.glob("*.md"):
        if not file.name.startswith("."):
            count += 1
    return count


def get_file_list(folder_path, limit=5):
    """
    Get list of recent files
    Roman Urdu: Haaliya files ki list lena
    """
    path = Path(folder_path)
    if not path.exists():
        return "No files"
    
    files = []
    for file in list(path.glob("*.md"))[:limit]:
        files.append(f"- {file.name}")
    
    return "\n".join(files) if files else "No files"


def get_agent_status():
    """
    Get Cloud and Local agent status
    Roman Urdu: Cloud aur Local agent ka status lena
    """
    # Roman Urdu: Check if orchestrator is running
    import psutil
    
    cloud_running = False
    local_running = False
    
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info.get('cmdline', []) or [])
            if 'orchestrator.py' in cmdline:
                cloud_running = True
                local_running = True
        except:
            pass
    
    return cloud_running, local_running


def get_health_status():
    """
    Get latest health report status
    Roman Urdu: Latest health report ka status lena
    """
    inbox_path = Path(VAULT_PATH) / "Inbox"
    health_reports = list(inbox_path.glob("health_report_*.md"))
    
    if health_reports:
        latest = sorted(health_reports)[-1]
        content = read_file(str(latest))
        
        # Roman Urdu: Extract overall health
        if "overall_health: HEALTHY" in content:
            return "🟢 Healthy", "All systems normal"
        elif "overall_health: WARNING" in content:
            return "🟡 Warning", "Minor issues detected"
        elif "overall_health: CRITICAL" in content:
            return "🔴 Critical", "Major issues detected"
    
    return "⚪ Unknown", "No health report found"


def update_dashboard():
    """
    Update dashboard with current status
    Roman Urdu: Dashboard ko current status se update karna
    """
    print("Updating Dashboard...")
    
    # Roman Urdu: Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Roman Urdu: Count files in each folder
    inbox_count = count_files(Path(VAULT_PATH) / "Inbox")
    needs_action_count = count_files(Path(VAULT_PATH) / "Needs_Action")
    in_progress_count = count_files(Path(VAULT_PATH) / "In_Progress")
    pending_count = count_files(Path(VAULT_PATH) / "Pending_Approval")
    done_count = count_files(Path(VAULT_PATH) / "Done")
    
    # Roman Urdu: Cloud/Local specific counts
    cloud_count = count_files(Path(VAULT_PATH) / "Needs_Action" / "cloud")
    local_count = count_files(Path(VAULT_PATH) / "Needs_Action" / "local")
    
    # Roman Urdu: Get file lists
    in_progress_files = get_file_list(Path(VAULT_PATH) / "In_Progress", limit=5)
    pending_approval_files = get_file_list(Path(VAULT_PATH) / "Pending_Approval", limit=5)
    
    # Roman Urdu: Agent status
    cloud_running, local_running = get_agent_status()
    cloud_status = "[ONLINE]" if cloud_running else "[OFFLINE]"
    local_status = "[ONLINE]" if local_running else "[OFFLINE]"
    orchestrator_status = "[RUNNING]" if (cloud_running and local_running) else "[STOPPED]"
    
    # Roman Urdu: Health status
    health_status, health_details = get_health_status()
    
    # Roman Urdu: Read template
    dashboard_path = Path(VAULT_PATH) / DASHBOARD_FILE
    content = read_file(str(dashboard_path))
    
    # Roman Urdu: Replace placeholders
    replacements = {
        "{{timestamp}}": timestamp,
        "{{inbox_count}}": str(inbox_count),
        "{{needs_action_count}}": str(needs_action_count),
        "{{in_progress_count}}": str(in_progress_count),
        "{{pending_count}}": str(pending_count),
        "{{done_count}}": str(done_count),
        "{{cloud_status}}": cloud_status,
        "{{local_status}}": local_status,
        "{{orchestrator_status}}": orchestrator_status,
        "{{cloud_tasks}}": str(cloud_count),
        "{{local_tasks}}": str(local_count),
        "{{in_progress_files}}": in_progress_files,
        "{{pending_approval_files}}": pending_approval_files,
        "{{vault_status}}": "[OK]",
        "{{cloud_health}}": cloud_status,
        "{{local_health}}": local_status,
        "{{git_status}}": "[NOT CONFIGURED]",
        "{{git_details}}": "No remote configured",
        "{{cloud_details}}": "Operational" if cloud_running else "Not running",
        "{{local_details}}": "Operational" if local_running else "Not running",
        "{{today_completed}}": str(done_count),
        "{{emails_processed}}": str(inbox_count),
        "{{approvals_made}}": str(pending_count),
        "{{last_sync}}": timestamp,
        "{{recent_activity_log}}": f"- Dashboard updated at {timestamp}",
        "{{inbox_status}}": "[ACTIVE]" if inbox_count > 0 else "[EMPTY]",
        "{{needs_action_status}}": "[PENDING]" if needs_action_count > 0 else "[EMPTY]",
        "{{in_progress_status}}": "[ACTIVE]" if in_progress_count > 0 else "[EMPTY]",
        "{{pending_status}}": "[WAITING]" if pending_count > 0 else "[EMPTY]",
        "{{done_status}}": f"[{done_count} done]" if done_count > 0 else "[EMPTY]",
    }
    
    for key, value in replacements.items():
        content = content.replace(key, value)
    
    # Roman Urdu: Write updated dashboard
    success = write_file(str(dashboard_path), content)
    
    if success:
        print(f"[OK] Dashboard updated successfully at {timestamp}")
        print(f"  - Inbox: {inbox_count}")
        print(f"  - Needs Action: {needs_action_count}")
        print(f"  - In Progress: {in_progress_count}")
        print(f"  - Pending Approval: {pending_count}")
        print(f"  - Done: {done_count}")
        print(f"  - Cloud Agent: {cloud_status}")
        print(f"  - Local Agent: {local_status}")
        return True
    else:
        print(f"[FAIL] Failed to update dashboard")
        return False


def main():
    """
    Main function
    Roman Urdu: Main function
    """
    print("=" * 60)
    print("Dashboard Updater - Platinum Tier")
    print("=" * 60)
    
    success = update_dashboard()
    
    if success:
        print("\n[OK] Dashboard update complete!")
        print("\nOpen Obsidian to see live status:")
        print(f"  {VAULT_PATH}\\{DASHBOARD_FILE}")
    else:
        print("\n[FAIL] Dashboard update failed!")


if __name__ == "__main__":
    main()
