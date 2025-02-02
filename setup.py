import gspread
from google.oauth2.service_account import Credentials as google_credential
import os 
from dotenv import load_dotenv
import pandas as pd
load_dotenv()


class getCredential():

    def __init__(self):
        self.HEADER = [os.getenv("HEADER").split(',')]
        self.SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
        self.SCOPES = os.getenv("SCOPES").split(',')
        self.EXCEL_NAME = os.getenv('EXCEL_NAME')

class googleApi():
    def __init__(self):
        self.credentials = getCredential()
        creds = google_credential.from_service_account_file(self.credentials.SERVICE_ACCOUNT_FILE, scopes = self.credentials.SCOPES)
        self.client = gspread.authorize(creds)
    def get_worksheet(self):
        spreadsheet = self.client.open(self.credentials.EXCEL_NAME)
        worksheet = spreadsheet.sheet1
        return worksheet
    def setup_google_sheet(self):
        worksheet = self.get_worksheet()
        worksheet.clear()
        worksheet.update('A1:H1', self.credentials.HEADER) 
    def __get_data__(self):
        worksheet = self.get_worksheet()
        return worksheet.get_all_values()

    def get_data_as_dataframe(self):
        worksheet =self.get_worksheet()
        data = worksheet.get_all_values()

        if not data:
            return pd.DataFrame() 
        df = pd.DataFrame(data[1:], columns = data[0])
        return df

    def update_dataframe_to_sheet(self, df):
        """
        Update Google Sheets with the modified DataFrame.
        """
        worksheet = self.get_worksheet()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())  # Update the sheet with the new data
 
    def update_element(self, email, column_name, new_value):
        """
        Update an element in the Google Sheet and Pandas DataFrame.
        
        :param email: The email of the lead to update.
        :param column_name: The column name (e.g., "Response Status").
        :param new_value: The new value to update in the DataFrame and Google Sheets.
        """
        df = self.get_data_as_dataframe()

        if email not in df[' Email'].values:
            print(f"❌ Email {email} not found.")
            return

        # Update the specific column for the matching email
        df.loc[df[' Email'] == email, column_name] = new_value

        # Push the updated DataFrame back to Google Sheets
        self.update_dataframe_to_sheet(df)

        print(f"✅ Updated {column_name} for {email} to {new_value}")
    
        



if __name__ == "__main__":
    google_api = googleApi()
    
    # Example: Updating "Response Status" for a specific email
    google_api.update_element(
        email="contact.srv.sh@gmail.com",
        column_name=" Response Status",
        new_value="Interested"
    )
