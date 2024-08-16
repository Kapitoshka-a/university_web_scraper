"""File for dumping data into a google spreadsheets"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1yMDaqac6w-llZozpR19XMFgWVyuo4sjDfGdUhR3t1-w'
RANGE_NAME = 'Аркуш1!A1'


def main():
    creds = None
    if os.path.exists("data/token.json"):
        creds = Credentials.from_authorized_user_file("data/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("data/client_secret_data.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("data/token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        with open('data/universities.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

        values = [['Title', 'Address', 'Link', 'Type of Educational Institution', 'Ownership', 'Tuition Fee per Year',
                   'Form of Education', 'Qualification Level', 'Amount of Students', 'City', 'Consolidated Rating 2022',
                   'Consolidated Rating 2023']]
        for item in data:
            values.append([
                item['title'],
                item['address'],
                item['link'],
                item['type_of_educational_institution'],
                item['ownership'],
                item['tuition_fee_per_year'],
                item['form_of_education'],
                item['qualification_level'],
                item['amount_of_students'],
                item['city'],
                item['consolidated_rating_2022'],
                item['consolidated_rating_2023']
            ])

        body = {
            'values': values
        }

        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='RAW', body=body).execute()

        print(f"{result.get('updatedCells')} cells updated.")

    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
