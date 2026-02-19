import os
import shutil
from datetime import datetime

# Roman Urdu: Audit logger ko import karna
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audit_logger import log_file_operation, log_error


def log_message(operation):
    """Helper function to log messages with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {operation}")


def read_file(path):
    """
    Reads and returns the content of a file.

    Args:
        path (str): Path to the file to read

    Returns:
        str: Content of the file or None if error occurs
    """
    try:
        # Roman Urdu: Audit log for file read operation
        log_file_operation("READ", path, source="vault_skill")
        
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            log_message(f"Successfully read file: {path}")
            # Roman Urdu: Audit log for successful read
            log_file_operation("READ", path, result="SUCCESS", 
                              file_size=len(content), source="vault_skill")
            return content
    except FileNotFoundError:
        log_message(f"Error: File not found - {path}")
        log_error("FILE_NOT_FOUND", f"File not found: {path}", action="read_file")
        return None
    except PermissionError:
        log_message(f"Error: Permission denied to read file - {path}")
        log_error("PERMISSION_DENIED", f"Permission denied: {path}", action="read_file")
        return None
    except Exception as e:
        log_message(f"Error reading file {path}: {str(e)}")
        log_error("FILE_READ_ERROR", str(e), file_involved=path, action="read_file")
        return None


def write_file(path, content):
    """
    Writes content to a file.

    Args:
        path (str): Path to the file to write
        content (str): Content to write to the file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Roman Urdu: Audit log for file write operation
        log_file_operation("WRITE", path, file_size=len(content), source="vault_skill")
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)
            log_message(f"Successfully wrote to file: {path}")
            # Roman Urdu: Audit log for successful write
            log_file_operation("WRITE", path, result="SUCCESS", 
                              file_size=len(content), source="vault_skill")
            return True
    except PermissionError:
        log_message(f"Error: Permission denied to write to file - {path}")
        log_error("PERMISSION_DENIED", f"Permission denied: {path}", action="write_file")
        return False
    except Exception as e:
        log_message(f"Error writing to file {path}: {str(e)}")
        log_error("FILE_WRITE_ERROR", str(e), file_involved=path, action="write_file")
        return False


def move_file(source_path, dest_path):
    """
    Moves a file from source to destination.

    Args:
        source_path (str): Path to the source file
        dest_path (str): Path to the destination

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Roman Urdu: Audit log for file move operation
        log_file_operation("MOVE", source_path, destination=dest_path, source="vault_skill")
        
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_path)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)

        shutil.move(source_path, dest_path)
        log_message(f"Successfully moved file from {source_path} to {dest_path}")
        # Roman Urdu: Audit log for successful move
        log_file_operation("MOVE", source_path, result="SUCCESS", 
                          destination=dest_path, source="vault_skill")
        return True
    except FileNotFoundError:
        log_message(f"Error: Source file not found - {source_path}")
        log_error("FILE_NOT_FOUND", f"Source file not found: {source_path}", action="move_file")
        return False
    except PermissionError:
        log_message(f"Error: Permission denied to move file - {source_path} to {dest_path}")
        log_error("PERMISSION_DENIED", f"Permission denied: {source_path}", action="move_file")
        return False
    except Exception as e:
        log_message(f"Error moving file from {source_path} to {dest_path}: {str(e)}")
        log_error("FILE_MOVE_ERROR", str(e), file_involved=source_path, action="move_file")
        return False


def list_folder(folder_path):
    """
    Lists all files in a folder.
    
    Args:
        folder_path (str): Path to the folder to list
        
    Returns:
        list: List of filenames in the folder or empty list if error occurs
    """
    try:
        if not os.path.isdir(folder_path):
            log_message(f"Error: Path is not a directory - {folder_path}")
            return []
        
        files = os.listdir(folder_path)
        log_message(f"Successfully listed folder: {folder_path} ({len(files)} items)")
        return files
    except PermissionError:
        log_message(f"Error: Permission denied to access folder - {folder_path}")
        return []
    except Exception as e:
        log_message(f"Error listing folder {folder_path}: {str(e)}")
        return []