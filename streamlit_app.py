import streamlit as st
import requests
import json

# --- 1. SETUP & SECRETS ---
# Using the 36-byte HEX key for LiveAvatar sessions as per your .ipynb
LIVE_KEY = st.secrets["HeyGen"]["LIVE_AVATAR_KEY"]
BASE_URL = "https://api.liveavatar.com/v1"

HEADERS = {
    "X-API-KEY": LIVE_KEY,
    "accept": "application/json",
    "content-type": "application/json",
}

# Accurate IDs from your uploaded metadata and notebook
AVATAR_ID = "65f9e3c9-d48b-4118-b73a-4ae2e3cbb8f0"  # June HR
VOICE_ID = "62bbb4b2-bb26-4727-bc87-cfb2bd4e0cc8"   # June Lifelike
# Note: In FULL mode, a Context ID is recommended to avoid LLM errors
CONTEXT_ID = "9d633fe3-d462-49a7-8b06-d9c3fcfad5e9" # 3D-Printing example from your log

st.title("Avatar Agentic AI")
st.subheader("LiveAvatar: June HR")

# --- 2. SESSION LOGIC ---
def create_live_session():
    payload = {
        "mode": "FULL",
        "avatar_id": AVATAR_ID,
        "avatar_persona": {
            "voice_id": VOICE_ID,
            "context_id": CONTEXT_ID,
            "language": "en"
        }
    }
    
    # 1. Get Session Token
    token_resp = requests.post(f"{BASE_URL}/sessions/token", headers=HEADERS, json=payload)
    
    if token_resp.status_code != 200:
        st.error(f"Token Error: {token_resp.text}")
        return None, None

    token_json = token_resp.json()
    # Handle the 'data' wrapper to prevent the 'NoneType' error in your logs 
    data_wrapper = token_json.get("data")
    if not data_wrapper:
        st.error("Invalid response format: Missing 'data' field.")
        return None, None
        
    session_token = data_wrapper.get("session_token")
    
    # 2. Start the Session
    start_headers = {
        "accept": "application/json",
        "authorization": f"Bearer {session_token}"
    }
    start_resp = requests.post(f"{BASE_URL}/sessions/start", headers=start_headers)
    
    if start_resp.status_code not in [200, 201]:
        st.error(f"Start Error: {start_resp.text}")
        return None, None
        
    return start_resp.json().get("data"), session_token

# --- 3. UI ---
if st.button("Launch June"):
    with st.spinner("Establishing Live Connection..."):
        session_data, s_token = create_live_session()
        
        if session_data:
            st.success("June is Online!")
            
            # Extract LiveKit details for the viewer
            lk_url = session_data.get("livekit_url")
            lk_token = session_data.get("livekit_client_token")
            
            # Construct the Quick Join URL
            from urllib.parse import quote
            viewer_url = f"https://meet.livekit.io/custom?liveKitUrl={quote(lk_url)}&token={quote(lk_token)}"
            
            st.markdown(f"### [🚀 Open Interactive View]({viewer_url})")
            st.info("Once the window opens, June will be ready to respond to your voice or text.")
            
            # Store session token in session state for the stop button
            st.session_state['current_s_token'] = s_token

if st.button("Stop Session"):
    if 'current_s_token' in st.session_state:
        stop_headers = {"authorization": f"Bearer {st.session_state['current_s_token']}"}
        requests.post(f"{BASE_URL}/sessions/stop", headers=stop_headers)
        st.warning("Session Closed.")
    else:
        st.write("No active session to stop.")
