from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pickle
from google.oauth2 import service_account
from googleapiclient.discovery import build
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 🔥 Add CORS Middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any frontend (for dev)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Shift Organizer API URL
LOGIN_URL = "https://app.shiftorganizer.com/api/auth/login/"

# Define the request body structure
class LoginRequest(BaseModel):
    company: str
    username: str
    password: str

@app.post("/login")
def login(data: LoginRequest):
    """Logs in to Shift Organizer and saves session cookies."""
    session = requests.Session()

    login_payload = {
        "company": data.company,
        "username": data.username,
        "password": data.password
    }

    response = session.post(LOGIN_URL, json=login_payload)

    if response.status_code == 200:
        # Save session cookies to reuse later
        with open("cookies.pkl", "wb") as file:
            pickle.dump(session.cookies, file)

        user_id = response.json().get("id")
        return {"message": "Login successful!", "user_id": user_id}
    
    raise HTTPException(status_code=401, detail="Login failed!")


@app.get("/schedule/{user_id}")
def fetch_schedule(user_id: int):
    """Fetch the user's schedule from Shift Organizer API."""
    try:
        with open("cookies.pkl", "rb") as file:
            session_cookies = pickle.load(file)
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Not logged in. Please log in first.")

    session = requests.Session()
    session.cookies.update(session_cookies)

    ROTA_URL = "https://app.shiftorganizer.com/api/rotas"
    rota_response = session.get(ROTA_URL)

    if rota_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch rota ID.")

    rota_id = rota_response.json()[0].get("id")

    API_URL = f"https://app.shiftorganizer.com/api/cells/?rota={rota_id}&employee={user_id}"
    response = session.get(API_URL)

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=400, detail="Failed to fetch schedule.")

@app.post("/sync-calendar/{user_id}")
def sync_calendar(user_id: int):
    """Fetch shifts from Shift Organizer and add them to Google Calendar."""
    schedule = fetch_schedule(user_id)  

    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    SERVICE_ACCOUNT_FILE = "credentials.json"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)

    CALENDAR_ID = "tamar.dobrin@gmail.com"  

    for shift in schedule:
        start_datetime = f"{shift['date']}T{shift['planned_start']}"
        end_datetime = f"{shift['date']}T{shift['planned_end']}"

        event = {
            "summary": f"Work Shift (Role {shift['role']})",
            "start": {"dateTime": start_datetime, "timeZone": "Asia/Jerusalem"},
            "end": {"dateTime": end_datetime, "timeZone": "Asia/Jerusalem"},
        }

        service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

    return {"message": "Shifts synced to Google Calendar!"}