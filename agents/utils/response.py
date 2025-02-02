from flask import Flask, request
import json
import sys
sys.path.append("../..")
from setup import googleApi

app = Flask(__name__)
# google_api = googleApi()

@app.route('/sendgrid_webhook', methods=['POST'])
def sendgrid_webhook():
    events = request.get_json()
    
    # Parse the events and determine the action (open, click, etc.)
    for event in events:
        email = event.get('email')
        event_type = event.get('event')  # 'open', 'click', 'bounce', etc.
        timestamp = event.get('timestamp')
        
        # Log or process the event (open, click, etc.)
        # print(f"Email: {email} | Event: {event_type} | Timestamp: {timestamp}")

        # Depending on the event type, update the response status in your sheet
        update_response_status(email, event_type,timestamp)

    return 'OK'

def update_response_status(email, event_type,timestamp):
    googleapi = googleApi()
    # Here you'd update your Google Sheet or database with the response status
    status = 'pending'
    if event_type == 'click':
        print(f"Email: {email} | Event: {event_type} | Timestamp: {timestamp}")
        status = 'Interested'  # Or another custom status based on clicks
    elif event_type == 'unsubscribe':
        print(f"Email: {email} | Event: {event_type} | Timestamp: {timestamp}")
        status = 'Not Interested'
    elif event_type == 'spamreport':
        print(f"Email: {email} | Event: {event_type} | Timestamp: {timestamp}")
        status = 'Not Interested'
    
    if status in ['Interested','Not Interested']:
        print(f"customer is {status}")
        googleapi.update_element(
            email=email,
            column_name=" Response Status",
            new_value=status
        )
    



if __name__ == '__main__':
    app.run(debug=True)