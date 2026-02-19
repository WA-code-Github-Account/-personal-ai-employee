import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil


class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder, needs_action_folder):
        self.inbox_folder = inbox_folder
        self.needs_action_folder = needs_action_folder

    def on_created(self, event):
        if not event.is_directory:
            # Check if the file is .md or .txt
            if event.src_path.endswith(('.md', '.txt')):
                # Move the file to Needs_Action folder
                filename = os.path.basename(event.src_path)
                destination = os.path.join(self.needs_action_folder, filename)
                
                # Wait a moment to ensure file is completely written
                time.sleep(0.5)
                
                shutil.move(event.src_path, destination)
                print(f"File {filename} moved from Inbox to Needs_Action")


def main():
    inbox_folder = "D:/AI_Workspace/AI_Employee_Vault/Inbox"
    needs_action_folder = "D:/AI_Workspace/AI_Employee_Vault/Needs_Action"

    # Ensure paths exist using os.path.abspath
    inbox_folder = os.path.abspath(inbox_folder)
    needs_action_folder = os.path.abspath(needs_action_folder)

    # Create directories if they don't exist
    os.makedirs(inbox_folder, exist_ok=True)
    os.makedirs(needs_action_folder, exist_ok=True)

    # Create the event handler
    event_handler = InboxHandler(inbox_folder, needs_action_folder)

    # Create the observer
    observer = Observer()
    observer.schedule(event_handler, inbox_folder, recursive=False)

    # Start the observer
    observer.start()
    print("Watcher started. Monitoring Inbox folder for new .md and .txt files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped.")

    observer.join()


if __name__ == "__main__":
    main()