

import os
import re
import json
import uuid  
import hashlib
import random
from datetime import datetime, timedelta 
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin 
from werkzeug.security import generate_password_hash, check_password_hash
from google import genai # FIX 1: Keep only the main module import
from google.api_core.exceptions import GoogleAPICallError as GeminiAPIError 
from flask_mail import Mail, Message 

# --- Gemini availability flag and Client Setup ---
GEMINI_API_KEY_DEV = "AIzaSyAO6B2rFk9VzjJ7uLUJH5-YYjAN4R0wByA" 
os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_DEV 

GEMINI_AVAILABLE = False
gemini_client = None

try:
    # FIX 2: Use the explicit Client constructor with the key
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
    GEMINI_AVAILABLE = True
except Exception as e:
    # This will now catch the error during direct initialization
    print(f"CRITICAL ERROR: Gemini Client Initialization Failed: {e}")
    GEMINI_AVAILABLE = False

# -----------------------------------------------------------------

# ... (Rest of the file remains the same) ...
# ----------------------------------

# ... (Rest of the file remains the same) ...
# ----------------------------------

# ---------- Configuration ----------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
DEFAULT_SQLITE = "sqlite:///" + DB_PATH

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# --- FLASK-MAIL CONFIGURATION ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587 
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

mail = Mail(app)
CORS(app) 
db = SQLAlchemy(app)


# --- UTILITY FUNCTIONS (Defined at the top) ---

def print_users():
    """Print all users for debugging."""
    with app.app_context():
        users = User.query.all()
        print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
        if not users: print("The 'users' table is currently empty.")
        print("------------------------------------------")

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_mobile(mobile):
    """Validate mobile number format (10 digits)"""
    pattern = r'^[6-9]\d{9}$' 
    return re.match(pattern, mobile) is not None

def validate_password_strength(password):
    """
    FIX: Temporarily simplifies password strength to length check only (for final testing).
    """
    if len(password) < 6: return "Password must be at least 6 characters long."
    return None 

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_reset_email(recipient_email, token, username):
    """Skips mail server connection and logs the link to the console for testing."""
    reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
    msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
    msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
    try:
        mail.send(msg)
        print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
        return True
    except Exception as e:
        print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
        print(f"Link (COPY THIS): {reset_link}")
        return True

def send_otp_sms(mobile, otp, username):
    """Send OTP via SMS (placeholder)."""
    print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
    return True 

def send_otp_email(recipient_email, otp, username):
    """Send OTP via email as fallback or alternative"""
    print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
    return True 
# ====================================================================


# ---------- Models (UPDATED WITH QUIZ SESSION) ----------
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
    email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
    mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
    password_hash = db.Column(db.String(200), nullable=False)
    
    reset_token_hash = db.Column(db.String(64), nullable=True) 
    reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)
    otp_verified = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat()}


# FIX: NEW MODEL FOR QUIZ HISTORY STORAGE
class QuizSession(db.Model):
    __tablename__ = "quiz_sessions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    
    results_json = db.Column(db.Text, nullable=False)
    
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "score": self.score,
            "total": self.total_questions,
            "topic": self.topic,
            "completed_at": self.completed_at.isoformat(),
            "details": json.loads(self.results_json)
        }
# -----------------------------------------------

# ---------- Ensure DB (Will now create QuizSession table) ----------
with app.app_context():
    db.create_all()

# ---------- Helper: AI quiz generation (Gemini) ----------
def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
    """
    Tries to call Google Gemini with a multi-type structured prompt.
    """
    difficulty_map = {
        "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
    }
    difficulty = difficulty_map.get(skill_level, "easy")

    if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
        try:
            prompt = (
                f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
                f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
                f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. "
                f"Ensure the output includes a balanced mix of: "
                f"1. Multiple Choice (type: 'mcq', answer: single option). "
                f"2. True/False (type: 'true_false', answer: 'True' or 'False'). "
                f"3. Fill-in-the-Blank (type: 'fill_blank', answer: single word/phrase). "
                f"4. Multiple Answer Select (type: 'multi_select', answer: comma-separated correct options)."
                f"The total number of questions must be {num_quizzes}."
            )
            response = gemini_client.models.generate_content(
                model='gemini-2.5-flash', contents=prompt, config={'response_mime_type': 'application/json', 'temperature': 0.7} 
            )
            content = response.text.strip()
            if content.startswith(('[', '{')):
                try: return {"quiz": json.loads(content)} 
                except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON (Parsing failed)."}, 500
            else: return {"error": "AI response was not valid quiz JSON (Bad format)."}, 500
        
        except GeminiAPIError as e:
            return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
        except Exception as e:
            return {"error": f"AI generation failed: {e}"}, 500
    else:
        return {"error": "Gemini client is not configured or API key is missing."}, 500


# ---------- ROUTES ----------

@app.route("/", methods=["GET"])
@cross_origin()
def welcome():
    return jsonify({"message": "Welcome to Smart Quizzer."}), 200

@app.route("/api/register", methods=["POST"])
@cross_origin()
def register():
    data = request.get_json() or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    password_confirm = data.get("password_confirm") or ""
    email = (data.get("email") or "").strip()
    mobile = (data.get("mobile") or "").strip()
    
    if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
    password_error = validate_password_strength(password)
    if password_error: return jsonify({"success": False, "message": password_error}), 400
    if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
    if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
    if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
    if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

    existing = User.query.filter(
        (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
    ).first()
    if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

    password_hash = generate_password_hash(password)
    user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


@app.route("/api/login", methods=["POST"])
@cross_origin()
def login():
    data = request.get_json() or {}
    identifier = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
    ).first()
    
    if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

    if check_password_hash(user.password_hash, password):
        return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
    else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


@app.route("/api/forgot_password", methods=["POST"])
@cross_origin()
def forgot_password():
    data = request.get_json() or {}
    identifier = (data.get("identifier") or "").strip()
    reset_method = data.get("method", "email") # Defaults to email method

    if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

    is_email = validate_email(identifier)
    is_mobile = validate_mobile(identifier)

    if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

    if is_email: user = User.query.filter_by(email=identifier).first()
    else: user = User.query.filter_by(mobile=identifier).first()

    if not user: 
        print(f"Reset requested for non-existent identifier: {identifier}")
        return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

    # Token and expiry logic is run regardless of method
    plain_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
    expiry = datetime.utcnow() + timedelta(hours=1)
    
    user.reset_token_hash = token_hash
    user.reset_token_expiry = expiry
    db.session.commit()

    # --- EMAIL PATH (Link Reset) ---
    if is_email or reset_method == "email":
        if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
        send_reset_email(user.email, plain_token, user.username)
        return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

    # --- MOBILE PATH (OTP Reset) ---
    else: 
        if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
        otp = generate_otp()
        user.otp_code = otp
        user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        user.otp_verified = False
        db.session.commit()

        send_otp_sms(user.mobile, otp, user.username)
        
        return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


@app.route("/api/verify_otp", methods=["POST"])
@cross_origin()
def verify_otp():
    data = request.get_json() or {}
    mobile = (data.get("mobile") or "").strip()
    otp = (data.get("otp") or "").strip()

    if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

    user = User.query.filter_by(mobile=mobile).first()

    if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
    if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
    if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

    user.otp_verified = True
    user.otp_code = None
    user.otp_expiry = None
    db.session.commit()

    temp_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
    user.reset_token_hash = token_hash 
    user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()

    return jsonify({
        "success": True, 
        "message": "OTP verified successfully.",
        "reset_token": temp_token
    }), 200


@app.route("/api/reset_password", methods=["POST"])
@cross_origin()
def reset_password():
    data = request.get_json() or {}
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
    password_error = validate_password_strength(new_password)
    if password_error: return jsonify({"success": False, "message": password_error}), 400

    received_hash = hashlib.sha256(token.encode()).hexdigest()
    user = User.query.filter_by(reset_token_hash=received_hash).first()

    if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
    if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

    user.password_hash = generate_password_hash(new_password)
    user.reset_token_hash = None
    user.reset_token_expiry = None
    user.otp_verified = False # Clear mobile verification flag
    db.session.commit()

    print(f"Password successfully reset for user: {user.username}")
    return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


@app.route("/api/topic-selection", methods=["POST"])
@cross_origin()
def topic_selection():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    skill_level = data.get("skill_level", "")
    choice = str(data.get("choice", "1"))
    subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
    num_quizzes = int(data.get("num_quizzes", 5))

    if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
        return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

    # CRITICAL FIX: Call the REAL AI generator (Gemini)
    quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

    # Check if the AI returned an error tuple (status 500)
    if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
        # This will now display the specific API key error on the frontend
        return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

    # Return the successful quiz data
    return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


@app.route("/api/history/<username>", methods=["GET"])
@cross_origin()
def get_quiz_history(username):
    """Fetches all quiz sessions for a specific user."""
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"success": False, "message": "User not found."}), 404
        
    # Query all sessions, ordered by most recent first
    sessions = QuizSession.query.filter_by(user_id=user.id).order_by(QuizSession.completed_at.desc()).all()
    
    # Return list of session dictionaries
    return jsonify([session.to_dict() for session in sessions]), 200


@app.route("/api/health", methods=["GET"])
@cross_origin()
def health():
    return jsonify({"status": "ok"}), 200


# ---------- Run ----------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print_users()


    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
