from fastapi import Body
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import requests
import pickle
import json
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
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

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

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
        return None

def get_current_rota_id(session):
    response = session.get(ROTA_URL)
    if response.status_code == 200:
        return response.json()[0].get("id", None)
    return None

def get_role_mapping(session):
    response = session.get(ROLES_API_URL)
    if response.status_code == 200:
        return {entry["id"]: entry["name"] for entry in response.json()}
    return {}

def get_schedule_data(session, rota_id, user_id):
    API_URL = (
        f"https://app.shiftorganizer.com/api/cells/?rota={rota_id}&employee={user_id}"
    )
    response = session.get(API_URL)
    if response.status_code == 200:
        return response.json()
    return []

def format_event(row):
    start_datetime = f"{row['date']}T{row['planned_start']}"
    end_datetime = f"{row['date']}T{row['planned_end']}"
    try:
        datetime.fromisoformat(start_datetime)
        datetime.fromisoformat(end_datetime)
    except ValueError:
        return None
    return {
        "summary": f"Work Shift - {row['role_name']}",
        "start": {"dateTime": start_datetime, "timeZone": "Asia/Jerusalem"},
        "end": {"dateTime": end_datetime, "timeZone": "Asia/Jerusalem"},
    }

@app.get("/")
def home():
    return {"message": "FastAPI Backend is Running!"}

@app.post("/login")
def login(data: LoginRequest):
    session = requests.Session()
    login_payload = {
        "company": data.company,
        "username": data.username,
        "password": data.password,
    }
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
    extracted_data = [
        {
            "date": entry["date"],
            "planned_start": entry["planned_start"],
            "planned_end": entry["planned_end"],
            "role": entry["role"],
            "role_name": role_mapping.get(entry["role"], "Unknown Role"),
        }
        for entry in schedule_data
        if entry.get("planned_start") and entry.get("planned_end")
    ]
    return extracted_data

# Generate Google Calendar Event Link for Individual Shift
@app.get("/calendar-link")
def generate_calendar_link(date: str, start_time: str, end_time: str, role_name: str):
    base_url = "https://www.google.com/calendar/event?action=TEMPLATE"
    formatted_date = date.replace("-", "")
    start_datetime = f"{formatted_date}T{start_time.replace(':', '')}"
    end_datetime = f"{formatted_date}T{end_time.replace(':', '')}"
    event_title = f"Shift - {role_name}"

    event_url = f"{base_url}&dates={start_datetime}/{end_datetime}&text={event_title}&location=&details=Shift+scheduled"
    return {"google_calendar_link": event_url}

@app.get("/auth/login")
def login_with_google():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    authorization_url, _ = flow.authorization_url(
        access_type="offline", prompt="consent"
    )
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
def auth_callback(code: str):
    """Handles Google OAuth callback, gets access token."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(code=code)

    credentials = flow.credentials
    access_token = credentials.token
    refresh_token = credentials.refresh_token

    token_data = {
    "access_token": credentials.token,
    "refresh_token": credentials.refresh_token,
    "token_uri": credentials.token_uri,
    "client_id": credentials.client_id,
    "client_secret": credentials.client_secret,
    }

    with open("oauth_credentials.json", "w") as f:
        json.dump(token_data, f)

    return RedirectResponse(f"https://dobrin.xyz/dashboard?access_token={access_token}")


@app.post("/sync-calendar-oauth")
def sync_calendar_oauth(
    access_token: str = Body(..., embed=True), shifts: list = Body(...)
):
    """Uses Google OAuth token to add multiple shifts to Google Calendar."""
    if not access_token:
        raise HTTPException(status_code=400, detail="Missing access token")

    # creds = Credentials(token=access_token)
    with open("oauth_credentials.json", "r") as f:
       token_data = json.load(f)

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data["token_uri"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
    )
    service = build("calendar", "v3", credentials=creds)

    for shift in shifts:
        event = {
            "summary": f"Shift - {shift['role_name']}",
            "start": {
                "dateTime": f"{shift['date']}T{shift['planned_start']}",
                "timeZone": "Asia/Jerusalem",
            },
            "end": {
                "dateTime": f"{shift['date']}T{shift['planned_end']}",
                "timeZone": "Asia/Jerusalem",
            },
        }
        service.events().insert(calendarId="primary", body=event).execute()

    return {"message": "Shifts added successfully via OAuth!"}
