import asana
from datetime import datetime, timedelta
import time

# Replace these placeholders with actual values
ASANA_ACCESS_TOKEN = "YOUR_PERSONAL_ACCESS_TOKEN"
PROJECT_ID = "YOUR_PROJECT_ID"
IN_PROGRESS_SECTION_ID = "YOUR_IN_PROGRESS_SECTION_ID"

# Initialize Asana client
client = asana.Client.access_token(ASANA_ACCESS_TOKEN)

# Function to assign due dates based on priority
def assign_due_date(task):
    priority = task.get("priority")
    due_date = None
    
    if priority == "Low":
        due_date = datetime.now() + timedelta(days=14)
    elif priority == "Mid":
        due_date = datetime.now() + timedelta(days=7)
    elif priority == "High":
        due_date = datetime.now() + timedelta(days=2)

    if due_date:
        # Update the task's due date in Asana
        client.tasks.update_task(task["gid"], {"due_on": due_date.strftime("%Y-%m-%d")})
        print(f"Assigned due date for task '{task['name']}': {due_date.strftime('%Y-%m-%d')}")

# Function to adjust deadlines dynamically in a section
def adjust_due_dates_for_section(high_priority_task):
    # Fetch all tasks in the "In Progress" section
    tasks_in_section = client.tasks.get_tasks_for_section(
        IN_PROGRESS_SECTION_ID, opt_fields="gid,name,due_on"
    )

    for task in tasks_in_section:
        if task["gid"] != high_priority_task["gid"]:  # Skip the high-priority task itself
            current_due_date = task.get("due_on")
            if current_due_date:
                current_due_date = datetime.strptime(current_due_date, "%Y-%m-%d")
                new_due_date = current_due_date + timedelta(days=2)
                # Update the new due date
                client.tasks.update_task(
                    task["gid"], {"due_on": new_due_date.strftime("%Y-%m-%d")}
                )
                print(f"Extended due date for task '{task['name']}' to {new_due_date.strftime('%Y-%m-%d')}")

# Main function to monitor and handle dynamic deadlines
def monitor_and_update_deadlines():
    while True:  # Continuously monitor for changes (optional)
        tasks = client.tasks.get_tasks_for_project(
            PROJECT_ID, opt_fields="gid,name,priority,assignee_section,due_on"
        )
        
        for task in tasks:
            # Assign due dates if not already set
            if not task.get("due_on"):
                assign_due_date(task)

            # Check if a High Priority task is moved to the "Dynamic Section"
            section_id = task.get("assignee_section", {}).get("gid")
            if task.get("priority") == "High" and section_id == IN_PROGRESS_SECTION_ID:
                print(f"High Priority Task '{task['name']}' detected in 'In Progress' section.")
                adjust_due_dates_for_section(task)

        # Wait before polling again
        time.sleep(60)  # Poll every 60 seconds

if __name__ == "__main__":
    try:
        monitor_and_update_deadlines()
    except KeyboardInterrupt:
        print("Script stopped by user.")
