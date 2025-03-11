import os
import json
import pickle
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")  # Default to "primary" if not set
ROLES_API_URL = "https://app.shiftorganizer.com/api/roles-list/"
ROTA_URL = "https://app.shiftorganizer.com/api/rotas"

def load_session():
    with open("cookies.pkl", "rb") as file:
        return pickle.load(file)

def load_user_id():
    try:
        with open("user_id.json", "r") as file:
            return json.load(file).get("id", None)
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: User ID file not found or corrupted.")
        return None

def get_current_rota_id(session):
    response = session.get(ROTA_URL)
    if response.status_code == 200:
        return response.json()[0].get("id", None)
    else:
        print(f"Failed to fetch rota ID! Status code: {response.status_code}")
        return None

def get_role_mapping(session):
    response = session.get(ROLES_API_URL)
    if response.status_code == 200:
        return {entry["id"]: entry["name"] for entry in response.json()}
    else:
        print("Failed to fetch role names!")
        return {}

def get_schedule_data(session, rota_id, user_id):
    API_URL = f"https://app.shiftorganizer.com/api/cells/?rota={rota_id}&employee={user_id}"
    response = session.get(API_URL)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch schedule! Status code: {response.status_code}")
        return []

def format_event(row):
    start_datetime = f"{row['date']}T{row['planned_start']}"
    end_datetime = f"{row['date']}T{row['planned_end']}"

    try:
        datetime.fromisoformat(start_datetime)
        datetime.fromisoformat(end_datetime)
    except ValueError:
        print(f"Invalid date format: {start_datetime} - {end_datetime}")
        return None

    return {
        "summary": f"Work Shift - {row['role_name']}",
        "start": {
            "dateTime": start_datetime,
            "timeZone": "Asia/Jerusalem"
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": "Asia/Jerusalem"
        }
    }

def add_events_to_google_calendar(events):
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    SERVICE_ACCOUNT_FILE = "credentials.json"

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=credentials)

        for event in events:
            if event:
                created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
                print(f"Event created: {created_event.get('htmlLink')}")

    except Exception as e:
        print(f"Error adding event to Google Calendar: {e}")

if __name__ == "__main__":
    session = requests.Session()
    session.cookies.update(load_session())

    user_id = load_user_id()
    if not user_id:
        exit()

    rota_id = get_current_rota_id(session)
    if not rota_id:
        exit()

    role_mapping = get_role_mapping(session)
    schedule_data = get_schedule_data(session, rota_id, user_id)

    extracted_data = [{
        "date": entry["date"],
        "planned_start": entry["planned_start"],
        "planned_end": entry["planned_end"],
        "role": entry["role"],
        "role_name": role_mapping.get(entry["role"], "Unknown Role")
    } for entry in schedule_data]

    df = pd.DataFrame(extracted_data)
    events = [format_event(row) for _, row in df.iterrows()]
    
    add_events_to_google_calendar(events)