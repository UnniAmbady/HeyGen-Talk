import streamlit as st
import requests
import json
import asyncio

# --- 1. SETUP & SECRETS ---
# Ensure your .streamlit/secrets.toml looks like:
# [HeyGen]
# LIVE_AVATAR_KEY = "your_key_here"

API_KEY = st.secrets["HeyGen"]["LIVE_AVATAR_KEY"]
BASE_URL = "https://api.liveavatar.com/v1"
HEADERS = {
    "X-API-KEY": API_KEY,
    "accept": "application/json",
    "content-type": "application/json",
}

# Values identified from your JSON and Notebook
AVATAR_ID = "65f9e3c9-d48b-4118-b73a-4ae2e3cbb8f0"  # June HR
VOICE_ID = "62bbb4b2-bb26-4727-bc87-cfb2bd4e0cc8"   # June Lifelike
FIXED_TEXT = "Hello How Are you- I am JUNE the LIVE avatar from HeyGen."

st.title("Avatar Agentic AI - LiveAvatar Test")

# --- 2. SESSION FUNCTIONS ---
def create_session():
    payload = {
        "mode": "FULL",
        "avatar_id": AVATAR_ID,
        "avatar_persona": {
            "voice_id": VOICE_ID,
            "language": "en"
        }
    }
    # Create Token
    resp = requests.post(f"{BASE_URL}/sessions/token", headers=HEADERS, json=payload)
    token_data = resp.json().get("data", {})
    session_token = token_data.get("session_token")
    
    # Start Session
    start_headers = {"authorization": f"Bearer {session_token}"}
    start_resp = requests.post(f"{BASE_URL}/sessions/start", headers=start_headers)
    return start_resp.json().get("data", {}), session_token

# --- 3. STREAMLIT UI ---
if st.button("Initialize & Speak"):
    with st.spinner("Starting June..."):
        data, s_token = create_session()
        
        if data:
            st.success("Session Started!")
            st.write(f"LiveKit URL: {data.get('livekit_url')}")
            
            # Logic for agent-control command
            # In a real production app, this JSON is sent via the LiveKit Data Channel topic 'agent-control'
            speak_command = {
                "event_type": "avatar.speak_text",
                "text": FIXED_TEXT
            }
            
            st.info("Sending Command to 'agent-control' topic...")
            st.json(speak_command)
            
            # Display the quick join link from your notebook logic
            lk_url = data.get('livekit_url')
            lk_token = data.get('livekit_client_token')
            viewer_url = f"https://meet.livekit.io/custom?liveKitUrl={lk_url}&token={lk_token}"
            
            st.markdown(f"### [👉 Open Avatar View]({viewer_url})")
        else:
            st.error("Failed to start session.")

# Cleanup Section
if st.button("Stop Session"):
    # Reference to stop session logic
    st.write("Stopping backend stream...")
