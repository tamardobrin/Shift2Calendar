import os
import json
import pickle
import requests
from dotenv import load_dotenv

load_dotenv()

COMPANY = os.getenv("COMPANY")
SO_USERNAME = os.getenv("SO_USERNAME")
PASSWORD = os.getenv("PASSWORD")

LOGIN_URL = "https://app.shiftorganizer.com/api/auth/login/"

def login():
    session = requests.Session()
    login_payload = {
        "company": COMPANY,
        "username": SO_USERNAME,
        "password": PASSWORD
    }

    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    #     "Content-Type": "application/json",
    #     "Accept": "application/json"
    # }

    try:
        response = session.post(LOGIN_URL, json=login_payload)
        response.raise_for_status()  

        print("Login successful!")

        with open("cookies.pkl", "wb") as file:
            pickle.dump(session.cookies, file)
        print("Cookies saved successfully!")

        user_id = response.json().get("id", None)
        if user_id:
            with open("user_id.json", "w") as file:
                json.dump({"id": user_id}, file)
            print("User ID saved successfully:", user_id)
        else:
            print("Warning: No user ID found in response!")

    except requests.exceptions.RequestException as e:
        print(f"Login failed! Error: {e}")

if __name__ == "__main__":
    login()
