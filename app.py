import streamlit as st
import cv2
import os
import json
from PIL import Image
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="ATM Face Recognition System",
    page_icon="🏧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling
st.markdown("""
    <style>
    .title { font-size: 2.5em; color: #1f77b4; text-align: center; font-weight: bold; }
    .success { color: #28a745; font-weight: bold; }
    .error { color: #dc3545; font-weight: bold; }
    .info { color: #17a2b8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="title">🏧 ATM FACE RECOGNITION SYSTEM</div>', unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_id = None
    st.session_state.balance = 0.0
    st.session_state.pin = "1234"

# File paths
script_dir = os.path.dirname(os.path.abspath(__file__))
accounts_file = os.path.join(script_dir, 'accounts.json')
trainer_path = os.path.join(script_dir, 'trainer', 'trainer.yml')
cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')
dataset_dir = os.path.join(script_dir, 'dataset')

# Default accounts
DEFAULT_ACCOUNTS = {
    'Pranay': 1000.0,
    'User2': 500.0,
    'User3': 250.0,
}

# ==================== UTILITY FUNCTIONS ====================

def load_accounts():
    """Load accounts from JSON file"""
    if os.path.exists(accounts_file):
        try:
            with open(accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return DEFAULT_ACCOUNTS.copy()
    return DEFAULT_ACCOUNTS.copy()

def save_accounts(accounts):
    """Save accounts to JSON file"""
    try:
        with open(accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving accounts: {e}")
        return False

def load_face_model():
    """Load the trained face recognition model"""
    try:
        if not os.path.exists(trainer_path):
            return None, None, []
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(trainer_path)
        
        face_cascade = cv2.CascadeClassifier(cascade_path)
        if face_cascade.empty():
            return None, None, []
        
        # Get user IDs and names from dataset
        user_ids = set()
        for dirpath, _, files in os.walk(dataset_dir):
            for filename in files:
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    rel = os.path.relpath(dirpath, dataset_dir)
                    first_part = rel.split(os.sep)[0]
                    if first_part.isdigit():
                        user_ids.add(int(first_part))
        
        default_names = {0: 'User0', 1: 'Pranay', 2: 'User2', 3: 'User3'}
        if user_ids:
            max_id = max(user_ids)
            names = [''] * (max_id + 1)
            for uid in sorted(user_ids):
                names[uid] = default_names.get(uid, f'User{uid}')
        else:
            names = []
        
        return recognizer, face_cascade, names
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None, []

def recognize_face_from_image(image_array, recognizer, face_cascade, names):
    """Recognize face from image array"""
    try:
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 6, minSize=(100, 100))
        
        if len(faces) == 0:
            return None, None, "No face detected"
        
        for (x, y, w, h) in faces:
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            confidence_score = max(0, min(100, round(100 - confidence)))
            
            if confidence < 50 and confidence_score >= 75:
                if 0 <= id < len(names) and names[id]:
                    return names[id], id, f"Confidence: {confidence_score}%"
        
        return None, None, "Face not recognized"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# ==================== FACE RECOGNITION LOGIN ====================

def capture_with_opencv():
    """Capture face using OpenCV directly"""
    st.info("📷 OpenCV Camera Capture")
    
    recognizer, face_cascade, names = load_face_model()
    
    if recognizer is None or face_cascade is None:
        st.error("❌ Model not trained. Please run train_model.py first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎥 Start Camera & Capture Face"):
            try:
                cap = cv2.VideoCapture(0)
                
                if not cap.isOpened():
                    st.error("❌ Cannot access camera. Please check:")
                    st.write("1. Camera is connected and working")
                    st.write("2. No other app is using the camera")
                    st.write("3. Restart the application")
                    return
                
                st.info("⏳ Initializing camera... Please wait (5 seconds)")
                
                frame_count = 0
                captured_frame = None
                
                # Capture frames for 5 seconds
                progress_bar = st.progress(0)
                for i in range(150):  # 5 seconds at 30 FPS
                    ret, frame = cap.read()
                    
                    if not ret:
                        st.error("❌ Failed to read from camera")
                        break
                    
                    frame_count += 1
                    progress_bar.progress(min(i / 150, 0.99))
                    
                    # Capture the best centered frame
                    if i == 120:  # Get frame at 4 seconds
                        captured_frame = frame
                
                cap.release()
                progress_bar.progress(1.0)
                
                if captured_frame is not None:
                    st.success("✅ Photo captured!")
                    st.image(cv2.cvtColor(captured_frame, cv2.COLOR_BGR2RGB))
                    
                    username, user_id, message = recognize_face_from_image(captured_frame, recognizer, face_cascade, names)
                    
                    if username:
                        st.markdown(f'<p class="success">✅ Face recognized: {username}</p>', unsafe_allow_html=True)
                        
                        accounts = load_accounts()
                        if username in accounts:
                            st.session_state.authenticated = True
                            st.session_state.username = username
                            st.session_state.user_id = user_id
                            st.session_state.balance = accounts[username]
                            st.success("🔓 Login Successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(f"User {username} not found in accounts")
                    else:
                        st.markdown(f'<p class="error">❌ {message}</p>', unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to capture image")
                    
            except Exception as e:
                st.error(f"❌ Camera Error: {str(e)}")
    
    with col2:
        st.write("### Available Users")
        for name in sorted(set(names) - {''}):
            st.write(f"👤 {name}")

def face_login():
    """Face recognition login section"""
    st.subheader("👤 Face Recognition Login")
    
    recognizer, face_cascade, names = load_face_model()
    
    if recognizer is None or face_cascade is None:
        st.error("❌ Model not trained. Please run train_model.py first.")
        return
    
    # Show available users
    st.write("### Available Users")
    for name in sorted(set(names) - {''}):
        st.write(f"👤 {name}")
    
    st.divider()
    
    # Login method selection
    login_method = st.radio(
        "Choose login method:",
        ["📷 Camera Capture (OpenCV)", "📤 Upload Image File"]
    )
    
    if login_method == "📷 Camera Capture (OpenCV)":
        capture_with_opencv()
    
    else:  # Upload Image File
        st.info("📤 Upload a photo for face recognition")
        uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                st.image(image, caption="Uploaded Image")
                
                username, user_id, message = recognize_face_from_image(image_array, recognizer, face_cascade, names)
                
                if username:
                    st.markdown(f'<p class="success">✅ Face recognized: {username}</p>', unsafe_allow_html=True)
                    
                    accounts = load_accounts()
                    if username in accounts:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_id = user_id
                        st.session_state.balance = accounts[username]
                        st.success("🔓 Login Successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error(f"User {username} not found in accounts")
                else:
                    st.markdown(f'<p class="error">❌ {message}</p>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")

# ==================== ATM OPERATIONS ====================

def atm_operations():
    """ATM operations interface"""
    st.subheader(f"💰 Welcome, {st.session_state.username}!")
    
    # Display balance
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Balance", f"${st.session_state.balance:.2f}", delta=None)
    
    # Load accounts
    accounts = load_accounts()
    
    # ATM Menu
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Check Balance", "Deposit", "Withdraw", "Change PIN", "Logout"])
    
    with tab1:
        st.write(f"### Your Balance: ${st.session_state.balance:.2f}")
        st.success("Balance check successful")
    
    with tab2:
        st.write("### 💵 Deposit Money")
        deposit_amount = st.number_input("Enter deposit amount ($)", min_value=0.01, step=0.01, key="deposit")
        
        if st.button("Deposit", key="btn_deposit"):
            if deposit_amount > 0:
                st.session_state.balance += deposit_amount
                accounts[st.session_state.username] = st.session_state.balance
                if save_accounts(accounts):
                    st.success(f"✅ Deposited ${deposit_amount:.2f}\nNew Balance: ${st.session_state.balance:.2f}")
                else:
                    st.error("Failed to save transaction")
            else:
                st.error("Please enter a positive amount")
    
    with tab3:
        st.write("### 💸 Withdraw Money")
        withdraw_amount = st.number_input("Enter withdrawal amount ($)", min_value=0.01, step=0.01, key="withdraw")
        
        if st.button("Withdraw", key="btn_withdraw"):
            if withdraw_amount > 0:
                if withdraw_amount <= st.session_state.balance:
                    st.session_state.balance -= withdraw_amount
                    accounts[st.session_state.username] = st.session_state.balance
                    if save_accounts(accounts):
                        st.success(f"✅ Withdrawn ${withdraw_amount:.2f}\n📄 Please collect your cash\nRemaining Balance: ${st.session_state.balance:.2f}")
                    else:
                        st.error("Failed to save transaction")
                else:
                    st.error(f"❌ Insufficient balance. Available: ${st.session_state.balance:.2f}")
            else:
                st.error("Please enter a positive amount")
    
    with tab4:
        st.write("### 🔐 Change PIN")
        new_pin = st.text_input("Enter new PIN (4+ digits)", type="password", key="new_pin")
        
        if st.button("Change PIN", key="btn_pin"):
            if len(new_pin) >= 4 and new_pin.isdigit():
                st.session_state.pin = new_pin
                st.success("✅ PIN changed successfully")
            else:
                st.error("❌ PIN must be at least 4 digits")
    
    with tab5:
        st.warning("⚠️ Are you sure you want to logout?")
        if st.button("Logout", key="btn_logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.balance = 0.0
            st.success("Logged out successfully")
            st.rerun()

# ==================== MAIN APP ====================

def main():
    if not st.session_state.authenticated:
        face_login()
    else:
        atm_operations()

if __name__ == "__main__":
    main()
