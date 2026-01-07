import streamlit as st
import requests
import time
from urllib.parse import quote

# --- 1. CONFIGURATION ---
LIVE_KEY = st.secrets["HeyGen"]["LIVE_AVATAR_KEY"]
BASE_URL = "https://api.liveavatar.com/v1"
HEADERS = {
    "X-API-KEY": LIVE_KEY,
    "accept": "application/json",
    "content-type": "application/json",
}

# Accurate IDs from your setup
AVATAR_ID = "65f9e3c9-d48b-4118-b73a-4ae2e3cbb8f0"  # June HR
VOICE_ID = "62bbb4b2-bb26-4727-bc87-cfb2bd4e0cc8"   # June Lifelike
BLANK_CONTEXT_ID = "04951707-afab-4fe5-be9e-d6d3d1233a92"  # Your Blank Context
FIXED_TEXT = "Hello How Are you- I am JUNE the LIVE avatar from HeyGen."

st.set_page_config(page_title="June CUSTOM Mode Test")
st.title("LiveAvatar: June (CUSTOM Mode)")

# --- 2. SESSION FUNCTIONS ---
def start_custom_session():
    # Force CUSTOM mode to prevent default AI interference
    payload = {
        "mode": "CUSTOM", 
        "avatar_id": AVATAR_ID,
        "avatar_persona": {
            "voice_id": VOICE_ID,
            "context_id": BLANK_CONTEXT_ID,
            "language": "en"
        }
    }
    
    # Create Token
    resp = requests.post(f"{BASE_URL}/sessions/token", headers=HEADERS, json=payload)
    token_data = resp.json().get("data")
    if not token_data:
        st.error(f"Failed to get token: {resp.text}")
        return None
    
    s_token = token_data.get("session_token")
    
    # Start Session
    start_resp = requests.post(
        f"{BASE_URL}/sessions/start", 
        headers={"authorization": f"Bearer {s_token}", "accept": "application/json"}
    )
    return start_resp.json().get("data"), s_token

def send_command(s_token, event_type, extra_params=None):
    # In a full production app, this would use LiveKit publishData.
    # For this test, we use the REST Command API
    url = f"{BASE_URL}/sessions/command"
    payload = {"event_type": event_type}
    if extra_params:
        payload.update(extra_params)
        
    requests.post(url, headers={"authorization": f"Bearer {s_token}"}, json=payload)

# --- 3. UI EXECUTION ---
if st.button("🚀 Initialize June (CUSTOM Mode)"):
    data, s_token = start_custom_session()
    
    if data:
        st.success("Session Created. Initializing WebRTC...")
        
        # Open the viewer first so the user can see initialization
        lk_url = data.get("livekit_url")
        lk_token = data.get("livekit_client_token")
        viewer_url = f"https://meet.livekit.io/custom?liveKitUrl={quote(lk_url)}&token={quote(lk_token)}"
        st.markdown(f"### [👉 OPEN JUNE VIEWER]({viewer_url})")
        
        # 90-Second Warm-up Countdown
        countdown_placeholder = st.empty()
        for i in range(90, 0, -1):
            countdown_placeholder.info(f"⏳ June is warming up... Sending command in {i} seconds.")
            time.sleep(1)
        
        # THE OVERRIDE SEQUENCE
        st.warning("⚡ Sending Interrupt and Fixed Text...")
        
        # 1. Interrupt (forget any idle state/context noise)
        send_command(s_token, "avatar.interrupt")
        time.sleep(0.5)
        
        # 2. Speak Text (The Fixed Sentence)
        send_command(s_token, "avatar.speak_text", {"text": FIXED_TEXT})
        
        st.success("✅ Command Sent! Check the viewer window.")
        st.session_state['s_token'] = s_token

if st.button("Stop Session"):
    if 's_token' in st.session_state:
        requests.post(f"{BASE_URL}/sessions/stop", headers={"authorization": f"Bearer {st.session_state['s_token']}"})
        st.write("Session terminated.")
