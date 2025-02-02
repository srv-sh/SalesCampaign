import sys
from dotenv import load_dotenv
import os
import requests
import re
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import smtplib
from email.message import EmailMessage


load_dotenv()


sys.path.append("..")
from setup import googleApi


class Task():
    def __init__(self):
        self.google_sheet_api = googleApi()
        self.rows = self.google_sheet_api.__get_data__()
        self.headers = self.rows[0]
        self.data = self.rows[1:]
        self.hunter_api = os.getenv("HUNTER")
        self.PLAIN_TEXT_EMAIL = os.getenv("PLAIN_TEXT_EMAIL")
        self.HTML_EMAIL = os.getenv("HTML_EMAIL")


    def get_pending_job(self):

        pending_tasks = [
            {self.headers[i]: row[i] for i in range(len(self.headers))}
            for row in self.data
            if row[5] == 'pending' or row[6] == 'pending'  # Email Verified or Response Status is empty
        ]

        return pending_tasks
    

    def email_verfication(self,email):

        """
        Check if the given string is a valid email address.
        
        :param email: The email address to validate
        :return: True if valid, False otherwise
        """
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if bool(re.match(email_regex, email)):

            self.google_sheet_api.update_element(
                    email=email,
                    column_name=" Email Verified (Y/N)",
                    new_value="Y"
                )

            return True
        else: 
            return False 

        # hunter_api = self.hunter_api.format(email)
        # response = requests.get(hunter_api)
        # result = response.json()
        # print(result)
        # return result['data']['gibberish']


        # print(self.hunter_api.format(email))
    def send_email(self, to_email, to_name):
        is_verified = self.email_verfication(to_email)
        if is_verified:

            # Define email content
            plain_text_content = f"Hi {to_name},\n\nGet 20% off your next purchase!\nVisit: https://www.linkedin.com/in/srv-sh/"
            html_content = f"""
            <p>Hi {to_name},</p>
            <p>Get <b>20% off</b> your next purchase!</p>
            <p>Click <a href="https://www.linkedin.com/in/srv-sh/" target="_blank">here</a> to claim your offer.</p>
            """

            # Create email message
            message = Mail(
                from_email=Email('contact.srv.sh@gmail.com'),
                to_emails=to_email,
                subject='Exclusive Offer for You!',
                plain_text_content=self.PLAIN_TEXT_EMAIL.format(to_name),
                html_content=self.HTML_EMAIL.format(to_name)  # Add HTML content for better tracking
            )

            # Set reply-to email
            message.reply_to = Email('study.srv.sh@gmail.com')

            try:
                sg = SendGridAPIClient(os.getenv("SENDGRID"))
                response = sg.send(message)
                print(f"✅ Email sent to {to_name} ({to_email}) with status code {response.status_code}")
            except Exception as e:
                print(f"❌ Failed to send email to {to_name} ({to_email}): {str(e)}") 
        else:
            print("email address is not valid")
    def send_email_stackholder(self, total_verified, total_interested):
        host =  os.getenv("EMAIL_HOST")    
        port =  os.getenv("EMAIL_PORT")
        from_email =  os.getenv("EMAIL_USER")
        password =  os.getenv("EMAIL_PASS")
        subject =  os.getenv("SUBJECT")
        stack_email = os.getenv("STACKHOLDER")
        body = os.getenv("BODY").format(total_verified, total_interested)

        msg = EmailMessage()
        msg["Subject"] = subject 
        msg["From"] = from_email
        msg["To"] = stack_email
        msg.set_content(body)

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL(host, port) as server:
            server.login(from_email, password)
            server.send_message(msg)
            print("Email sent successfully!!")





          



class Agent(Task):
    def __init__(self, name , role):
        super().__init__()
        self.__name__ = name
        self.__role__ = role
        # self.__permission__ = permission
    

if __name__ == "__main__":
    task  = Task()
    # is_valid =  task.send_email('data.geek.srv@gmail.com','sourav saha')
    print(task.send_email_stackholder(5,10))
