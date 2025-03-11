from fastapi import APIRouter, HTTPException
import requests
import pickle
import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

router = APIRouter()

ROLES_API_URL = "https://app.shiftorganizer.com/api/roles-list/"
ROTA_URL = "https://app.shiftorganizer.com/api/rotas"

def load_session():
    """Load saved session cookies."""
    with open("cookies.pkl", "rb") as file:
        return pickle.load(file)

@router.get("/schedule/{user_id}")
def fetch_schedule(user_id: int):
    session = requests.Session()
    session.cookies.update(load_session())

    rota_response = session.get(ROTA_URL)
    rota_id = rota_response.json()[0].get("id")

    API_URL = f"https://app.shiftorganizer.com/api/cells/?rota={rota_id}&employee={user_id}"
    response = session.get(API_URL)

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=400, detail="Failed to fetch schedule!")
