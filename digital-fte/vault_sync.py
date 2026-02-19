#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vault Sync - Git Synchronization for AI Employee Vault
Syncs vault between Cloud and Local agents using Git
"""

import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Roman Urdu: Configuration aur global variables
VAULT_PATH = "D:/AI_Workspace/AI_Employee_Vault"
GITIGNORE_ITEMS = [
    ".env",
    "credentials.json",
    "token.pickle",
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    ".obsidian/",
    "*.log",
    "agent.log",
    "*.bak"
]
AGENT_NAME = "Vault-Sync"
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


class VaultSync:
    """
    Git-based synchronization for AI Employee Vault
    Roman Urdu: Git-based vault synchronization system
    """

    def __init__(self, vault_path=None):
        """
        Initialize Vault Sync
        Roman Urdu: Vault Sync ko initialize karna
        
        Args:
            vault_path (str): Path to vault directory
        """
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.git_dir = self.vault_path / ".git"
        
        # Roman Urdu: Ensure vault exists
        if not self.vault_path.exists():
            logger.error(f"Vault path does not exist: {self.vault_path}")
            raise FileNotFoundError(f"Vault not found: {self.vault_path}")
        
        logger.info(f"Vault Sync initialized. Path: {self.vault_path}")

    def is_git_initialized(self):
        """
        Check if git repository is initialized in vault
        Roman Urdu: Check karna ke git repo initialized hai ya nahi
        
        Returns:
            bool: True if git repo exists, False otherwise
        """
        return self.git_dir.exists()

    def initialize_git_repo(self):
        """
        Initialize git repository in vault if not exists
        Roman Urdu: Vault mein git repository initialize karna
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.is_git_initialized():
            logger.info("Git repository already initialized")
            return True
        
        try:
            # Roman Urdu: Git init command
            result = self._run_git_command("init")
            if result:
                logger.info("Git repository initialized successfully")
                
                # Roman Urdu: Initial config setup
                self._run_git_command("config", "user.name", "AI Employee Vault")
                self._run_git_command("config", "user.email", "vault@aiemployee.local")
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error initializing git repo: {str(e)}")
            return False

    def create_gitignore(self):
        """
        Create .gitignore file with standard exclusions
        Roman Urdu: .gitignore file banana with standard exclusions
        
        Returns:
            bool: True if successful, False otherwise
        """
        gitignore_path = self.vault_path / ".gitignore"
        
        try:
            # Roman Urdu: .gitignore content
            content = """# AI Employee Vault - Git Ignore File
# Roman Urdu: Ye files git mein track nahi hongi

# Environment and credentials
.env
credentials.json
token.pickle
*.key
*.secret

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Logs
*.log
agent.log
logs/

# Obsidian
.obsidian/

# Backup files
*.bak
*.backup
*.old

# OS files
.DS_Store
Thumbs.db
desktop.ini

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
tmp/
temp/
*.tmp
"""
            
            with open(gitignore_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f".gitignore created at: {gitignore_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating .gitignore: {str(e)}")
            return False

    def _run_git_command(self, *args):
        """
        Run git command in vault directory
        Roman Urdu: Vault directory mein git command chalana
        
        Args:
            *args: Git command arguments
            
        Returns:
            str: Command output, or None if failed
        """
        try:
            # Roman Urdu: Git command execute karna
            cmd = ["git"] + list(args)
            result = subprocess.run(
                cmd,
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.debug(f"Git command successful: {' '.join(cmd)}")
                return result.stdout.strip()
            else:
                logger.warning(f"Git command failed: {' '.join(cmd)} - {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            logger.error(f"Git command timed out: {' '.join(cmd)}")
            return None
        except Exception as e:
            logger.error(f"Error running git command: {str(e)}")
            return None

    def get_status(self):
        """
        Get git status of vault
        Roman Urdu: Vault ka git status lena
        
        Returns:
            str: Git status output
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot get status")
            return None
        
        return self._run_git_command("status", "--short")

    def add_all(self):
        """
        Add all changes to git staging
        Roman Urdu: Saare changes ko git staging mein add karna
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot add files")
            return False
        
        result = self._run_git_command("add", "-A")
        if result is not None:
            logger.info("All changes added to staging")
            return True
        return False

    def commit(self, message=None):
        """
        Commit staged changes with timestamp message
        Roman Urdu: Staged changes ko timestamp ke saath commit karna
        
        Args:
            message (str): Optional commit message prefix
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot commit")
            return False
        
        # Roman Urdu: Timestamp ke saath commit message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if message:
            commit_msg = f"{message} - {timestamp}"
        else:
            commit_msg = f"Auto-sync: Vault update - {timestamp}"
        
        result = self._run_git_command("commit", "-m", commit_msg)
        
        if result is not None:
            logger.info(f"Committed: {commit_msg}")
            return True
        else:
            # Roman Urdu: Agar commit fail ho (no changes), to bhi True return karna
            if "nothing to commit" in str(result):
                logger.info("No changes to commit")
                return True
            return False

    def push(self, remote="origin", branch="main"):
        """
        Push commits to remote repository
        Roman Urdu: Remote repository ko commits push karna
        
        Args:
            remote (str): Remote name (default: origin)
            branch (str): Branch name (default: main)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot push")
            return False
        
        # Roman Urdu: Pehle branch check/create karna
        current_branch = self._get_current_branch()
        
        if current_branch != branch:
            # Roman Urdu: Branch switch ya create karna
            self._run_git_command("checkout", "-b", branch)
        
        # Roman Urdu: Remote check karna
        remotes = self._run_git_command("remote", "-v")
        if not remotes:
            logger.warning(f"No remote '{remote}' configured. Add remote first.")
            return False
        
        # Roman Urdu: Push command
        result = self._run_git_command("push", "-u", remote, branch)
        
        if result is not None:
            logger.info(f"Pushed to {remote}/{branch}")
            return True
        else:
            logger.warning("Push failed or no changes to push")
            return True  # Roman Urdu: No changes ko error nahi maanna

    def pull(self, remote="origin", branch="main"):
        """
        Pull changes from remote repository
        Roman Urdu: Remote repository se changes pull karna
        
        Args:
            remote (str): Remote name (default: origin)
            branch (str): Branch name (default: main)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot pull")
            return False
        
        # Roman Urdu: Pehle branch check karna
        current_branch = self._get_current_branch()
        
        if current_branch != branch:
            # Roman Urdu: Branch switch karna
            self._run_git_command("checkout", branch)
        
        # Roman Urdu: Pull command
        result = self._run_git_command("pull", remote, branch)
        
        if result is not None:
            logger.info(f"Pulled from {remote}/{branch}")
            return True
        else:
            logger.warning("Pull failed")
            return False

    def _get_current_branch(self):
        """
        Get current git branch name
        Roman Urdu: Current git branch ka naam lena
        
        Returns:
            str: Current branch name
        """
        result = self._run_git_command("branch", "--show-current")
        return result if result else "main"

    def add_remote(self, remote_url, remote_name="origin"):
        """
        Add remote repository URL
        Roman Urdu: Remote repository URL add karna
        
        Args:
            remote_url (str): Remote repository URL
            remote_name (str): Remote name (default: origin)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot add remote")
            return False
        
        # Roman Urdu: Pehle existing remote check karna
        existing = self._run_git_command("remote", "get-url", remote_name)
        
        if existing:
            logger.info(f"Remote '{remote_name}' already exists: {existing}")
            # Roman Urdu: Update existing remote
            result = self._run_git_command("remote", "set-url", remote_name, remote_url)
        else:
            # Roman Urdu: Naya remote add karna
            result = self._run_git_command("remote", "add", remote_name, remote_url)
        
        if result is not None:
            logger.info(f"Remote '{remote_name}' configured: {remote_url}")
            return True
        return False

    def sync_full(self, commit_message=None, do_push=True, do_pull=True):
        """
        Full sync: add -> commit -> pull -> push
        Roman Urdu: Complete sync process
        
        Args:
            commit_message (str): Optional commit message
            do_push (bool): Whether to push (default: True)
            do_pull (bool): Whether to pull (default: True)
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting full vault sync...")
        
        # Roman Urdu: Step 1: Initialize if needed
        if not self.is_git_initialized():
            logger.info("Initializing git repository...")
            if not self.initialize_git_repo():
                return False
            if not self.create_gitignore():
                return False
        
        # Roman Urdu: Step 2: Add all changes
        logger.info("Adding changes...")
        self.add_all()
        
        # Roman Urdu: Step 3: Commit
        logger.info("Committing changes...")
        if not self.commit(commit_message):
            logger.warning("Commit had no changes or failed")
        
        # Roman Urdu: Step 4: Pull first (to avoid conflicts)
        if do_pull:
            logger.info("Pulling remote changes...")
            self.pull()
        
        # Roman Urdu: Step 5: Push
        if do_push:
            logger.info("Pushing changes...")
            if not self.push():
                logger.warning("Push failed or no changes to push")
        
        logger.info("Full vault sync complete")
        return True

    def get_log(self, limit=10):
        """
        Get git commit log
        Roman Urdu: Git commit log lena
        
        Args:
            limit (int): Number of commits to retrieve
            
        Returns:
            list: List of commit messages
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot get log")
            return []
        
        result = self._run_git_command("log", f"-{limit}", "--oneline")
        
        if result:
            commits = result.split("\n")
            logger.info(f"Retrieved {len(commits)} commits")
            return commits
        return []

    def get_diff(self):
        """
        Get diff of unstaged changes
        Roman Urdu: Unstaged changes ka diff lena
        
        Returns:
            str: Diff output
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot get diff")
            return None
        
        return self._run_git_command("diff")

    def create_branch(self, branch_name):
        """
        Create a new branch
        Roman Urdu: Naya branch create karna
        
        Args:
            branch_name (str): Name of new branch
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot create branch")
            return False
        
        result = self._run_git_command("checkout", "-b", branch_name)
        
        if result is not None:
            logger.info(f"Created and switched to branch: {branch_name}")
            return True
        return False

    def switch_branch(self, branch_name):
        """
        Switch to existing branch
        Roman Urdu: Existing branch mein switch karna
        
        Args:
            branch_name (str): Name of branch to switch to
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_git_initialized():
            logger.warning("Git not initialized, cannot switch branch")
            return False
        
        result = self._run_git_command("checkout", branch_name)
        
        if result is not None:
            logger.info(f"Switched to branch: {branch_name}")
            return True
        return False


class CloudLocalSync:
    """
    Specialized sync for Cloud and Local agent coordination
    Roman Urdu: Cloud aur Local agents ke coordination ke liye sync
    """

    def __init__(self, vault_path=None):
        """
        Initialize Cloud-Local Sync
        Roman Urdu: Cloud-Local Sync ko initialize karna
        
        Args:
            vault_path (str): Path to vault directory
        """
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.vault_sync = VaultSync(vault_path)
        
        self.cloud_domain = self.vault_path / "Needs_Action" / "cloud"
        self.local_domain = self.vault_path / "Needs_Action" / "local"
        
        logger.info("Cloud-Local Sync initialized")

    def sync_cloud_to_local(self, filename):
        """
        Sync a file from cloud domain to local domain
        Roman Urdu: Cloud domain se local domain mein file sync karna
        
        Args:
            filename (str): Name of file to sync
            
        Returns:
            bool: True if successful, False otherwise
        """
        source = self.cloud_domain / filename
        dest = self.local_domain / filename
        
        if not source.exists():
            logger.error(f"Source file not found in cloud: {filename}")
            return False
        
        try:
            # Roman Urdu: File copy karna (not move, to preserve cloud copy)
            import shutil
            shutil.copy2(str(source), str(dest))
            
            # Roman Urdu: Sync metadata add karna
            from skills.vault_skill import read_file, write_file
            content = read_file(str(dest))
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sync_note = f"""
## Synced to Local
- **Synced at:** {timestamp}
- **From:** Cloud Domain
- **Sync by:** CloudLocalSync

"""
            content += sync_note
            write_file(str(dest), content)
            
            logger.info(f"Synced cloud->local: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error syncing file: {str(e)}")
            return False

    def sync_local_to_cloud(self, filename):
        """
        Sync a file from local domain to cloud domain
        Roman Urdu: Local domain se cloud domain mein file sync karna
        
        Args:
            filename (str): Name of file to sync
            
        Returns:
            bool: True if successful, False otherwise
        """
        source = self.local_domain / filename
        dest = self.cloud_domain / filename
        
        if not source.exists():
            logger.error(f"Source file not found in local: {filename}")
            return False
        
        try:
            # Roman Urdu: File copy karna
            import shutil
            shutil.copy2(str(source), str(dest))
            
            # Roman Urdu: Sync metadata add karna
            from skills.vault_skill import read_file, write_file
            content = read_file(str(dest))
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sync_note = f"""
## Synced to Cloud
- **Synced at:** {timestamp}
- **From:** Local Domain
- **Sync by:** CloudLocalSync

"""
            content += sync_note
            write_file(str(dest), content)
            
            logger.info(f"Synced local->cloud: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error syncing file: {str(e)}")
            return False

    def full_sync_with_git(self, commit_message=None):
        """
        Full sync with git commit
        Roman Urdu: Git commit ke saath full sync
        
        Args:
            commit_message (str): Optional commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting full sync with git...")
        
        # Roman Urdu: Vault sync
        if not self.vault_sync.sync_full(commit_message):
            return False
        
        logger.info("Full sync with git complete")
        return True


def main():
    """
    Main function to demonstrate Vault Sync capabilities
    Roman Urdu: Vault Sync capabilities ko demonstrate karna
    """
    print("=" * 60)
    print("Vault Sync - Git Synchronization")
    print("=" * 60)
    
    # Initialize sync
    sync = VaultSync()
    
    # Demo: Check git status
    print("\n[Demo] Checking Git Status:")
    if sync.is_git_initialized():
        print("  Git repository: Initialized ✓")
        status = sync.get_status()
        if status:
            print(f"  Status: {status if status else 'Clean'}")
    else:
        print("  Git repository: Not initialized")
        print("  Initializing...")
        sync.initialize_git_repo()
        sync.create_gitignore()
    
    # Demo: Get current branch
    print("\n[Demo] Current Branch:")
    branch = sync._get_current_branch()
    print(f"  Branch: {branch}")
    
    # Demo: Get commit log
    print("\n[Demo] Recent Commits:")
    commits = sync.get_log(limit=5)
    for commit in commits:
        print(f"  {commit}")
    
    # Demo: Full sync
    print("\n[Demo] Running Full Sync:")
    success = sync.sync_full(commit_message="Demo sync")
    print(f"  Sync result: {'Success ✓' if success else 'Failed ✗'}")
    
    print("\n" + "=" * 60)
    print("Vault Sync demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
