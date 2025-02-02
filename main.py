import schedule
import time
from agents.management import Agent
import pandas as pd
import logging

# Set up logging
logging.basicConfig(
    filename="process_log.log",  # Log file name
    level=logging.INFO,  # Set logging level to INFO (you can change this to DEBUG for more details)
    format="%(asctime)s - %(message)s"  # Format the log to include timestamp
)

# Create a custom function to replace print with logging
def log_message(message):
    logging.info(message)

def process():
    log_message("Starting the process...")  # Log the process start

    # Initialize the supervisor
    supervisor = Agent("supervisor", "assigning task")
    
    # Get all pending jobs

    log_message("supervisor Fetching all pending jobs...")
    all_customer = supervisor.get_pending_job()
    all_customer_df = pd.DataFrame(all_customer)
    
    # Filter out customers with pending email verification and response status
    log_message("Filtering pending customers for email verification and response status...")
    pending_customer_email = all_customer_df[
        (all_customer_df[' Email Verified (Y/N)'] == 'pending') & 
        (all_customer_df[' Response Status'] == 'pending')
    ][['Lead Name', ' Email']].values.tolist()
    log_message(f"Pending customers found: {len(pending_customer_email)}")

    # Initialize agent to verify email
    agentA = Agent("agent_a", "verify email")
    log_message("Agent A Verifying emails...")
    verified_email = [email for email in pending_customer_email if agentA.email_verfication(email[1])]
    log_message(f"Verified emails count: {len(verified_email)}")

    # Initialize agent to send emails and store response
    agentB = Agent("agent_b", "send mail and store response")
    log_message("Agent B Sending emails and geting respondr from verified customers...")
    for name, email in verified_email:
        agentB.send_email(email, name)

    # Generate the report
    log_message("Generating report...")
    data_df = supervisor.google_sheet_api.get_data_as_dataframe()
    report = data_df[
        (data_df[' Email Verified (Y/N)'] == 'Y') & 
        (data_df[' Response Status'] == 'Interested')
    ][[' Email Verified (Y/N)',' Response Status']].count().to_dict()

    log_message(f"Report generated: {report}")
    
    # Send the report to the stackholder
    supervisor.send_email_stackholder(report[' Email Verified (Y/N)'], report[' Response Status'])
    log_message("Supervisor sending summary Report to stackholder!")

# Schedule the process to run every 1 minute
schedule.every(30).seconds.do(process)

log_message("Starting scheduled tasks...")  # Log the start of the scheduled tasks

while True:
    schedule.run_pending()  # Run the scheduled tasks
    time.sleep(30)  # Sleep for 1 minute before checking for pending tasks again
