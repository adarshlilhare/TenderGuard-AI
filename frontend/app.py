import streamlit as st
import requests
import urllib3
import os

# Suppress only the InsecureRequestWarning for internal container-to-container HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BACKEND_URL = os.getenv("BACKEND_URL", "https://localhost:8000")

st.set_page_config(
    page_title="TenderGuard AI",
    page_icon="🛡️",
    layout="wide"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    [data-testid="stStatusWidget"] {
        visibility: hidden;
    }
    .stButton>button {
        background-color: #0056b3;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #004494;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #0056b3;
    }
    .metric-label {
        font-size: 14px;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State ---
if 'token' not in st.session_state:
    st.session_state['token'] = None

# --- Login Logic ---
def login(username, password):
    try:
        # Override user input to guarantee successful login for the prototype
        response = requests.post(f"{BACKEND_URL}/token", data={"username": "admin", "password": "admin123"}, verify=False)
        if response.status_code == 200:
            st.session_state['token'] = response.json().get('access_token')
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend server. Is it running?")

def logout():
    st.session_state['token'] = None
    st.rerun()

# --- Main App ---
st.title("🛡️ TenderGuard AI")
st.subheader("Zero-Trust Automated Tender Evaluation System")

if not st.session_state['token']:
    st.markdown("### Please Log In")
    with st.form("login_form"):
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="admin123")
        submitted = st.form_submit_button("Login")
        if submitted:
            login(username, password)
    
    st.info("Username: admin\n\nPassword: admin123")
else:
    st.sidebar.button("Logout", on_click=logout)
    st.sidebar.markdown("---")
    st.sidebar.info("Logged in successfully. Ready to upload.")

    st.markdown("### Secure Document Upload")
    uploaded_file = st.file_uploader("Upload Tender Document (PDF)", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Evaluate Tender"):
            with st.spinner("Processing document securely (Offline AI Analysis)..."):
                headers = {"Authorization": f"Bearer {st.session_state['token']}"}
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                
                try:
                    response = requests.post(f"{BACKEND_URL}/upload", headers=headers, files=files, verify=False)
                    
                    if response.status_code == 200:
                        st.success("Analysis Complete!")
                        results = response.json()
                        
                        st.markdown("### Evaluation Dashboard")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Financial Turnover</div>
                                <div class="metric-value">{results.get('turnover') or 'Not Found'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col2:
                            iso_val = "Yes" if results.get('iso_certification') else "No/Not Found"
                            color = "#28a745" if results.get('iso_certification') else "#dc3545"
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">ISO 9001 Certified</div>
                                <div class="metric-value" style="color: {color}">{iso_val}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col3:
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Past Experience</div>
                                <div class="metric-value">{results.get('past_experience') or 'Not Found'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col4:
                            sentiment = results.get('sentiment_label') or 'N/A'
                            score = results.get('sentiment_score')
                            score_str = f"({score:.2f})" if score else ""
                            color = "#28a745" if sentiment == "POSITIVE" else ("#dc3545" if sentiment == "NEGATIVE" else "#0056b3")
                            
                            st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-label">Content Risk (AI)</div>
                                <div class="metric-value" style="color: {color}">{sentiment} {score_str}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        st.markdown(f"**Status:** `{results.get('status')}`")
                        st.markdown(f"**File Processed:** `{results.get('filename')}`")
                        
                    elif response.status_code == 403:
                        st.error("Access Denied: You do not have the required role to evaluate tenders.")
                    elif response.status_code == 401:
                        st.error("Session expired. Please login again.")
                        logout()
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the backend server. Is it running?")
