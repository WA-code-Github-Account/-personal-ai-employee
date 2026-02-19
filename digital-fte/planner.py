import os
import glob
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('planner.log'),
        logging.StreamHandler()
    ]
)

def read_md_files(needs_action_dir):
    """
    Read all .md files from the Needs_Action directory
    Sab .md files ko Needs_Action directory se parhta hai
    """
    md_files = []
    pattern = os.path.join(needs_action_dir, "*.md")
    
    for file_path in glob.glob(pattern):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                md_files.append({
                    'filename': os.path.basename(file_path),
                    'filepath': file_path,
                    'content': content
                })
            logging.info(f"Successfully read file: {file_path}")
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {str(e)}")
    
    return md_files

def create_action_plan(filename, content):
    """
    Create a simple action plan based on filename and content
    Filename aur content ke hisaab se simple action plan banta hai
    """
    # Extract title from filename (without extension)
    title = os.path.splitext(filename)[0].replace('_', ' ').title()
    
    # Create a simple action plan
    plan = f"# Action Plan for: {title}\n\n"
    plan += "## Overview\n"
    plan += f"This plan addresses the requirements mentioned in '{filename}'.\n\n"
    
    plan += "## Key Points from Content\n"
    # Take first 500 characters of content as key points
    content_preview = content[:500] + "..." if len(content) > 500 else content
    plan += f"{content_preview}\n\n"
    
    plan += "## Action Items\n"
    plan += "1. Review the requirements in detail\n"
    plan += "2. Break down the task into smaller subtasks\n"
    plan += "3. Assign resources and timeline\n"
    plan += "4. Execute the plan\n"
    plan += "5. Monitor progress and adjust as needed\n\n"
    
    plan += "## Timeline\n"
    plan += "- Planning Phase: 1-2 days\n"
    plan += "- Execution Phase: Variable based on complexity\n"
    plan += "- Review Phase: 1 day\n\n"
    
    plan += "## Notes\n"
    plan += "Additional details may be required based on specific requirements.\n"
    
    return plan

def save_plan(plan_content, output_path):
    """
    Save the action plan to a Plan.md file
    Action plan ko Plan.md file mein save karta hai
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(plan_content)
        logging.info(f"Plan saved to: {output_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving plan to {output_path}: {str(e)}")
        return False

def main():
    """
    Main function to orchestrate the planning process
    Planning process ko coordinate karta hai
    """
    # Define paths
    needs_action_dir = "../AI_Employee_Vault/Needs_Action"
    output_dir = "../AI_Employee_Vault"
    output_file = os.path.join(output_dir, "Plan.md")
    
    # Check if Needs_Action directory exists
    if not os.path.isdir(needs_action_dir):
        logging.error(f"Directory does not exist: {needs_action_dir}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logging.info("Starting the planning process...")
    
    # Read all .md files from Needs_Action directory
    md_files = read_md_files(needs_action_dir)
    
    if not md_files:
        logging.info("No .md files found in Needs_Action directory")
        return
    
    logging.info(f"Found {len(md_files)} .md files to process")
    
    # Combine all content for a comprehensive plan
    combined_plan = "# Comprehensive Action Plan\n\n"
    combined_plan += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for file_info in md_files:
        filename = file_info['filename']
        content = file_info['content']
        
        logging.info(f"Processing file: {filename}")
        
        # Create action plan for this file
        plan_section = create_action_plan(filename, content)
        
        # Append to combined plan
        combined_plan += f"\n---\n\n{plan_section}\n"
    
    # Save the combined plan
    success = save_plan(combined_plan, output_file)
    
    if success:
        logging.info(f"Comprehensive action plan created: {output_file}")
        
        # Also create individual plans for each file
        for file_info in md_files:
            filename = file_info['filename']
            content = file_info['content']
            
            individual_plan = create_action_plan(filename, content)
            individual_filename = f"Plan_for_{os.path.splitext(filename)[0]}.md"
            individual_output_path = os.path.join(output_dir, individual_filename)
            
            save_plan(individual_plan, individual_output_path)
            logging.info(f"Individual plan created: {individual_filename}")
    else:
        logging.error("Failed to create the comprehensive action plan")

if __name__ == "__main__":
    main()