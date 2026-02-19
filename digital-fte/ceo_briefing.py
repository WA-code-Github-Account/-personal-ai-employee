#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CEO Briefing Generator - Weekly Executive Report
Yeh har haftay ki CEO briefing report generate karta hai
"""

import os
import glob
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# Roman Urdu: Dependencies ko import kia gaya hai
from skills.vault_skill import read_file, write_file, list_folder
from audit_logger import log_task_start, log_task_complete, log_file_operation, log_error

# Roman Urdu: Configuration aur global variables
VAULT_BASE = "D:/AI_Workspace_bronze_silver_gold/AI_Employee_Vault"
DONE_DIR = os.path.join(VAULT_BASE, "Done")
INBOX_DIR = os.path.join(VAULT_BASE, "Inbox")
NEEDS_ACTION_DIR = os.path.join(VAULT_BASE, "Needs_Action")
IN_PROGRESS_DIR = os.path.join(VAULT_BASE, "In_Progress")
PENDING_APPROVAL_DIR = os.path.join(VAULT_BASE, "Pending_Approval")


class CEOBriefingGenerator:
    """
    Weekly CEO Briefing Report Generator
    Haftawar CEO briefing report banane wala generator
    """

    def __init__(self):
        """Initialize the CEO Briefing Generator"""
        # Roman Urdu: Configuration initialize karna
        self.vault_base = Path(VAULT_BASE)
        self.done_dir = Path(DONE_DIR)
        self.inbox_dir = Path(INBOX_DIR)
        self.needs_action_dir = Path(NEEDS_ACTION_DIR)
        self.in_progress_dir = Path(IN_PROGRESS_DIR)
        self.pending_approval_dir = Path(PENDING_APPROVAL_DIR)
        
        # Roman Urdu: Date calculations
        self.today = datetime.now()
        self.week_start = self.today - timedelta(days=self.today.weekday())
        self.week_end = self.week_start + timedelta(days=6)
        
        # Roman Urdu: Report data storage
        self.report_data = {
            "generated_at": self.today.strftime("%Y-%m-%d %H:%M:%S"),
            "week_range": f"{self.week_start.strftime('%Y-%m-%d')} to {self.week_end.strftime('%Y-%m-%d')}",
            "done_count": 0,
            "done_files": [],
            "inbox_count": 0,
            "inbox_files": [],
            "needs_action_count": 0,
            "in_progress_count": 0,
            "pending_approval_count": 0,
            "plan_files": [],
            "completed_tasks": [],
            "emails_processed": 0
        }
        
        print(f"CEO Briefing Generator initialized")
        print(f"Week Range: {self.report_data['week_range']}")

    def count_done_files(self) -> int:
        """
        Count all files in Done folder
        Done folder mein saari files ginna
        """
        try:
            if not self.done_dir.exists():
                print(f"Done directory does not exist: {self.done_dir}")
                return 0
            
            # Roman Urdu: Sirf .md aur .txt files ko count karo
            done_files = []
            for ext in ['*.md', '*.txt']:
                for file_path in self.done_dir.glob(ext):
                    if file_path.name != '.gitkeep':
                        done_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        })
            
            self.report_data["done_count"] = len(done_files)
            self.report_data["done_files"] = done_files
            print(f"Done files counted: {len(done_files)}")
            return len(done_files)
        except Exception as e:
            print(f"Error counting done files: {str(e)}")
            return 0

    def count_inbox_files(self) -> int:
        """
        Count all files in Inbox folder (emails)
        Inbox folder mein saari files ginna (emails)
        """
        try:
            if not self.inbox_dir.exists():
                print(f"Inbox directory does not exist: {self.inbox_dir}")
                return 0
            
            # Roman Urdu: Inbox files ko count karo
            inbox_files = []
            for ext in ['*.md', '*.txt', '*.eml']:
                for file_path in self.inbox_dir.glob(ext):
                    if file_path.name != '.gitkeep':
                        inbox_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        })
            
            self.report_data["inbox_count"] = len(inbox_files)
            self.report_data["inbox_files"] = inbox_files
            
            # Roman Urdu: Email files ko specifically count karo
            email_files = [f for f in inbox_files if 'email' in f['name'].lower()]
            self.report_data["emails_processed"] = len(email_files)
            
            print(f"Inbox files counted: {len(inbox_files)} (Emails: {len(email_files)})")
            return len(inbox_files)
        except Exception as e:
            print(f"Error counting inbox files: {str(e)}")
            return 0

    def scan_plan_files_last_7_days(self) -> List[Dict]:
        """
        Scan Plan.md files from last 7 days
        Pichle 7 din ke Plan.md files ko scan karna
        """
        try:
            plan_files = []
            seven_days_ago = self.today - timedelta(days=7)
            
            # Roman Urdu: Vault base mein Plan.md files dhoondho
            for file_path in self.vault_base.glob("Plan*.md"):
                try:
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if modified_time >= seven_days_ago:
                        content = read_file(str(file_path))
                        plan_files.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "modified": modified_time.strftime("%Y-%m-%d %H:%M"),
                            "content_preview": content[:200] + "..." if content and len(content) > 200 else content
                        })
                except Exception as e:
                    print(f"Error reading plan file {file_path.name}: {str(e)}")
            
            self.report_data["plan_files"] = plan_files
            print(f"Plan files (last 7 days): {len(plan_files)}")
            return plan_files
        except Exception as e:
            print(f"Error scanning plan files: {str(e)}")
            return []

    def count_folder_status(self) -> Dict[str, int]:
        """
        Count files in all status folders
        Saare status folders mein files ginna
        """
        try:
            status_counts = {
                "needs_action": 0,
                "in_progress": 0,
                "pending_approval": 0
            }
            
            # Roman Urdu: Needs_Action count
            if self.needs_action_dir.exists():
                files = [f for f in self.needs_action_dir.glob("*.md") if f.name != '.gitkeep']
                status_counts["needs_action"] = len(files)
            
            # Roman Urdu: In_Progress count
            if self.in_progress_dir.exists():
                files = [f for f in self.in_progress_dir.glob("*.md") if f.name != '.gitkeep']
                status_counts["in_progress"] = len(files)
            
            # Roman Urdu: Pending_Approval count
            if self.pending_approval_dir.exists():
                files = [f for f in self.pending_approval_dir.glob("*.md") if f.name != '.gitkeep']
                status_counts["pending_approval"] = len(files)
            
            self.report_data["needs_action_count"] = status_counts["needs_action"]
            self.report_data["in_progress_count"] = status_counts["in_progress"]
            self.report_data["pending_approval_count"] = status_counts["pending_approval"]
            
            print(f"Status counts: {status_counts}")
            return status_counts
        except Exception as e:
            print(f"Error counting folder status: {str(e)}")
            return {}

    def summarize_completed_tasks(self) -> List[Dict]:
        """
        Summarize completed tasks from Done folder
        Done folder se completed tasks ka summary banana
        """
        try:
            completed_tasks = []
            
            # Roman Urdu: Report files ko read karo
            for report_file in self.done_dir.glob("Report_*.md"):
                try:
                    content = read_file(str(report_file))
                    if content:
                        # Extract task name from filename
                        task_name = report_file.name.replace("Report_", "").replace(".md", "").replace("_", " ").title()
                        
                        # Extract status from content
                        status = "Completed"
                        if "Status:" in content:
                            for line in content.split('\n'):
                                if 'Status:' in line:
                                    status = line.split('Status:')[1].strip()
                                    break
                        
                        completed_tasks.append({
                            "name": task_name,
                            "file": report_file.name,
                            "status": status,
                            "completed_at": datetime.fromtimestamp(report_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                        })
                except Exception as e:
                    print(f"Error reading report {report_file.name}: {str(e)}")
            
            self.report_data["completed_tasks"] = completed_tasks
            print(f"Completed tasks summarized: {len(completed_tasks)}")
            return completed_tasks
        except Exception as e:
            print(f"Error summarizing completed tasks: {str(e)}")
            return []

    def generate_briefing_report(self) -> str:
        """
        Generate the complete CEO briefing report
        Complete CEO briefing report generate karna
        """
        # Roman Urdu: Report header
        report = f"# CEO Weekly Briefing Report\n\n"
        report += f"## Executive Summary\n\n"
        report += f"**Report Generated:** {self.report_data['generated_at']}\n\n"
        report += f"**Week Range:** {self.report_data['week_range']}\n\n"
        report += "---\n\n"
        
        # Roman Urdu: Weekly Summary section
        report += f"## Weekly Summary\n\n"
        report += f"### Key Metrics\n\n"
        report += f"| Metric | Count |\n"
        report += f"|--------|-------|\n"
        report += f"| Tasks Completed | {self.report_data['done_count']} |\n"
        report += f"| Tasks In Progress | {self.report_data['in_progress_count']} |\n"
        report += f"| Tasks Pending Action | {self.report_data['needs_action_count']} |\n"
        report += f"| Pending Approvals | {self.report_data['pending_approval_count']} |\n"
        report += f"| Emails Processed | {self.report_data['emails_processed']} |\n\n"
        
        # Roman Urdu: Performance indicator
        total_active = self.report_data['in_progress_count'] + self.report_data['needs_action_count']
        completion_rate = 0
        if total_active + self.report_data['done_count'] > 0:
            completion_rate = (self.report_data['done_count'] / (total_active + self.report_data['done_count'])) * 100
        
        report += f"### Performance Indicator\n\n"
        report += f"- **Completion Rate:** {completion_rate:.1f}%\n"
        report += f"- **Active Tasks:** {total_active}\n"
        report += f"- **Pending Approvals:** {self.report_data['pending_approval_count']}\n\n"
        
        # Roman Urdu: Tasks Completed section
        report += f"## Tasks Completed\n\n"
        if self.report_data['completed_tasks']:
            report += f"| Task Name | Status | Completed At |\n"
            report += f"|-----------|--------|--------------|\n"
            for task in self.report_data['completed_tasks'][:10]:  # Show top 10
                report += f"| {task['name']} | {task['status']} | {task['completed_at']} |\n"
            
            if len(self.report_data['completed_tasks']) > 10:
                report += f"\n*... and {len(self.report_data['completed_tasks']) - 10} more tasks*\n"
        else:
            report += f"*No tasks completed this week.*\n\n"
        
        report += f"\n### All Done Files\n\n"
        if self.report_data['done_files']:
            for file_info in self.report_data['done_files'][:15]:  # Show top 15
                report += f"- `{file_info['name']}` (Modified: {file_info['modified']})\n"
            if len(self.report_data['done_files']) > 15:
                report += f"\n*... and {len(self.report_data['done_files']) - 15} more files*\n"
        else:
            report += f"*No files in Done folder.*\n"
        
        report += f"\n---\n\n"
        
        # Roman Urdu: Emails Processed section
        report += f"## Emails Processed\n\n"
        report += f"**Total Emails:** {self.report_data['emails_processed']}\n\n"
        
        if self.report_data['inbox_files']:
            report += f"### Inbox Files\n\n"
            for file_info in self.report_data['inbox_files'][:10]:  # Show top 10
                report += f"- `{file_info['name']}` (Modified: {file_info['modified']})\n"
            if len(self.report_data['inbox_files']) > 10:
                report += f"\n*... and {len(self.report_data['inbox_files']) - 10} more files*\n"
        else:
            report += f"*No emails in inbox.*\n"
        
        report += f"\n---\n\n"
        
        # Roman Urdu: Plans Created section
        report += f"## Plans Created (Last 7 Days)\n\n"
        if self.report_data['plan_files']:
            for plan in self.report_data['plan_files']:
                report += f"### {plan['name']}\n"
                report += f"- **Modified:** {plan['modified']}\n"
                if plan['content_preview']:
                    report += f"- **Preview:** {plan['content_preview']}\n"
                report += f"\n"
        else:
            report += f"*No plans created in the last 7 days.*\n\n"
        
        report += f"\n---\n\n"
        
        # Roman Urdu: Next Week Goals section
        report += f"## Next Week Goals\n\n"
        report += f"### Priority Actions\n\n"
        
        # Roman Urdu: Dynamic goals based on current state
        goals = []
        
        if self.report_data['needs_action_count'] > 0:
            goals.append(f"1. **Process Pending Tasks:** Address {self.report_data['needs_action_count']} tasks in Needs Action queue")
        
        if self.report_data['pending_approval_count'] > 0:
            goals.append(f"2. **Clear Approvals:** Review and approve {self.report_data['pending_approval_count']} pending items")
        
        if self.report_data['in_progress_count'] > 0:
            goals.append(f"3. **Complete In-Progress Tasks:** Finalize {self.report_data['in_progress_count']} ongoing tasks")
        
        goals.append(f"4. **Maintain Momentum:** Target {max(5, self.report_data['done_count'])} task completions next week")
        goals.append(f"5. **Review & Optimize:** Analyze completed tasks for process improvements")
        
        for goal in goals:
            report += f"{goal}\n\n"
        
        # Roman Urdu: Recommendations
        report += f"### Recommendations\n\n"

        if completion_rate < 50:
            report += f"- [!] **Attention Needed:** Completion rate is below 50%. Consider resource allocation review.\n"
        elif completion_rate < 75:
            report += f"- [~] **On Track:** Completion rate is moderate. Focus on clearing pending items.\n"
        else:
            report += f"- [OK] **Excellent:** Strong completion rate. Maintain current workflow efficiency.\n"

        if self.report_data['pending_approval_count'] > 5:
            report += f"- [!] **Bottleneck Alert:** High number of pending approvals. Expedite review process.\n"
        
        report += f"\n---\n\n"
        
        # Roman Urdu: Footer
        report += f"## Report Details\n\n"
        report += f"- **Generated By:** CEO Briefing Generator (Gold Tier)\n"
        report += f"- **System:** Ralph Wiggum Autonomous Loop\n"
        report += f"- **Report File:** CEO_Briefing_{self.today.strftime('%Y-%m-%d')}.md\n\n"
        report += f"---\n\n"
        report += f"*This is an automated report generated by the AI Employee System.*\n"
        
        return report

    def save_report(self) -> str:
        """
        Save the briefing report to AI_Employee_Vault
        Briefing report ko AI_Employee_Vault mein save karna
        """
        try:
            # Roman Urdu: Report file ka naam aur path
            report_filename = f"CEO_Briefing_{self.today.strftime('%Y-%m-%d')}.md"
            report_path = os.path.join(VAULT_BASE, report_filename)
            
            # Roman Urdu: Report content generate karna
            report_content = self.generate_briefing_report()

            # Roman Urdu: Audit log for file write operation
            log_file_operation("WRITE", report_path, source="ceo_briefing")

            # Roman Urdu: File save karna
            success = write_file(report_path, report_content)

            if success:
                print(f"CEO Briefing Report saved: {report_filename}")
                print(f"Location: {report_path}")
                # Roman Urdu: Audit log for successful write
                log_file_operation("WRITE", report_path, result="SUCCESS", 
                                  file_size=len(report_content), source="ceo_briefing")
                return report_path
            else:
                log_error("REPORT_WRITE_FAILED", "write_file returned False", 
                         file_involved=report_path, action="save_report")
                print(f"Failed to save CEO Briefing Report")
                return None
        except Exception as e:
            log_error("REPORT_SAVE_ERROR", str(e), file_involved=report_path, 
                     action="save_report")
            print(f"Error saving report: {str(e)}")
            return None

    def run(self) -> bool:
        """
        Run the complete briefing generation process
        Complete briefing generation process ko run karna
        """
        # Roman Urdu: Audit log for task start
        log_task_start("CEO Briefing Generation", source="ceo_briefing")
        
        print("\n" + "=" * 60)
        print("CEO Briefing Generator - Starting")
        print("=" * 60)

        try:
            # Roman Urdu: Saare data collection steps
            print("\n[1/6] Counting Done files...")
            self.count_done_files()

            print("\n[2/6] Counting Inbox files...")
            self.count_inbox_files()

            print("\n[3/6] Scanning Plan files (last 7 days)...")
            self.scan_plan_files_last_7_days()

            print("\n[4/6] Counting folder status...")
            self.count_folder_status()

            print("\n[5/6] Summarizing completed tasks...")
            self.summarize_completed_tasks()

            print("\n[6/6] Generating and saving report...")
            report_path = self.save_report()

            # Roman Urdu: Summary print karna
            print("\n" + "=" * 60)
            print("CEO Briefing Generator - Complete")
            print("=" * 60)
            print(f"\nReport Summary:")
            print(f"  - Tasks Completed: {self.report_data['done_count']}")
            print(f"  - Emails Processed: {self.report_data['emails_processed']}")
            print(f"  - Plans (7 days): {len(self.report_data['plan_files'])}")
            print(f"  - In Progress: {self.report_data['in_progress_count']}")
            print(f"  - Needs Action: {self.report_data['needs_action_count']}")
            print(f"  - Pending Approval: {self.report_data['pending_approval_count']}")

            if report_path:
                print(f"\n[OK] Report saved to: {report_path}")
                # Roman Urdu: Audit log for task completion
                log_task_complete("CEO Briefing Generation", result="SUCCESS", 
                                 source="ceo_briefing")
                return True
            else:
                print(f"\n[FAIL] Failed to save report")
                # Roman Urdu: Audit log for task failure
                log_task_complete("CEO Briefing Generation", result="FAILED", 
                                 error="Report path is None", source="ceo_briefing")
                return False

        except Exception as e:
            log_error("BRIEFING_GENERATION_ERROR", str(e), action="run", source="ceo_briefing")
            print(f"\nError in CEO Briefing Generator: {str(e)}")
            return False


def main():
    """
    Main entry point for CEO Briefing Generator
    CEO Briefing Generator ka main entry point
    """
    print("=" * 60)
    print("CEO Briefing Generator - Gold Tier")
    print("Weekly Executive Report System")
    print("=" * 60)
    
    # Roman Urdu: CEO Briefing Generator ko initialize aur run karna
    generator = CEOBriefingGenerator()
    success = generator.run()
    
    if success:
        print("\n[OK] CEO Briefing generated successfully!")
    else:
        print("\n[FAIL] CEO Briefing generation failed!")
    
    return success


if __name__ == "__main__":
    main()
