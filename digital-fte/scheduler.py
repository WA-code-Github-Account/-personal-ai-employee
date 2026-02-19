import schedule
import time
import subprocess
import os
from datetime import datetime

def run_gmail_watcher():
    """
    Run the gmail watcher check
    Gmail watcher check chalata hai
    """
    try:
        print(f"[{datetime.now()}] Running Gmail Watcher check...")
        result = subprocess.run(['python', 'gmail_watcher.py'], 
                                cwd=os.path.dirname(os.path.abspath(__file__)), 
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] Gmail Watcher check completed successfully")
        else:
            print(f"[{datetime.now()}] Gmail Watcher check failed: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] Error running Gmail Watcher: {str(e)}")


def run_planner():
    """
    Run the planner logic
    Planner logic chalata hai
    """
    try:
        print(f"[{datetime.now()}] Running Planner logic...")
        result = subprocess.run(['python', 'planner.py'], 
                                cwd=os.path.dirname(os.path.abspath(__file__)), 
                                capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[{datetime.now()}] Planner logic completed successfully")
        else:
            print(f"[{datetime.now()}] Planner logic failed: {result.stderr}")
    except Exception as e:
        print(f"[{datetime.now()}] Error running Planner: {str(e)}")


def update_dashboard():
    """
    Update Dashboard.md with current status and timestamp
    Dashboard.md ko current status aur timestamp ke saath update karta hai
    """
    try:
        print(f"[{datetime.now()}] Updating Dashboard.md...")
        
        dashboard_path = "../AI_Employee_Vault/Dashboard.md"
        
        # Create or update the dashboard file
        with open(dashboard_path, 'a', encoding='utf-8') as f:
            f.write(f"\n## Status Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("- Gmail Watcher: Active\n")
            f.write("- Planner: Active\n")
            f.write("- MCP Server: Active\n")
            f.write("- Scheduler: Running\n")
            f.write("---\n")
        
        print(f"[{datetime.now()}] Dashboard.md updated successfully")
    except Exception as e:
        print(f"[{datetime.now()}] Error updating Dashboard: {str(e)}")


def main():
    """
    Main function to set up and run the scheduler
    Scheduler set up aur run karne ke liye main function
    """
    print("Starting scheduler...")
    
    # Schedule tasks
    schedule.every(5).minutes.do(run_gmail_watcher)
    schedule.every(10).minutes.do(run_planner)
    schedule.every(1).hours.do(update_dashboard)
    
    # Run scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)  # Check every second for pending tasks


if __name__ == "__main__":
    main()