#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Platinum Tier Agent Coordinator
Coordinates Cloud and Local agents with thread management, task locking, and offline handling
"""

import os
import time
import logging
import threading
import queue
import shutil
from datetime import datetime
from pathlib import Path
from skills.vault_skill import read_file, write_file, move_file, list_folder

# Roman Urdu: Configuration aur global variables
VAULT_PATH = "D:/AI_Workspace/AI_Employee_Vault"
DIGITAL_FTE_PATH = "D:/AI_Workspace_bronze_silver_gold_platinum/digital-fte"

# Roman Urdu: Domain paths
CLOUD_DOMAIN = "Needs_Action/cloud"
LOCAL_DOMAIN = "Needs_Action/local"
IN_PROGRESS = "In_Progress"
PENDING_APPROVAL = "Pending_Approval"
DONE = "Done"
INBOX = "Inbox"

# Roman Urdu: Lock file path
LOCK_DIR = "Inbox/.locks"
COORDINATION_LOG = "Inbox/orchestration_log.md"

AGENT_NAME = "Orchestrator"
LOG_FILE = "agent.log"

# Roman Urdu: Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskLock:
    """
    Task locking mechanism to prevent double-work
    Roman Urdu: Double-work rokne ke liye task locking system
    """

    def __init__(self, vault_path=None):
        """
        Initialize Task Lock manager
        Roman Urdu: Task Lock manager ko initialize karna
        
        Args:
            vault_path (str): Path to vault directory
        """
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.lock_dir = self.vault_path / LOCK_DIR
        self.locks = {}  # Roman Urdu: In-memory locks cache
        self.lock_timeout = 300  # Roman Urdu: 5 minutes timeout
        
        # Roman Urdu: Lock directory ensure karna
        self._ensure_lock_dir()

    def _ensure_lock_dir(self):
        """
        Ensure lock directory exists
        Roman Urdu: Lock directory ko ensure karna
        """
        if not self.lock_dir.exists():
            self.lock_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created lock directory: {LOCK_DIR}")

    def acquire_lock(self, task_name, agent_type):
        """
        Acquire lock on a task
        Roman Urdu: Task par lock lena
        
        Args:
            task_name (str): Name of the task
            agent_type (str): Type of agent (cloud/local/orchestrator)
            
        Returns:
            bool: True if lock acquired, False if already locked
        """
        lock_file = self.lock_dir / f"{task_name}.lock"
        
        # Roman Urdu: Check if lock exists and is not expired
        if lock_file.exists():
            try:
                lock_content = read_file(str(lock_file))
                if lock_content:
                    # Roman Urdu: Lock metadata parse karna
                    lock_time = None
                    lock_agent = None
                    
                    for line in lock_content.split('\n'):
                        if 'locked_at:' in line:
                            lock_time_str = line.split('locked_at:')[1].strip()
                            try:
                                lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                            except:
                                pass
                        if 'locked_by:' in line:
                            lock_agent = line.split('locked_by:')[1].strip()
                    
                    # Roman Urdu: Check if lock is expired
                    if lock_time:
                        elapsed = (datetime.now() - lock_time).total_seconds()
                        if elapsed < self.lock_timeout:
                            logger.warning(f"Task already locked by {lock_agent} ({elapsed:.0f}s ago): {task_name}")
                            return False
                        else:
                            # Roman Urdu: Lock expired, stale lock remove karna
                            logger.info(f"Lock expired for task: {task_name}. Releasing stale lock.")
                            self._release_lock_file(task_name)
            except Exception as e:
                logger.error(f"Error reading lock file: {str(e)}")
        
        # Roman Urdu: New lock create karna
        lock_content = f"""---
task: {task_name}
locked_by: {agent_type}
locked_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: locked
---

# Task Lock
This task is being processed by {agent_type}.
Do not process simultaneously.
"""
        
        success = write_file(str(lock_file), lock_content)
        
        if success:
            self.locks[task_name] = {
                "agent": agent_type,
                "time": datetime.now()
            }
            logger.info(f"Lock acquired by {agent_type}: {task_name}")
            return True
        
        return False

    def release_lock(self, task_name, agent_type):
        """
        Release lock on a task
        Roman Urdu: Task se lock release karna
        
        Args:
            task_name (str): Name of the task
            agent_type (str): Type of agent releasing the lock
            
        Returns:
            bool: True if released, False otherwise
        """
        return self._release_lock_file(task_name)

    def _release_lock_file(self, task_name):
        """
        Remove lock file
        Roman Urdu: Lock file ko remove karna
        
        Args:
            task_name (str): Name of the task
            
        Returns:
            bool: True if removed, False otherwise
        """
        lock_file = self.lock_dir / f"{task_name}.lock"
        
        try:
            if lock_file.exists():
                os.remove(str(lock_file))
                logger.info(f"Lock released: {task_name}")
                
                if task_name in self.locks:
                    del self.locks[task_name]
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error releasing lock: {str(e)}")
            return False

    def is_locked(self, task_name):
        """
        Check if task is locked
        Roman Urdu: Check karna ke task locked hai ya nahi
        
        Args:
            task_name (str): Name of the task
            
        Returns:
            bool: True if locked, False otherwise
        """
        lock_file = self.lock_dir / f"{task_name}.lock"
        
        if not lock_file.exists():
            return False
        
        # Roman Urdu: Check if lock is expired
        try:
            lock_content = read_file(str(lock_file))
            if lock_content:
                for line in lock_content.split('\n'):
                    if 'locked_at:' in line:
                        lock_time_str = line.split('locked_at:')[1].strip()
                        try:
                            lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                            elapsed = (datetime.now() - lock_time).total_seconds()
                            return elapsed < self.lock_timeout
                        except:
                            return True
            return False
        except:
            return True

    def cleanup_expired_locks(self):
        """
        Clean up expired locks
        Roman Urdu: Expired locks ko clean karna
        
        Returns:
            int: Number of locks cleaned
        """
        cleaned = 0
        
        if not self.lock_dir.exists():
            return 0
        
        for lock_file in self.lock_dir.glob("*.lock"):
            task_name = lock_file.stem
            
            try:
                lock_content = read_file(str(lock_file))
                if lock_content:
                    for line in lock_content.split('\n'):
                        if 'locked_at:' in line:
                            lock_time_str = line.split('locked_at:')[1].strip()
                            try:
                                lock_time = datetime.strptime(lock_time_str, "%Y-%m-%d %H:%M:%S")
                                elapsed = (datetime.now() - lock_time).total_seconds()
                                
                                if elapsed >= self.lock_timeout:
                                    self._release_lock_file(task_name)
                                    cleaned += 1
                            except:
                                pass
            except:
                pass
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired locks")
        
        return cleaned


class AgentStatus:
    """
    Agent status tracker
    Roman Urdu: Agent status tracker
    """

    def __init__(self):
        """
        Initialize Agent Status
        Roman Urdu: Agent Status ko initialize karna
        """
        self.cloud_online = False
        self.local_online = False
        self.cloud_thread = None
        self.local_thread = None
        self.last_cloud_heartbeat = None
        self.last_local_heartbeat = None
        self.cloud_tasks_processed = 0
        self.local_tasks_processed = 0


class Orchestrator:
    """
    Main Orchestrator for Cloud and Local agents
    Roman Urdu: Cloud aur Local agents ke liye main Orchestrator
    """

    def __init__(self, vault_path=None):
        """
        Initialize Orchestrator
        Roman Urdu: Orchestrator ko initialize karna
        
        Args:
            vault_path (str): Path to vault directory
        """
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.cloud_domain = self.vault_path / CLOUD_DOMAIN
        self.local_domain = self.vault_path / LOCAL_DOMAIN
        self.in_progress = self.vault_path / IN_PROGRESS
        self.pending_approval = self.vault_path / PENDING_APPROVAL
        self.done = self.vault_path / DONE
        self.inbox = self.vault_path / INBOX
        
        # Roman Urdu: Ensure directories exist
        self._ensure_directories()
        
        # Roman Urdu: Components initialize karna
        self.task_lock = TaskLock(vault_path)
        self.agent_status = AgentStatus()
        
        # Roman Urdu: Communication queues
        self.cloud_queue = queue.Queue()
        self.local_queue = queue.Queue()
        self.coordination_queue = queue.Queue()
        
        # Roman Urdu: Running state
        self.is_running = False
        self.demo_mode = False
        
        # Roman Urdu: Coordination log
        self.coordination_log = []
        
        logger.info("Orchestrator initialized")

    def _ensure_directories(self):
        """
        Ensure all required directories exist
        Roman Urdu: Saare required directories ko ensure karna
        """
        for directory in [
            self.cloud_domain,
            self.local_domain,
            self.in_progress,
            self.pending_approval,
            self.done,
            self.inbox,
            self.vault_path / LOCK_DIR
        ]:
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory.name}")

    def _log_coordination(self, event_type, details):
        """
        Log coordination event
        Roman Urdu: Coordination event ko log karna
        
        Args:
            event_type (str): Type of event
            details (str): Event details
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "type": event_type,
            "details": details
        }
        
        self.coordination_log.append(log_entry)
        
        # Roman Urdu: Log to file
        self._write_coordination_log()
        
        logger.info(f"[{event_type}] {details}")

    def _write_coordination_log(self):
        """
        Write coordination log to file
        Roman Urdu: Coordination log ko file mein likhna
        """
        content = f"""---
type: orchestration_log
updated_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
total_events: {len(self.coordination_log)}
---

# Orchestration Coordination Log

## Recent Events

| Timestamp | Event Type | Details |
|-----------|------------|---------|
"""
        
        # Roman Urdu: Last 50 events show karna
        for entry in self.coordination_log[-50:]:
            content += f"| {entry['timestamp']} | {entry['type']} | {entry['details'][:50]}... |\n"
        
        content += f"""
## Statistics
- Cloud Tasks Processed: {self.agent_status.cloud_tasks_processed}
- Local Tasks Processed: {self.agent_status.local_tasks_processed}
- Cloud Status: {'Online' if self.agent_status.cloud_online else 'Offline'}
- Local Status: {'Online' if self.agent_status.local_online else 'Offline'}

---
*Generated by Orchestrator - Platinum Tier*
"""
        
        log_path = self.vault_path / COORDINATION_LOG
        write_file(str(log_path), content)

    def claim_task(self, filename, agent_type, source_domain=None):
        """
        Claim a task using claim-by-move rule
        Roman Urdu: Claim-by-move rule use karke task claim karna
        
        Args:
            filename (str): Name of the task file
            agent_type (str): Type of agent (cloud/local)
            source_domain (str): Source domain path
            
        Returns:
            bool: True if claimed successfully
        """
        # Roman Urdu: Pehle lock acquire karna
        if not self.task_lock.acquire_lock(filename, agent_type):
            self._log_coordination("CLAIM_FAILED", f"Task already locked: {filename}")
            return False
        
        # Roman Urdu: Source domain determine karna
        if not source_domain:
            if agent_type == "cloud":
                source_domain = self.cloud_domain
            else:
                source_domain = self.local_domain
        
        source = source_domain / filename
        dest = self.in_progress / filename
        
        # Roman Urdu: Check if file exists
        if not source.exists():
            # Roman Urdu: Check pending approval mein bhi
            source = self.pending_approval / filename
        
        if not source.exists():
            self._log_coordination("CLAIM_FAILED", f"Task not found: {filename}")
            self.task_lock.release_lock(filename, agent_type)
            return False
        
        # Roman Urdu: Move to In_Progress
        try:
            success = move_file(str(source), str(dest))
            
            if success:
                # Roman Urdu: Claim metadata add karna
                self._add_claim_metadata(dest, agent_type)
                self._log_coordination("TASK_CLAIMED", f"{agent_type} claimed: {filename}")
                
                # Roman Urdu: Agent counters update karna
                if agent_type == "cloud":
                    self.agent_status.cloud_tasks_processed += 1
                else:
                    self.agent_status.local_tasks_processed += 1
                
                return True
            else:
                self._log_coordination("CLAIM_FAILED", f"Move failed: {filename}")
                self.task_lock.release_lock(filename, agent_type)
                return False
        except Exception as e:
            self._log_coordination("CLAIM_ERROR", f"Error claiming {filename}: {str(e)}")
            self.task_lock.release_lock(filename, agent_type)
            return False

    def _add_claim_metadata(self, file_path, agent_type):
        """
        Add claim metadata to task file
        Roman Urdu: Task file mein claim metadata add karna
        
        Args:
            file_path (Path): Path to the task file
            agent_type (str): Type of agent
        """
        try:
            content = read_file(str(file_path))
            if content:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Roman Urdu: Metadata header add/update karna
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 2:
                        frontmatter = parts[1].strip()
                        if "claimed_by:" not in frontmatter:
                            frontmatter += f"\nclaimed_by: {agent_type}"
                        if "claimed_at:" not in frontmatter:
                            frontmatter += f"\nclaimed_at: {timestamp}"
                        if "status:" not in frontmatter:
                            frontmatter += f"\nstatus: in_progress"
                        
                        updated_content = f"---\n{frontmatter}\n---\n{parts[2] if len(parts) > 2 else ''}"
                    else:
                        updated_content = content
                else:
                    metadata = f"""---
claimed_by: {agent_type}
claimed_at: {timestamp}
status: in_progress
---

"""
                    updated_content = metadata + content
                
                write_file(str(file_path), updated_content)
        except Exception as e:
            logger.error(f"Error adding claim metadata: {str(e)}")

    def release_task(self, filename, destination="done"):
        """
        Release task after completion
        Roman Urdu: Completion ke baad task release karna
        
        Args:
            filename (str): Name of the task file
            destination (str): Destination folder (done/pending_approval)
            
        Returns:
            bool: True if released successfully
        """
        source = self.in_progress / filename
        
        if destination == "done":
            dest = self.done / filename
        elif destination == "pending_approval":
            dest = self.pending_approval / filename
        else:
            dest = self.done / filename
        
        if not source.exists():
            logger.error(f"Task not found in In_Progress: {filename}")
            return False
        
        try:
            # Roman Urdu: Update status
            content = read_file(str(source))
            if content:
                updated_content = content.replace("status: in_progress", f"status: {destination.replace('_', '_')}")
                updated_content = updated_content.replace("status: approved", f"status: {destination.replace('_', '_')}")
                write_file(str(source), updated_content)
            
            # Roman Urdu: Move to destination
            success = move_file(str(source), str(dest))
            
            if success:
                self._log_coordination("TASK_RELEASED", f"Released to {destination}: {filename}")
                self.task_lock.release_lock(filename, "orchestrator")
                return True
            return False
        except Exception as e:
            logger.error(f"Error releasing task: {str(e)}")
            return False

    def cloud_agent_loop(self):
        """
        Cloud agent processing loop (runs in thread)
        Roman Urdu: Cloud agent processing loop (thread mein chalta hai)
        """
        logger.info("Cloud agent thread started")
        self.agent_status.cloud_online = True
        self.agent_status.last_cloud_heartbeat = datetime.now()
        
        self._log_coordination("AGENT_STARTED", "Cloud agent thread started")
        
        while self.is_running:
            try:
                # Roman Urdu: Check cloud domain for new tasks
                if self.cloud_domain.exists():
                    files = list_folder(str(self.cloud_domain))
                    
                    for filename in files:
                        if filename.endswith(".md"):
                            # Roman Urdu: Check if task is already locked
                            if self.task_lock.is_locked(filename):
                                continue
                            
                            # Roman Urdu: Claim and process task
                            if self.claim_task(filename, "cloud"):
                                self._process_cloud_task(filename)
                
                # Roman Urdu: Heartbeat update
                self.agent_status.last_cloud_heartbeat = datetime.now()
                
                # Roman Urdu: Sleep before next check
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in cloud agent loop: {str(e)}")
                self._log_coordination("CLOUD_ERROR", f"Cloud agent error: {str(e)}")
                time.sleep(10)
        
        self.agent_status.cloud_online = False
        self._log_coordination("AGENT_STOPPED", "Cloud agent thread stopped")

    def _process_cloud_task(self, filename):
        """
        Process a cloud task
        Roman Urdu: Cloud task ko process karna
        
        Args:
            filename (str): Name of the task file
        """
        self._log_coordination("CLOUD_PROCESSING", f"Processing: {filename}")
        
        file_path = self.in_progress / filename
        
        try:
            content = read_file(str(file_path))
            
            if not content:
                return
            
            # Roman Urdu: Task type check karna
            task_type = "general"
            if "type: email_task" in content:
                task_type = "email"
            elif "type: social_post_draft" in content:
                task_type = "social"
            
            # Roman Urdu: Task processing simulation
            if task_type == "email":
                # Roman Urdu: Email draft reply generate karna
                if "## Draft Reply" in content:
                    self._log_coordination("CLOUD_ACTION", f"Draft reply exists for: {filename}")
                else:
                    # Roman Urdu: Auto-generate acknowledgment draft
                    draft = """
## Draft Reply

Dear Sender,

Thank you for your email. This is an automated acknowledgment.
Our team will review your message and respond within 24 hours.

Best regards,
AI Employee System
"""
                    content += draft
                    write_file(str(file_path), content)
                    self._log_coordination("CLOUD_ACTION", f"Draft reply generated for: {filename}")
            
            # Roman Urdu: Task ko approval ke liye bhejna
            self.release_task(filename, "pending_approval")
            self._log_coordination("CLOUD_COMPLETE", f"Task sent to Pending_Approval: {filename}")
            
        except Exception as e:
            logger.error(f"Error processing cloud task {filename}: {str(e)}")
            self._log_coordination("CLOUD_ERROR", f"Error processing {filename}: {str(e)}")
            # Roman Urdu: Lock release karna on error
            self.task_lock.release_lock(filename, "orchestrator")

    def local_agent_loop(self):
        """
        Local agent processing loop (runs in thread)
        Roman Urdu: Local agent processing loop (thread mein chalta hai)
        """
        logger.info("Local agent thread started")
        self.agent_status.local_online = True
        self.agent_status.last_local_heartbeat = datetime.now()
        
        self._log_coordination("AGENT_STARTED", "Local agent thread started")
        
        while self.is_running:
            try:
                # Roman Urdu: Check pending approval for tasks needing approval
                if self.pending_approval.exists():
                    files = list_folder(str(self.pending_approval))
                    
                    for filename in files:
                        if filename.endswith(".md"):
                            # Roman Urdu: Check if task is already locked
                            if self.task_lock.is_locked(filename):
                                continue
                            
                            # Roman Urdu: Claim and process task
                            if self.claim_task(filename, "local", self.pending_approval):
                                self._process_local_task(filename)
                
                # Roman Urdu: Check local domain for local-specific tasks
                if self.local_domain.exists():
                    files = list_folder(str(self.local_domain))
                    
                    for filename in files:
                        if filename.endswith(".md"):
                            if self.task_lock.is_locked(filename):
                                continue
                            
                            if self.claim_task(filename, "local"):
                                self._process_local_task(filename)
                
                # Roman Urdu: Heartbeat update
                self.agent_status.last_local_heartbeat = datetime.now()
                
                # Roman Urdu: Sleep before next check
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in local agent loop: {str(e)}")
                self._log_coordination("LOCAL_ERROR", f"Local agent error: {str(e)}")
                time.sleep(10)
        
        self.agent_status.local_online = False
        self._log_coordination("AGENT_STOPPED", "Local agent thread stopped")

    def _process_local_task(self, filename):
        """
        Process a local task
        Roman Urdu: Local task ko process karna
        
        Args:
            filename (str): Name of the task file
        """
        self._log_coordination("LOCAL_PROCESSING", f"Processing: {filename}")
        
        file_path = self.in_progress / filename
        
        try:
            content = read_file(str(file_path))
            
            if not content:
                return
            
            # Roman Urdu: Task type check karna
            task_type = "general"
            if "type: payment_task" in content:
                task_type = "payment"
            elif "type: whatsapp_task" in content:
                task_type = "whatsapp"
            elif "type: email_task" in content:
                task_type = "email"
            
            # Roman Urdu: Demo mode mein auto-approve
            if self.demo_mode:
                self._log_coordination("LOCAL_ACTION", f"Auto-approving in demo mode: {filename}")
                
                # Roman Urdu: Approval metadata add karna
                approval_section = f"""
## Approval
- **Approved at:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Approved by:** Local Agent (Demo Mode)
- **Status:** APPROVED
"""
                content += approval_section
                write_file(str(file_path), content)
                
                # Roman Urdu: Send action simulate karna
                time.sleep(2)  # Roman Urdu: Simulated delay
                
                self._log_coordination("LOCAL_ACTION", f"Sending task: {filename}")
                self.release_task(filename, "done")
            else:
                # Roman Urdu: Normal mode - requires user approval
                self._log_coordination("LOCAL_WAITING", f"Waiting for user approval: {filename}")
                # Roman Urdu: Yahan user approval ka wait karna hoga
                # For now, move to done after a delay
                time.sleep(3)
                self.release_task(filename, "done")
            
        except Exception as e:
            logger.error(f"Error processing local task {filename}: {str(e)}")
            self._log_coordination("LOCAL_ERROR", f"Error processing {filename}: {str(e)}")
            self.task_lock.release_lock(filename, "orchestrator")

    def handle_cloud_offline(self):
        """
        Handle scenario when Cloud agent is offline
        Roman Urdu: Cloud agent offline hone par handle karna
        """
        if self.agent_status.cloud_online:
            return
        
        self._log_coordination("CLOUD_OFFLINE", "Cloud agent is offline - queuing tasks")
        
        # Roman Urdu: Tasks ko queue mein daalna
        # Roman Urdu: New emails ko inbox mein store karna
        # Roman Urdu: Jab cloud online hoga, tab process honge
        
        logger.warning("Cloud agent offline. Incoming cloud tasks will be queued.")

    def handle_local_offline(self):
        """
        Handle scenario when Local agent is offline
        Roman Urdu: Local agent offline hone par handle karna
        """
        if self.agent_status.local_online:
            return
        
        self._log_coordination("LOCAL_OFFLINE", "Local agent is offline - pending approvals waiting")
        
        # Roman Urdu: Pending approvals ko hold karna
        # Roman Urdu: Cloud tasks Pending_Approval mein accumulate honge
        
        logger.warning("Local agent offline. Approvals and sends are on hold.")

    def start(self):
        """
        Start orchestrator and agent threads
        Roman Urdu: Orchestrator aur agent threads ko start karna
        
        Returns:
            bool: True if started successfully
        """
        if self.is_running:
            logger.warning("Orchestrator is already running")
            return False
        
        self.is_running = True
        self._log_coordination("ORCHESTRATOR_STARTED", "Orchestrator starting...")
        
        # Roman Urdu: Cloud agent thread
        self.agent_status.cloud_thread = threading.Thread(
            target=self.cloud_agent_loop,
            name="CloudAgent",
            daemon=True
        )
        self.agent_status.cloud_thread.start()
        
        # Roman Urdu: Local agent thread
        self.agent_status.local_thread = threading.Thread(
            target=self.local_agent_loop,
            name="LocalAgent",
            daemon=True
        )
        self.agent_status.local_thread.start()
        
        # Roman Urdu: Offline monitoring thread
        offline_thread = threading.Thread(
            target=self._offline_monitor_loop,
            name="OfflineMonitor",
            daemon=True
        )
        offline_thread.start()
        
        self._log_coordination("ORCHESTRATOR_STARTED", "All threads started")
        logger.info("Orchestrator started all threads")
        
        return True

    def stop(self):
        """
        Stop orchestrator and agent threads
        Roman Urdu: Orchestrator aur agent threads ko stop karna
        
        Returns:
            bool: True if stopped successfully
        """
        if not self.is_running:
            logger.warning("Orchestrator is not running")
            return False
        
        self.is_running = False
        self._log_coordination("ORCHESTRATOR_STOPPING", "Stopping orchestrator...")
        
        # Roman Urdu: Threads ko join karna
        if self.agent_status.cloud_thread:
            self.agent_status.cloud_thread.join(timeout=10)
        
        if self.agent_status.local_thread:
            self.agent_status.local_thread.join(timeout=10)
        
        # Roman Urdu: Expired locks cleanup
        self.task_lock.cleanup_expired_locks()
        
        self._log_coordination("ORCHESTRATOR_STOPPED", "Orchestrator stopped")
        logger.info("Orchestrator stopped")
        
        return True

    def _offline_monitor_loop(self):
        """
        Monitor agent offline status
        Roman Urdu: Agent offline status ko monitor karna
        """
        while self.is_running:
            try:
                # Roman Urdu: Cloud agent heartbeat check
                if self.agent_status.cloud_online:
                    elapsed = (datetime.now() - self.agent_status.last_cloud_heartbeat).total_seconds()
                    if elapsed > 30:  # Roman Urdu: 30 seconds no heartbeat
                        self.agent_status.cloud_online = False
                        self.handle_cloud_offline()
                
                # Roman Urdu: Local agent heartbeat check
                if self.agent_status.local_online:
                    elapsed = (datetime.now() - self.agent_status.last_local_heartbeat).total_seconds()
                    if elapsed > 30:
                        self.agent_status.local_online = False
                        self.handle_local_offline()
                
                time.sleep(10)
            except Exception as e:
                logger.error(f"Error in offline monitor: {str(e)}")
                time.sleep(10)

    def get_status(self):
        """
        Get orchestrator status
        Roman Urdu: Orchestrator status lena
        
        Returns:
            dict: Current status
        """
        return {
            "is_running": self.is_running,
            "cloud_online": self.agent_status.cloud_online,
            "local_online": self.agent_status.local_online,
            "cloud_tasks": self.agent_status.cloud_tasks_processed,
            "local_tasks": self.agent_status.local_tasks_processed,
            "active_locks": len(self.task_lock.locks)
        }


def run_demo():
    """
    Demo mode: Simulates complete workflow
    Roman Urdu: Demo mode: Complete workflow simulate karna
    """
    print("=" * 70)
    print("ORCHESTRATOR DEMO MODE")
    print("Simulating: Email arrives -> Cloud drafts -> Local approves -> Send")
    print("=" * 70)
    
    # Roman Urdu: Orchestrator initialize karna
    orchestrator = Orchestrator()
    orchestrator.demo_mode = True
    
    # Roman Urdu: Step 1: Simulate email arriving while Local is offline
    print("\n[STEP 1] Simulating email arrival (Local agent OFFLINE)...")
    orchestrator._log_coordination("DEMO_STEP", "Step 1: Email arriving")
    
    # Roman Urdu: Local agent ko offline mark karna
    orchestrator.agent_status.local_online = False
    
    # Roman Urdu: Email task create karna
    email_filename = f"demo_email_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    email_content = f"""---
type: email_task
domain: cloud
priority: high
created_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
sender: demo@example.com
subject: Demo: Project Inquiry
status: pending
---

# Email Task

## Original Email
- **From:** demo@example.com
- **Subject:** Demo: Project Inquiry
- **Received:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Body
Hi,

I'm interested in your AI automation services. Can we schedule a call?

Best regards,
Demo Client

## Draft Reply
<!-- Cloud Agent: Draft reply yahan likhen -->
"""
    
    email_path = orchestrator.cloud_domain / email_filename
    write_file(str(email_path), email_content)
    print(f"  [OK] Email task created: {email_filename}")
    orchestrator._log_coordination("EMAIL_ARRIVED", f"Demo email created: {email_filename}")
    
    # Roman Urdu: Step 2: Start Cloud agent (Local still offline)
    print("\n[STEP 2] Starting Cloud agent (Local still OFFLINE)...")
    orchestrator._log_coordination("DEMO_STEP", "Step 2: Cloud agent processing")
    
    orchestrator.is_running = True
    orchestrator.agent_status.cloud_online = True
    
    # Roman Urdu: Cloud agent manually process karna
    print("  Cloud agent processing email...")
    if orchestrator.claim_task(email_filename, "cloud"):
        orchestrator._process_cloud_task(email_filename)
        print(f"  [OK] Cloud drafted reply and moved to Pending_Approval")
    
    # Roman Urdu: Step 3: Local agent comes online
    print("\n[STEP 3] Local agent comes ONLINE...")
    orchestrator.agent_status.local_online = True
    orchestrator._log_coordination("DEMO_STEP", "Step 3: Local agent online")
    print("  [OK] Local agent is now online")
    
    # Roman Urdu: Step 4: Local agent processes pending approval
    print("\n[STEP 4] Local agent processes Pending_Approval...")
    orchestrator._log_coordination("DEMO_STEP", "Step 4: Local approval and send")
    
    # Roman Urdu: Local agent manually process karna
    print("  Local agent reviewing and approving...")
    time.sleep(1)
    
    if orchestrator.claim_task(email_filename, "local", orchestrator.pending_approval):
        orchestrator._process_local_task(email_filename)
        print(f"  [OK] Local approved and sent email")
    
    # Roman Urdu: Step 5: Show final status
    print("\n[STEP 5] Final Status:")
    status = orchestrator.get_status()
    print(f"  Cloud Tasks Processed: {status['cloud_tasks']}")
    print(f"  Local Tasks Processed: {status['local_tasks']}")
    
    # Roman Urdu: Check file location
    done_path = orchestrator.done / email_filename
    if done_path.exists():
        print(f"  [OK] Task completed: {email_filename} -> Done/")
    else:
        print(f"  Task still in progress: {email_filename}")
    
    # Roman Urdu: Show coordination log
    print("\n[STEP 6] Coordination Log Summary:")
    for entry in orchestrator.coordination_log[-10:]:
        print(f"  [{entry['timestamp']}] {entry['type']}: {entry['details'][:60]}...")
    
    # Roman Urdu: Cleanup
    orchestrator.stop()
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETE!")
    print("=" * 70)
    print("\nWorkflow Summary:")
    print("1. [OK] Email arrived (Local offline)")
    print("2. [OK] Cloud drafted reply")
    print("3. [OK] Cloud moved to Pending_Approval")
    print("4. [OK] Local came online")
    print("5. [OK] Local approved and sent")
    print("6. [OK] Task moved to Done/")
    print("\nCheck the following files:")
    print(f"  - Coordination Log: {VAULT_PATH}/{COORDINATION_LOG}")
    print(f"  - Completed Task: {VAULT_PATH}/Done/{email_filename}")


def main():
    """
    Main function
    Roman Urdu: Main function
    """
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        # Roman Urdu: Normal mode
        print("=" * 70)
        print("ORCHESTRATOR - Platinum Tier")
        print("=" * 70)
        
        orchestrator = Orchestrator()
        
        print("\nStarting Orchestrator...")
        print("Press Ctrl+C to stop")
        
        orchestrator.start()
        
        try:
            while True:
                time.sleep(1)
                status = orchestrator.get_status()
                print(f"\rStatus: Cloud={'ON' if status['cloud_online'] else 'OFF'} | "
                      f"Local={'ON' if status['local_online'] else 'OFF'} | "
                      f"Cloud Tasks: {status['cloud_tasks']} | "
                      f"Local Tasks: {status['local_tasks']}", end="")
        except KeyboardInterrupt:
            print("\n\nStopping Orchestrator...")
            orchestrator.stop()
            print("Orchestrator stopped.")


if __name__ == "__main__":
    main()
