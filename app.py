import json
import streamlit as st
import requests
from PIL import Image
from io import BytesIO

import jwt
import time
from datetime import datetime, timezone
from dotenv import load_dotenv
from streamlit_javascript import st_javascript


load_dotenv()
SECRET_KEY= "your_secret_key"
ALGORITHM = "HS256"

# Initialize the screen state using session state
if "screenstate" not in st.session_state:
    st.session_state.screenstate = {
        "login_page": True,
        "logout": False,
        "generate_reports": False,  
        "visual_qa": False,
        "drift_detection": False,
    }

# Function to authenticate user and get token
def authenticate(username, password):
    try:
        response = requests.post(
            "http://127.0.0.1:8000/token/",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            st.error("Incorrect username or password.")
            return None
    except Exception as e:
        st.error(f"An error occurred during authentication: {str(e)}")
        return None
 
 
# ____________________________________________________________________________________________________________________________


# Define functions to interact with localStorage
def local_storage_get(key):
    return st_javascript(f"localStorage.getItem('{key}');")

def local_storage_set(key, value):
    value = json.dumps(value)
    return st_javascript(f"localStorage.setItem('{key}', JSON.stringify({value}));")

def local_storage_remove(key):
    return st_javascript(f"localStorage.removeItem('{key}');")

def is_token_valid(token: str):
    try:
        # Decode the token without verifying the signature (just to extract the exp)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Get the expiration time (exp) from the payload
        exp_timestamp = payload.get("exp")
        
        # Check if the token has expired
        if exp_timestamp:
            exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_datetime > datetime.now(timezone.utc):
                return True  # Token is still valid
            else:
                st.error("Token has expired.")
                return False  # Token has expired
        else:
            st.error("No expiration field in token.")
            return False  # No expiration info in token

    except jwt.ExpiredSignatureError:
        st.error("Token has expired.")
        return False  # The token has expired

    except jwt.InvalidTokenError:
        st.error("Invalid token.")
        return False  # Invalid token

# Function to show success message temporarily
def show_temporary_success_message(message, duration=3):
    placeholder = st.empty()  # Create a placeholder for the success message
    placeholder.success(message)  # Display the success message
    time.sleep(duration)  # Wait for 3 seconds
    placeholder.empty()
    
# Function to check if token exists and wait for value
def wait_for_token():
    token = local_storage_get("token")
    print("Hello token", token)
    if token:
        # And it still valid.
        if is_token_valid(token):
            st.session_state.token = token

# Ensure session state is initialized
if "token" not in st.session_state:
    st.session_state.token = None
    # Trigger token fetch from localStorage
    wait_for_token()

# Check if the token exists after fetching
if st.session_state.token:
    # User is authenticated, proceed with other logic
    show_temporary_success_message(f"You are authenticated.")

# Login form
if st.session_state.screenstate["login_page"]:
    # Authentication form
    with st.form("login_form"):
        st.write("Please log in to continue.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    # Simulate login and store token in localStorage
    if login_button:
        # Simulate token generation after login
        token = authenticate(username, password)
        if token:
            local_storage_set("token", token)  # Store token in localStorage
            st.session_state.token = token  # Store the token in session state
            st.session_state.screenstate["login_page"] = False  # Hide login page
            st.session_state.screenstate["generate_reports"] = True  # Show report generator
            st.session_state.screenstate["logout"] = True  # Show Logout button
            # st.success(f"Logged in successfully!")
            
            # Rerun the app to apply the state change
            st.rerun()

# Sidebar content with background color
if st.session_state.token:
    st.markdown(
        """
        <style>
        .css-1v3fvcr {
            background-color: #00B4D8 !important;
        }
        .css-1q8dd3e {
            color: #FFF !important;
        }
        .stButton>button {
            background-color: #FFF;
            color: #00B4D8;
        }
        </style>
        """, unsafe_allow_html=True
    )
    
    def section(label):
        button_html = f"""
            <div style="width: 100%;">
                <button style="width: 100%; background-color: #00B4D8; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 16px;">
                    {label}
                </button>
            </div>
            """
        return button_html
    
    # Sidebar for navigation
    with st.sidebar:

        st.write("## Main Tasks")
        if st.button("Report Generation"):
            st.session_state.screenstate["generate_reports"] = True
            st.session_state.screenstate["visual_qa"] = False
            st.session_state.screenstate["drift_detection"] = False
        
        if st.button("Visual Question Answering"):
            st.session_state.screenstate["generate_reports"] = False
            st.session_state.screenstate["visual_qa"] = True
            st.session_state.screenstate["drift_detection"] = False

        st.write("## Secondary Tasks")
        if st.button("Visualize Drift Detection"):
            st.session_state.screenstate["generate_reports"] = False
            st.session_state.screenstate["visual_qa"] = False
            st.session_state.screenstate["drift_detection"] = True

        # Logout button at the bottom
        st.markdown("<div style='position: fixed; bottom: 0; width: 100%;'>", unsafe_allow_html=True)
        if st.button("Logout"):
            local_storage_remove("token")
            st.session_state.token = None
            st.session_state.screenstate["login_page"] = True  # Show login page
            st.session_state.screenstate["generate_reports"] = False  # Hide report generator
            st.session_state.screenstate["logout"] = False  # Hide Logout button
            st.session_state.screenstate["visual_qa"] = False
            st.session_state.screenstate["drift_detection"] = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    

# Main content
st.title("Radiology Report Generator")

# Show the report generation page if logged in
if st.session_state.screenstate["generate_reports"]:
    st.write("You are now logged in and can generate reports.")
    # File uploader for the chest X-ray image
    uploaded_file = st.file_uploader("Choose a chest X-ray image...", type=["jpg", "jpeg", "png"])

    # Text input for the clinical indication
    indication = st.text_input("Clinical Indication", "Patient presenting with persistent cough, fever, and difficulty breathing. Evaluate for pneumonia.")

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Chest X-ray.', use_column_width=True)
        if st.button("Generate Report"):
            with st.spinner('Generating report...'):
                try:
                    img_str = uploaded_file.read()
                    response = requests.post(
                        "http://127.0.0.1:8000/generate_report/",
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        files={"file": ("image.jpg", img_str, uploaded_file.type)},
                        data={"indication": indication}
                    )
                    if response.status_code == 200:
                        data = response.json()
                        report = data.get("report", "No report generated.")
                        # Split the report into sections based on the keywords "Indication", "Finding", and "Impression"
                        if report:
                            indications = ""
                            findings = ""
                            impressions = ""

                            # Parse the report
                            if "indication" in report.lower():
                                indications = report.split("findings")[0].strip()
                                findings_impressions = report.split("findings")[1].strip()
                                if "impression" in findings_impressions.lower():
                                    findings = findings_impressions.split("impression")[0].strip()
                                    impressions = findings_impressions.split("impression")[1].strip()

                            # Display the formatted report
                            st.success("Report generated successfully!")
                            st.write(f"**Report**:\n")
                            
                            if indications:
                                st.markdown(f"**Indication**:\n{indications}")
                            
                            if findings:
                                st.markdown(f"**Finding**:\n{findings}")
                            
                            if impressions:
                                st.markdown(f"**Impression**:\n{impressions}")
                        # st.success("Report generated successfully!")
                    else:
                        st.error(f"Error generating the report. Status code: {response.status_code}")
                        st.write(response.text)  # Print the error details
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Visual Question Answering page
if st.session_state.screenstate["visual_qa"]:
    st.write("Visual Question Answering feature coming soon!")

# Drift Detection page
# if st.session_state.screenstate["drift_detection"]:
    
#     st.write("Drift Detection Visualization feature coming soon!")
# Drift Detection page
if st.session_state.screenstate["drift_detection"]:
    st.write("Drift Detection Visualization")

    # Call the FastAPI monitoring endpoint
    try:
        response = requests.get("http://127.0.0.1:8000/monitoring")  # URL for FastAPI monitoring route
        
        if response.status_code == 200:
            # Display the HTML content
            html_content = response.text

            st.components.v1.html(html_content, height=1000, scrolling=True)
        else:
            st.error(f"Failed to load drift detection report. Status code: {response.status_code}")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")






st.markdown(
    """
    <style>
    .sidebar .stButton > button {
        width: 100%;
        background-color: #00B4D8;  /* Custom background color */
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True
)

