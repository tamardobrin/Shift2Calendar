from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import pickle
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

CALENDAR_ID = os.getenv("CALENDAR_ID", "primary")
ROLES_API_URL = "https://app.shiftorganizer.com/api/roles-list/"
ROTA_URL = "https://app.shiftorganizer.com/api/rotas"
LOGIN_URL = "https://app.shiftorganizer.com/api/auth/login/"

class LoginRequest(BaseModel):
    company: str
    username: str
    password: str

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
        "start": {"dateTime": start_datetime, "timeZone": "Asia/Jerusalem"},
        "end": {"dateTime": end_datetime, "timeZone": "Asia/Jerusalem"},
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

@app.post("/login")
def login(data: LoginRequest):
    session = requests.Session()
    login_payload = {"company": data.company, "username": data.username, "password": data.password}
    response = session.post(LOGIN_URL, json=login_payload)
    if response.status_code == 200:
        with open("cookies.pkl", "wb") as file:
            pickle.dump(session.cookies, file)
        user_id = response.json().get("id")
        return {"message": "Login successful!", "user_id": user_id}
    raise HTTPException(status_code=401, detail="Login failed!")

@app.get("/schedule/{user_id}")
def fetch_schedule(user_id: int):
    session = requests.Session()
    session.cookies.update(load_session())
    rota_id = get_current_rota_id(session)
    if not rota_id:
        raise HTTPException(status_code=400, detail="Failed to get rota ID.")
    role_mapping = get_role_mapping(session)
    schedule_data = get_schedule_data(session, rota_id, user_id)
    extracted_data = [{
        "date": entry["date"],
        "planned_start": entry["planned_start"],
        "planned_end": entry["planned_end"],
        "role": entry["role"],
        "role_name": role_mapping.get(entry["role"], "Unknown Role")
    } for entry in schedule_data]
    return extracted_data

@app.post("/sync-calendar/{user_id}")
def sync_calendar(user_id: int):
    schedule = fetch_schedule(user_id)
    df = pd.DataFrame(schedule)
    events = [format_event(row) for _, row in df.iterrows()]
    add_events_to_google_calendar(events)
    return {"message": "Shifts synced to Google Calendar!"}
