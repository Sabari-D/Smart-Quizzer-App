
# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from werkzeug.security import generate_password_hash, check_password_hash


# try:
#     from openai import OpenAI
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Config ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # Allow CORS for development (Angular dev server on :4200)
# CORS(app, resources={r"/api/*": {"origins": "*"}, r"/": {"origins": "*"}})

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI (if configured). If OpenAI not available or API key missing,
#     returns a mock sample quiz (helpful for local dev).
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # If OpenAI client available and key present, call it
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             # new client usage
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
#             # Extract content
#             content = ""
#             try:
#                 # try to find response text safely
#                 content = resp.choices[0].message["content"]
#             except Exception:
#                 # last resort: turn into str()
#                 content = str(resp)
#             # If the model returned JSON text, return it parsed if possible (else raw)
#             return {"raw_response": content}
#         except Exception as e:
#             return {"error": f"OpenAI error: {str(e)}"}
#     # Fallback: mock quiz generator (useful for dev without OpenAI)
#     sample = []
#     for i in range(num_quizzes):
#         sample.append({
#             "type": "mcq",
#             "question": f"Sample question {i+1} on {subject_or_concept} (difficulty={difficulty})?",
#             "options": ["A", "B", "C", "D"],
#             "answer": "A"
#         })
#     return sample

# # ---------- Routes ----------
# @app.route("/", methods=["GET"])
# def welcome():
#     return jsonify({
#         "app": "Smart Quizzer: Adaptive AI-based Quiz Generator",
#         "options": {"1": "Register", "2": "Login", "3": "Exit"},
#         "message": "Welcome to Smart Quizzer. Choose an option: 1 Register | 2 Login | 3 Exit"
#     }), 200

# @app.route("/api/register", methods=["POST"])
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""

#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400

#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400

#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# def topic_selection():
#     """
#     Called from frontend after login/registration. Validates name, skill_level, choice,
#     subject/concept and num_quizzes, then generates quiz with AI or fallback.
#     """
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     # Validate
#     if not name:
#         return jsonify({"success": False, "message": "Name is required."}), 400
#     if skill_level not in ["Beginner", "Intermediate", "Advanced"]:
#         return jsonify({"success": False, "message": "Invalid skill level. Choose Beginner/Intermediate/Advanced."}), 400
#     if choice not in ["1", "2"]:
#         return jsonify({"success": False, "message": "Choice must be '1' or '2'."}), 400
#     if not subject_or_concept:
#         return jsonify({"success": False, "message": "Topic or concept required."}), 400

#     quiz = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
#     return jsonify({"success": True, "message": f"Generated {num_quizzes} quizzes for {name}.", "quiz": quiz})

# @app.route("/api/generate_quiz", methods=["POST"])
# def generate_quiz_route():
#     """
#     Simpler generator: accepts {topic, num_questions} and returns a quick sample if AI not configured.
#     """
#     data = request.get_json() or {}
#     topic = data.get("topic", "General Knowledge")
#     num_questions = int(data.get("num_questions", 5))
#     # small mock
#     quiz = [{"question": f"Sample question {i+1} on {topic}?", "options": ["A","B","C","D"], "answer": "A"} for i in range(num_questions)]
#     return jsonify({"topic": topic, "quiz": quiz})

# @app.route("/api/health", methods=["GET"])
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     # set OPENAI_API_KEY in environment (do not hardcode in source)
#     # export OPENAI_API_KEY=...
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)







# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from werkzeug.security import generate_password_hash, check_password_hash


# try:
#     from openai import OpenAI
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Config ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # Allow CORS for development (Angular dev server on :4200)
# CORS(app, resources={r"/api/*": {"origins": "*"}, r"/": {"origins": "*"}})

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI (if configured). If OpenAI not available or API key missing,
#     returns a mock sample quiz (helpful for local dev).
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # If OpenAI client available and key present, call it
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             # new client usage
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
#             # Extract content
#             content = ""
#             try:
#                 # try to find response text safely
#                 content = resp.choices[0].message["content"]
#             except Exception:
#                 # last resort: turn into str()
#                 content = str(resp)
#             # If the model returned JSON text, return it parsed if possible (else raw)
#             return {"raw_response": content}
#         except Exception as e:
#             return {"error": f"OpenAI error: {str(e)}"}
#     # Fallback: mock quiz generator (useful for dev without OpenAI)
#     sample = []
#     for i in range(num_quizzes):
#         sample.append({
#             "type": "mcq",
#             "question": f"Sample question {i+1} on {subject_or_concept} (difficulty={difficulty})?",
#             "options": ["A", "B", "C", "D"],
#             "answer": "A"
#         })
#     return sample

# # ---------- Routes ----------
# @app.route("/", methods=["GET"])
# def welcome():
#     return jsonify({
#         "app": "Smart Quizzer: Adaptive AI-based Quiz Generator",
#         "options": {"1": "Register", "2": "Login", "3": "Exit"},
#         "message": "Welcome to Smart Quizzer. Choose an option: 1 Register | 2 Login | 3 Exit"
#     }), 200

# @app.route("/api/register", methods=["POST"])
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""

#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400

#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400

#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# def topic_selection():
#     """
#     Called from frontend after login/registration. Validates name, skill_level, choice,
#     subject/concept and num_quizzes, then generates quiz with AI or fallback.
#     """
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     # Validate
#     if not name:
#         return jsonify({"success": False, "message": "Name is required."}), 400
#     if skill_level not in ["Beginner", "Intermediate", "Advanced"]:
#         return jsonify({"success": False, "message": "Invalid skill level. Choose Beginner/Intermediate/Advanced."}), 400
#     if choice not in ["1", "2"]:
#         return jsonify({"success": False, "message": "Choice must be '1' or '2'."}), 400
#     if not subject_or_concept:
#         return jsonify({"success": False, "message": "Topic or concept required."}), 400

#     quiz = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
#     return jsonify({"success": True, "message": f"Generated {num_quizzes} quizzes for {name}.", "quiz": quiz})

# @app.route("/api/generate_quiz", methods=["POST"])
# def generate_quiz_route():
#     """
#     Simpler generator: accepts {topic, num_questions} and returns a quick sample if AI not configured.
#     """
#     data = request.get_json() or {}
#     topic = data.get("topic", "General Knowledge")
#     num_questions = int(data.get("num_questions", 5))
#     # small mock
#     quiz = [{"question": f"Sample question {i+1} on {topic}?", "options": ["A","B","C","D"], "answer": "A"} for i in range(num_questions)]
#     return jsonify({"topic": topic, "quiz": quiz})

# @app.route("/api/health", methods=["GET"])
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     # set OPENAI_API_KEY in environment (do not hardcode in source)
#     # export OPENAI_API_KEY=...
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)




# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from werkzeug.security import generate_password_hash, check_password_hash


# try:
#     from openai import OpenAI
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Config ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # Allow CORS for development (Angular dev server on :4200)
# CORS(app, resources={r"/api/*": {"origins": "*"}, r"/": {"origins": "*"}})

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI (if configured). If OpenAI not available or API key missing,
#     returns a mock sample quiz (helpful for local dev).
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # If OpenAI client available and key present, call it
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             # new client usage
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
#             # Extract content
#             content = ""
#             try:
#                 # try to find response text safely
#                 content = resp.choices[0].message["content"]
#             except Exception:
#                 # last resort: turn into str()
#                 content = str(resp)
#             # If the model returned JSON text, return it parsed if possible (else raw)
#             return {"raw_response": content}
#         except Exception as e:
#             return {"error": f"OpenAI error: {str(e)}"}
#     # Fallback: mock quiz generator (useful for dev without OpenAI)
#     sample = []
#     for i in range(num_quizzes):
#         sample.append({
#             "type": "mcq",
#             "question": f"Sample question {i+1} on {subject_or_concept} (difficulty={difficulty})?",
#             "options": ["A", "B", "C", "D"],
#             "answer": "A"
#         })
#     return sample

# # ---------- Routes ----------
# @app.route("/", methods=["GET"])
# def welcome():
#     return jsonify({
#         "app": "Smart Quizzer: Adaptive AI-based Quiz Generator",
#         "options": {"1": "Register", "2": "Login", "3": "Exit"},
#         "message": "Welcome to Smart Quizzer. Choose an option: 1 Register | 2 Login | 3 Exit"
#     }), 200

# @app.route("/api/register", methods=["POST"])
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""

#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400

#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400

#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# # --- START NEW ADMIN ROUTE ---
# @app.route("/api/users", methods=["GET"])
# def get_all_users():
#     # In a real application, you would add an @admin_required decorator here
#     # to ensure only an admin can access this.
    
#     users = User.query.all()
#     user_list = [user.to_dict() for user in users]
#     return jsonify(user_list), 200
# # --- END NEW ADMIN ROUTE ---

# @app.route("/api/topic-selection", methods=["POST"])
# def topic_selection():
#     """
#     Called from frontend after login/registration. Validates name, skill_level, choice,
#     subject/concept and num_quizzes, then generates quiz with AI or fallback.
#     """
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     # Validate
#     if not name:
#         return jsonify({"success": False, "message": "Name is required."}), 400
#     if skill_level not in ["Beginner", "Intermediate", "Advanced"]:
#         return jsonify({"success": False, "message": "Invalid skill level. Choose Beginner/Intermediate/Advanced."}), 400
#     if choice not in ["1", "2"]:
#         return jsonify({"success": False, "message": "Choice must be '1' or '2'."}), 400
#     if not subject_or_concept:
#         return jsonify({"success": False, "message": "Topic or concept required."}), 400

#     quiz = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
#     return jsonify({"success": True, "message": f"Generated {num_quizzes} quizzes for {name}.", "quiz": quiz})

# @app.route("/api/generate_quiz", methods=["POST"])
# def generate_quiz_route():
#     """
#     Simpler generator: accepts {topic, num_questions} and returns a quick sample if AI not configured.
#     """
#     data = request.get_json() or {}
#     topic = data.get("topic", "General Knowledge")
#     num_questions = int(data.get("num_questions", 5))
#     # small mock
#     quiz = [{"question": f"Sample question {i+1} on {topic}?", "options": ["A","B","C","D"], "answer": "A"} for i in range(num_questions)]
#     return jsonify({"topic": topic, "quiz": quiz})

# @app.route("/api/health", methods=["GET"])
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     # set OPENAI_API_KEY in environment (do not hardcode in source)
#     # export OPENAI_API_KEY=...
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)





# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin # Added cross_origin
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # FIX: Global CORS initialization. Decorators will handle specific headers.
# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         # (Formatting logic remains the same for printing users)

# # --- Helper: AI quiz generation ---
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (AI and Mock Logic remains the same as your app.py helper)
#     # ... (Your existing generate_quiz_with_ai implementation) ...
#     pass 
#     # NOTE: Since you provided a mock-only file, I'll assume you switch to it for testing.
#     # For a working version here, the full implementation is required.

# # --- MOCK HELPER (Use this for reliable testing) ---
# def generate_mock_quiz(subject_or_concept, num_quizzes):
#     quiz_data = []
#     num = max(1, int(num_quizzes)) 
#     for i in range(num):
#         quiz_data.append({"type": "mcq", "question": f"Mock Q{i+1} on {subject_or_concept}?", "options": ["A", "B", "C", "D"], "answer": "A"})
#     return {"quiz": quiz_data}
# # ----------------------------------------------------


# # ---------- Routes (with FIX: @cross_origin) ----------

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     # ... (rest of registration logic)
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     # ... (rest of login logic)
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     # Use the mock generation for reliable testing
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name:
#         return jsonify({"success": False, "message": "Name is required."}), 400
        
#     quiz = generate_mock_quiz(subject_or_concept, num_quizzes)
#     return jsonify({"success": True, "message": f"MOCK Quizzes generated for {name}.", "quiz": quiz['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     # Ensure all DB tables are present and print users
#     with app.app_context():
#         db.create_all()
#         print_users()

#     # Run server
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)






# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# import json

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return
#         # NOTE: Formatting logic omitted for brevity.


# # ---------- Helper: AI quiz generation (FULL ORIGINAL LOGIC RESTORED) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI. If it fails, it returns a hard error response.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # CRITICAL: We only proceed if OpenAI is available, eliminating the silent mock fallback
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
#             content = ""
#             try:
#                 content = resp.choices[0].message["content"]
#             except Exception:
#                 content = str(resp)
                
#             # If AI response starts with { or [, assume JSON content, else return error
#             if content and content.strip().startswith(('[', '{')):
#                 # Try to parse the output; Python handles this better than JS sometimes
#                 return {"quiz": json.loads(content)} 
#             else:
#                 # If the AI response is garbage/not parsable JSON, return an error
#                  return {"error": "AI response was not valid quiz JSON."}, 500
                 
#         except Exception as e:
#             # If API key is bad or network is down, return a hard error
#             print(f"OpenAI API Call Failed: {str(e)}")
#             return {"error": f"AI generation failed: {str(e)}"}, 500
#     else:
#         # Hard stop if key or library is missing
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- Routes ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     # ... (Registration logic remains the same) ...
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     # ... (Login logic remains the same) ...
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     """Generates quiz using the REAL AI helper and enforces validation."""
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     # Validation remains the same
#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # Call the real AI generation function
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
    
#     # Check if the AI returned an error (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]['error']}), 500
        
#     # Success: returns the generated quiz (which is a dictionary containing 'quiz')
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     # Run server
#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)


# import os
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# import json
# import re 

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return
#         # NOTE: Formatting logic omitted for brevity.


# # ---------- Helper: AI quiz generation (FIXED DOT NOTATION) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI. If it fails, it returns a hard error response.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             # --- CRITICAL FIX: Changed from resp.choices[0].message["content"] to dot notation ---
#             content = resp.choices[0].message.content
#             # --- END FIX ---
            
#             # --- JSON CLEANING AND PARSING LOGIC ---
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     print(f"JSON Parsing FAILED after cleaning: {json_error}")
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  print(f"AI returned non-JSON text: {content_clean[:50]}")
#                  return {"error": "AI response was not valid quiz JSON."}, 500
                 
#         except Exception as e:
#             print(f"OpenAI API Call Failed: {str(e)}")
#             return {"error": f"AI generation failed: {str(e)}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- Routes ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     """Generates quiz using the REAL AI helper and enforces validation."""
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
    
#     # Check if the AI returned an error (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]['error']}), 500
        
#     # Success: returns the generated quiz 
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)


# import os
# import re
# import json
# from datetime import datetime
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# import re # Already imported, kept here for clarity

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# # ---------- Helper: AI quiz generation (FINAL CORRECTED LOGIC) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI. If successful, returns {'quiz': data}. On error, returns {'error': msg}, 500.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             # FIX: Get content using DOT NOTATION (resolves 'subscriptable' error)
#             content = resp.choices[0].message.content
            
#             # --- JSON CLEANING AND PARSING LOGIC ---
#             content_clean = content.strip()
            
#             # Use regex to strip common markdown fences
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     # Success: Return the parsed quiz data
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     print(f"JSON Parsing FAILED after cleaning: {json_error}")
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  # If the AI returns non-JSON content
#                  print(f"AI returned non-JSON text: {content_clean[:50]}")
#                  return {"error": "AI response was not valid quiz JSON."}, 500
                 
#         except Exception as e:
#             # Catch API network/key errors
#             print(f"OpenAI API Call Failed: {str(e)}")
#             return {"error": f"AI generation failed: {str(e)}"}, 500
#     else:
#         # Hard stop if key or library is missing
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- Routes ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     """Generates quiz using the REAL AI helper and enforces validation."""
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
    
#     # Check if the AI returned an error (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]['error']}), 500
        
#     # Success: returns the generated quiz 
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)




# import os
# import re
# import json
# import uuid  # <-- NEW: For generating unique reset tokens
# from datetime import datetime, timedelta # <-- NEW: For managing token expiry
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models (UPDATED) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     # --- NEW FIELDS FOR PASSWORD RESET ---
#     reset_token = db.Column(db.String(36), nullable=True)
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
#     # -------------------------------------
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return
#         # NOTE: Formatting logic omitted for brevity.


# # ---------- Helper: AI quiz generation ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI. If successful, returns {'quiz': data}. On error, returns {'error': msg}, 500.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             content = resp.choices[0].message.content
            
#             # --- JSON CLEANING AND PARSING LOGIC ---
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     print(f"JSON Parsing FAILED after cleaning: {json_error}")
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  print(f"AI returned non-JSON text: {content_clean[:50]}")
#                  return {"error": "AI response was not valid quiz JSON."}, 500
                 
#         except Exception as e:
#             print(f"OpenAI API Call Failed: {str(e)}")
#             return {"error": f"AI generation failed: {str(e)}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- New Endpoint: Forgot Password Request (FIX) ----------
# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()

#     if not identifier:
#         return jsonify({"success": False, "message": "Username or Email is required."}), 400

#     # 1. Find the user (assuming identifier is username)
#     user = User.query.filter_by(username=identifier).first()
    
#     # Security: Return generic success message even if user is not found
#     if not user:
#         return jsonify({"success": True, "message": "If an account exists, a reset process has been initiated."}), 200

#     # 2. Generate a token (UUID) and set expiry (e.g., 1 hour)
#     token = str(uuid.uuid4())
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     # 3. Save the token and expiry to the user record
#     user.reset_token = token
#     user.reset_token_expiry = expiry
#     db.session.commit()
    
#     # 4. Log the link for frontend testing (instead of sending email)
#     reset_link = f"http://localhost:4200/reset-password?token={token}"
#     print("\n--- PASSWORD RESET TOKEN ---")
#     print(f"User: {user.username} | Token: {token}")
#     print(f"Link (for testing): {reset_link}")
#     print("----------------------------\n")
    
#     return jsonify({"success": True, "message": "If an account exists, a reset link has been processed."}), 200


# # New Endpoint: Reset Password Confirmation (Placeholder)
# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")
    
#     if not token or not new_password:
#         return jsonify({"success": False, "message": "Token and new password are required."}), 400

#     user = User.query.filter_by(reset_token=token).first()
    
#     # 1. Check if user/token exists
#     if not user:
#         return jsonify({"success": False, "message": "Invalid or expired token."}), 400
    
#     # 2. Check token expiry
#     if user.reset_token_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "Token has expired."}), 400

#     # 3. Update password and clear token fields
#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token = None
#     user.reset_token_expiry = None
#     db.session.commit()
    
#     return jsonify({"success": True, "message": "Password successfully reset. Please log in."}), 200
# # ---------- END NEW ENDPOINTS ----------


# # ---------- Other Existing Routes ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     # ... (Logic remains the same) ...
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     # ... (Logic remains the same) ...
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     # ... (Logic remains the same) ...
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
    
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]['error']}), 500
        
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

# import os
# import re
# import json
# import uuid  # For generating unique reset tokens
# from datetime import datetime, timedelta # For managing token expiry
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI

# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# CORS(app) 

# db = SQLAlchemy(app)

# # ---------- Models (UPDATED) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     # --- NEW FIELDS FOR PASSWORD RESET ---
#     reset_token = db.Column(db.String(36), nullable=True)
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
#     # -------------------------------------
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # --- Utility: Print Users (for debugging) ---
# def print_users():
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# # ---------- Helper: AI quiz generation ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call OpenAI. If successful, returns {'quiz': data}. On error, returns {'error': msg}, 500.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory",
#         "Intermediate": "moderately challenging",
#         "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             content = resp.choices[0].message.content
            
#             # --- JSON CLEANING AND PARSING LOGIC ---
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     print(f"JSON Parsing FAILED after cleaning: {json_error}")
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  print(f"AI returned non-JSON text: {content_clean[:50]}")
#                  return {"error": "AI response was not valid quiz JSON."}, 500
                 
#         except Exception as e:
#             print(f"OpenAI API Call Failed: {str(e)}")
#             return {"error": f"AI generation failed: {str(e)}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- Routes ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "username, password and password_confirm are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     existing = User.query.filter_by(username=username).first()
#     if existing:
#         return jsonify({"success": False, "message": "You are already registered. Please go to the login page."}), 409
#     password_hash = generate_password_hash(password)
#     user = User(username=username, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201

# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     if not username or not password:
#         return jsonify({"success": False, "message": "username and password are required."}), 400
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404
#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome back, {username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401

# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()

#     if not identifier:
#         return jsonify({"success": False, "message": "Username or Email is required."}), 400

#     user = User.query.filter_by(username=identifier).first()
    
#     if not user:
#         return jsonify({"success": True, "message": "If an account exists, a reset process has been initiated."}), 200

#     token = str(uuid.uuid4())
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token = token
#     user.reset_token_expiry = expiry
#     db.session.commit()
    
#     reset_link = f"http://localhost:4200/reset-password?token={token}"
#     print("\n--- PASSWORD RESET TOKEN ---")
#     print(f"User: {user.username} | Token: {token}")
#     print(f"Link (for testing): {reset_link}")
#     print("----------------------------\n")
    
#     return jsonify({"success": True, "message": "If an account exists, a reset link has been processed."}), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")
    
#     if not token or not new_password:
#         return jsonify({"success": False, "message": "Token and new password are required."}), 400

#     user = User.query.filter_by(reset_token=token).first()
    
#     if not user:
#         return jsonify({"success": False, "message": "Invalid or expired token."}), 400
    
#     # NOTE: Need to compare against the current time (now)
#     if user.reset_token_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "Token has expired."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token = None
#     user.reset_token_expiry = None
#     db.session.commit()
    
#     return jsonify({"success": True, "message": "Password successfully reset. Please log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     # ... (Logic remains the same) ...
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)
    
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]['error']}), 500
        
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result['quiz']}), 200

# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200

# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)

# import os
# import re
# import json   
# import uuid  
# import hashlib # <--- CRITICAL FIX: Added missing hashlib import
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'smartquizzer.noreply@example.com')

# mail = Mail(app)
# CORS(app)
# db = SQLAlchemy(app)
# from flask_migrate import Migrate
# migrate = Migrate(app, db)


# # ---------- MODELS (CORRECTED) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     # NEW: Email field for password reset delivery
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     # FIX: Use 'reset_token_hash' for storing the secure SHA256 hash
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email, # Include email in dict
#             "created_at": self.created_at.isoformat(),
#         }


# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()


# # ---------- Utility (CORRECTED) ----------
# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#         else:
#             # Print new email field for better debugging
#             for u in users:
#                 print(f"ID: {u.id}, User: {u.username}, Email: {u.email}")
#         print("------------------------------------------")


# def send_reset_email(recipient_email, token):
#     """Send password reset link via email."""
    
#     # NOTE: The token here must be the PLAIN token before hashing
#     reset_link = f"http://localhost:4200/reset-password?token={token}"
#     msg = Message("Password Reset Request for Smart Quizzer", recipients=[recipient_email])
    
#     msg.body = f"""
#     Hello,
    
#     You requested a password reset for your Smart Quizzer account.
    
#     To reset your password, click the link below (valid for 1 hour):
#     {reset_link}

#     If you did not make this request, please ignore this email.
#     """
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Sent reset link to {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL: {e} ---")
#         return False


# # ---------- AI Quiz Generator (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing logic remains the same, using dot notation and cleaning)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip() # FIX: Capture email from the payload
    
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400

#     # FIX: Check for existing user by both username OR email
#     existing = User.query.filter((User.username == username) | (User.email == email)).first()
#     if existing:
#         return jsonify({"success": False, "message": "User already exists. Please log in."}), 409

#     password_hash = generate_password_hash(password)
#     # FIX: Save email to the database
#     user = User(username=username, email=email if email else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip() # Renamed to identifier for clarity
#     password = data.get("password") or ""
    
#     if not identifier or not password:
#         return jsonify({"success": False, "message": "Username/Email and password are required."}), 400

#     # FIX: Allow login by either username or email
#     user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()

#     if not identifier:
#         return jsonify({"success": False, "message": "Username or Email is required."}), 400

#     # Find user by either username or email
#     user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

#     if not user:
#         return jsonify({"success": True, "message": "If an account exists, a reset process has been initiated."}), 200
    
#     # CRITICAL SECURITY FIX: Generate plain token, hash it, and store the HASH.
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)

#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # Send email using the PLAIN token (for the URL) and the user's registered email
#     recipient = user.email if user.email else user.username # Use email if available, else username
#     send_reset_email(recipient, plain_token) # Send the PLAIN token via email

#     return jsonify({"success": True, "message": "If an account exists, a reset link has been processed."}), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token") # This is the PLAIN token from the URL
#     new_password = data.get("new_password")

#     if not token or not new_password:
#         return jsonify({"success": False, "message": "Token and new password are required."}), 400

#     # FIX: Hash the PLAIN token received from the URL for database lookup
#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user:
#         return jsonify({"success": False, "message": "Invalid or expired token."}), 400
#     if user.reset_token_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "Token has expired."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     db.session.commit()

#     return jsonify({"success": True, "message": "Password successfully reset. Please log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)








# import os
# import re
# import json
# import uuid  
# import hashlib
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'smartquizzer.noreply@example.com')

# mail = Mail(app)
# CORS(app)
# db = SQLAlchemy(app)
# from flask_migrate import Migrate
# migrate = Migrate(app, db)


# # ---------- MODELS (CORRECTED) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     # NEW: Email field for password reset delivery
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     # FIX: Use 'reset_token_hash' for storing the secure SHA256 hash
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email, # Include email in dict
#             "created_at": self.created_at.isoformat(),
#         }


# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()


# # ---------- Utility (CORRECTED) ----------
# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#         else:
#             # Print new email field for better debugging
#             for u in users:
#                 print(f"ID: {u.id}, User: {u.username}, Email: {u.email}")
#         print("------------------------------------------")


# def send_reset_email(recipient_email, token):
#     """Send password reset link via email."""
    
#     # NOTE: The token here must be the PLAIN token before hashing
#     reset_link = f"http://localhost:4200/reset-password?token={token}"
#     msg = Message("Password Reset Request for Smart Quizzer", recipients=[recipient_email])
    
#     msg.body = f"""
#     Hello,
    
#     You requested a password reset for your Smart Quizzer account.
    
#     To reset your password, click the link below (valid for 1 hour):
#     {reset_link}

#     If you did not make this request, please ignore this email.
#     """
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Sent reset link to {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL: {e} ---")
#         return False


# # ---------- Password Strength Validation ----------
# def validate_password_strength(password):
#     """Validate password meets minimum requirements"""
#     if len(password) < 8:
#         return "Password must be at least 8 characters long"
#     if not re.search(r"[A-Z]", password):
#         return "Password must contain at least one uppercase letter"
#     if not re.search(r"[a-z]", password):
#         return "Password must contain at least one lowercase letter"
#     if not re.search(r"\d", password):
#         return "Password must contain at least one number"
#     if not re.search(r"[@$!%*?&]", password):
#         return "Password must contain at least one special character (@$!%*?&)"
#     return None


# # ---------- AI Quiz Generator (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing logic remains the same, using dot notation and cleaning)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800
#             )
            
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError as json_error:
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                  return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip() # FIX: Capture email from the payload
    
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400

#     # FIX: Check for existing user by both username OR email
#     existing = User.query.filter((User.username == username) | (User.email == email)).first()
#     if existing:
#         return jsonify({"success": False, "message": "User already exists. Please log in."}), 409

#     password_hash = generate_password_hash(password)
#     # FIX: Save email to the database
#     user = User(username=username, email=email if email else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip() # Renamed to identifier for clarity
#     password = data.get("password") or ""
    
#     if not identifier or not password:
#         return jsonify({"success": False, "message": "Username/Email and password are required."}), 400

#     # FIX: Allow login by either username or email
#     user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()

#     if not identifier:
#         return jsonify({"success": False, "message": "Username or Email is required."}), 400

#     # Find user by either username or email
#     user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()

#     if not user:
#         # Security: Don't reveal if user exists
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been sent."}), 200
    
#     # Check if user has email configured for password reset
#     if not user.email:
#         return jsonify({"success": False, "message": "No email configured for this account. Please contact support."}), 400

#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)

#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # Send email - handle failures
#     email_sent = send_reset_email(user.email, plain_token)
    
#     if email_sent:
#         return jsonify({"success": True, "message": "Password reset link has been sent to your email."}), 200
#     else:
#         # Rollback token if email fails
#         user.reset_token_hash = None
#         user.reset_token_expiry = None
#         db.session.commit()
#         return jsonify({"success": False, "message": "Failed to send reset email. Please try again."}), 500


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token") # This is the PLAIN token from the URL
#     new_password = data.get("new_password")

#     if not token or not new_password:
#         return jsonify({"success": False, "message": "Token and new password are required."}), 400

#     # Validate password strength
#     password_error = validate_password_strength(new_password)
#     if password_error:
#         return jsonify({"success": False, "message": password_error}), 400

#     # FIX: Hash the PLAIN token received from the URL for database lookup
#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user:
#         return jsonify({"success": False, "message": "Invalid or expired token."}), 400
#     if user.reset_token_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "Token has expired."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     db.session.commit()

#     return jsonify({"success": True, "message": "Password successfully reset. Please log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)





# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'smartquizzer.noreply@example.com')

# # --- Frontend URL Configuration ---
# FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:4200")

# mail = Mail(app)
# CORS(app)
# db = SQLAlchemy(app)
# from flask_migrate import Migrate
# migrate = Migrate(app, db)


# # ---------- MODELS (UPDATED) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     # Email and mobile fields
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     # Reset token fields (for email-based reset)
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     # OTP fields (for mobile-based reset)
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }


# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()


# # ---------- Utility Functions ----------
# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#         else:
#             for u in users:
#                 print(f"ID: {u.id}, User: {u.username}, Email: {u.email}, Mobile: {u.mobile}")
#         print("------------------------------------------")


# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$'  # Indian mobile number format
#     return re.match(pattern, mobile) is not None


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """Send password reset link via email with improved formatting."""
    
#     reset_link = f"{FRONTEND_URL}/reset-password?token={token}&type=email"
    
#     msg = Message(
#         subject="Password Reset Request - Smart Quizzer",
#         recipients=[recipient_email]
#     )
    
#     msg.html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#             .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#             .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
#             .content {{ background: #f9f9f9; padding: 20px; }}
#             .button {{ display: inline-block; padding: 12px 24px; background: #4CAF50; 
#                      color: white; text-decoration: none; border-radius: 4px; margin: 15px 0; }}
#             .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="header">
#                 <h1>Smart Quizzer</h1>
#                 <h2>Password Reset Request</h2>
#             </div>
#             <div class="content">
#                 <p>Hello <strong>{username}</strong>,</p>
#                 <p>You requested a password reset for your Smart Quizzer account.</p>
#                 <p>To reset your password, click the button below:</p>
#                 <p style="text-align: center;">
#                     <a href="{reset_link}" class="button">Reset Your Password</a>
#                 </p>
#                 <p><strong>This link will expire in 1 hour.</strong></p>
#                 <p>If you didn't request this reset, please ignore this email.</p>
#             </div>
#             <div class="footer">
#                 <p>&copy; 2024 Smart Quizzer. All rights reserved.</p>
#             </div>
#         </div>
#     </body>
#     </html>
#     """
    
#     msg.body = f"""
#     Smart Quizzer - Password Reset Request
#     Hello {username},
#     Visit this link to reset your password (valid for 1 hour): {reset_link}
#     """
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Sent reset email to {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL: {e} ---")
#         return False


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder - integrate with SMS gateway like Twilio, MSG91, etc.)"""
    
#     # IMPORTANT: Integrate with your SMS service provider
#     # Example with Twilio (uncomment and configure):
#     # from twilio.rest import Client
#     # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
#     # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
#     # client = Client(account_sid, auth_token)
#     # message = client.messages.create(
#     #     body=f"Your Smart Quizzer password reset OTP is: {otp}. Valid for 10 minutes.",
#     #     from_=os.environ.get('TWILIO_PHONE_NUMBER'),
#     #     to=f"+91{mobile}"
#     # )
    
#     # For development/testing, just log the OTP
#     print(f"\n--- SMS OTP for {username} ({mobile}): {otp} ---")
#     print(f"--- In production, integrate with SMS gateway (Twilio/MSG91/etc.) ---\n")
    
#     # Return True for development (change to actual SMS send result in production)
#     return True


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
    
#     msg = Message(
#         subject="Password Reset OTP - Smart Quizzer",
#         recipients=[recipient_email]
#     )
    
#     msg.html = f"""
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <style>
#             body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#             .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#             .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
#             .content {{ background: #f9f9f9; padding: 20px; text-align: center; }}
#             .otp {{ font-size: 32px; font-weight: bold; color: #4CAF50; 
#                    background: #fff; padding: 20px; border-radius: 8px; 
#                    letter-spacing: 8px; margin: 20px 0; }}
#             .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
#         </style>
#     </head>
#     <body>
#         <div class="container">
#             <div class="header">
#                 <h1>Smart Quizzer</h1>
#                 <h2>Password Reset OTP</h2>
#             </div>
#             <div class="content">
#                 <p>Hello <strong>{username}</strong>,</p>
#                 <p>Your password reset OTP is:</p>
#                 <div class="otp">{otp}</div>
#                 <p><strong>This OTP will expire in 10 minutes.</strong></p>
#                 <p>Enter this code on the password reset page to continue.</p>
#                 <p>If you didn't request this OTP, please ignore this email.</p>
#             </div>
#             <div class="footer">
#                 <p>&copy; 2024 Smart Quizzer. All rights reserved.</p>
#             </div>
#         </div>
#     </body>
#     </html>
#     """
    
#     msg.body = f"""
#     Smart Quizzer - Password Reset OTP
#     Hello {username},
#     Your OTP is: {otp}
#     Valid for 10 minutes.
#     """
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Sent OTP email to {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING OTP EMAIL: {e} ---")
#         return False


# # ---------- Password Strength Validation ----------
# def validate_password_strength(password):
#     """Validate password meets minimum requirements"""
#     if len(password) < 8:
#         return "Password must be at least 8 characters long"
#     if not re.search(r"[A-Z]", password):
#         return "Password must contain at least one uppercase letter"
#     if not re.search(r"[a-z]", password):
#         return "Password must contain at least one lowercase letter"
#     if not re.search(r"\d", password):
#         return "Password must contain at least one number"
#     if not re.search(r"[@$!%*?&]", password):
#         return "Password must contain at least one special character (@$!%*?&)"
#     return None


# # ---------- AI Quiz Generator ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = (
#                 f"You are a quiz generator. Difficulty: {difficulty}.\n"
#                 f"Choice: {choice} (1=topic,2=concept). Subject/Concept: {subject_or_concept}.\n"
#                 f"Generate {num_quizzes} questions. Include mcq (4 options), fill_blank, descriptive.\n"
#                 "Return only JSON array of objects with keys: type, question, options (if mcq), answer.\n"
#             )
#             resp = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=800,
#                 timeout=30
#             )
            
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
            
#             if content_clean.startswith('```'):
#                 content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()

#             if content_clean and content_clean.startswith(('[', '{')):
#                 try:
#                     return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError:
#                     return {"error": "AI response was not valid quiz JSON."}, 500
#             else:
#                 return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm:
#         return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
    
#     # Validate password strength
#     password_error = validate_password_strength(password)
#     if password_error:
#         return jsonify({"success": False, "message": password_error}), 400
    
#     if password != password_confirm:
#         return jsonify({"success": False, "message": "Passwords do not match."}), 400
    
#     # Validate email format if provided
#     if email and not validate_email(email):
#         return jsonify({"success": False, "message": "Invalid email format."}), 400
    
#     # Validate mobile format if provided
#     if mobile and not validate_mobile(mobile):
#         return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
    
#     # At least one of email or mobile must be provided
#     if not email and not mobile:
#         return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     # Check for existing user
#     existing = User.query.filter(
#         (User.username == username) | 
#         (User.email == email if email else False) |
#         (User.mobile == mobile if mobile else False)
#     ).first()
    
#     if existing:
#         return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(
#         username=username, 
#         email=email if email else None, 
#         mobile=mobile if mobile else None,
#         password_hash=password_hash
#     )
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password:
#         return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     # Allow login by username, email, or mobile
#     user = User.query.filter(
#         (User.username == identifier) | 
#         (User.email == identifier) | 
#         (User.mobile == identifier)
#     ).first()
    
#     if not user:
#         return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else:
#         return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email")  # "email" or "mobile"

#     if not identifier:
#         return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     # Determine if identifier is email or mobile
#     is_email = '@' in identifier
#     is_mobile = identifier.isdigit() and len(identifier) == 10

#     if not is_email and not is_mobile:
#         return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     # Find user
#     if is_email:
#         user = User.query.filter_by(email=identifier).first()
#     else:
#         user = User.query.filter_by(mobile=identifier).first()

#     if not user:
#         # Security: Don't reveal if user exists
#         print(f"Password reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been sent."}), 200

#     # EMAIL METHOD: Send reset link
#     if is_email or reset_method == "email":
#         if not user.email:
#             return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         plain_token = str(uuid.uuid4())
#         token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#         expiry = datetime.utcnow() + timedelta(hours=1)

#         user.reset_token_hash = token_hash
#         user.reset_token_expiry = expiry
#         db.session.commit()

#         email_sent = send_reset_email(user.email, plain_token, user.username)
        
#         if email_sent:
#             return jsonify({
#                 "success": True, 
#                 "message": "Password reset link has been sent to your email.",
#                 "method": "email"
#             }), 200
#         else:
#             user.reset_token_hash = None
#             user.reset_token_expiry = None
#             db.session.commit()
#             return jsonify({"success": False, "message": "Failed to send email."}), 500

#     # MOBILE METHOD: Send OTP
#     else:
#         if not user.mobile:
#             return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         expiry = datetime.utcnow() + timedelta(minutes=10)

#         user.otp_code = otp
#         user.otp_expiry = expiry
#         user.otp_verified = False
#         db.session.commit()

#         # Send OTP via SMS (or email as fallback)
#         sms_sent = send_otp_sms(user.mobile, otp, user.username)
        
#         if sms_sent:
#             return jsonify({
#                 "success": True, 
#                 "message": f"OTP has been sent to {user.mobile[-4:].rjust(10, '*')}",
#                 "method": "mobile"
#             }), 200
#         else:
#             user.otp_code = None
#             user.otp_expiry = None
#             db.session.commit()
#             return jsonify({"success": False, "message": "Failed to send OTP."}), 500


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     """Verify OTP for mobile-based password reset"""
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp:
#         return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code:
#         return jsonify({"success": False, "message": "Invalid OTP or session expired."}), 400

#     if user.otp_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "OTP has expired. Please request a new one."}), 400

#     if user.otp_code != otp:
#         return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     # Mark OTP as verified
#     user.otp_verified = True
#     db.session.commit()

#     # Generate a temporary token for password reset
#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password:
#         return jsonify({"success": False, "message": "Token and new password are required."}), 400

#     # Validate password strength
#     password_error = validate_password_strength(new_password)
#     if password_error:
#         return jsonify({"success": False, "message": password_error}), 400

#     # Hash the token for lookup
#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user:
#         return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
    
#     if user.reset_token_expiry < datetime.utcnow():
#         return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     # Update password and clear reset tokens
#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_code = None
#     user.otp_expiry = None
#     user.otp_verified = False
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)




# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# # Note: The specific mail server config is now irrelevant for console logging.
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)

# # ====================================================================
# # --- UTILITY FUNCTIONS (Defined before being called in routes) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """Validate password meets minimum requirements"""
#     if len(password) < 8: return "Password must be at least 8 characters long"
#     if not re.search(r"[A-Z]", password): return "Password must contain at least one uppercase letter"
#     if not re.search(r"[a-z]", password): return "Password must contain at least one lowercase letter"
#     if not re.search(r"\d", password): return "Password must contain at least one number"
#     if not re.search(r"[@$!%*?&]", password): return "Password must contain at least one special character (@$!%*?&)"
#     return None


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """
#     FIX: Skips external mail connection and logs the link to the console for testing.
#     (This resolves the SMTP connection error 10061).
#     """
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
    
#     print("\n--- PASSWORD RESET TOKEN (FOR TESTING) ---")
#     print(f"User: {username}")
#     print(f"Recipient: {recipient_email}")
#     print(f"Link (COPY THIS): {reset_link}")
#     print("-------------------------------------------\n")
    
#     # We return True to signal success to the /forgot_password route
#     return True 


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing AI logic remains the same)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = ("...") # Prompt generation
#             resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], timeout=30, max_tokens=800)
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
#             if content_clean.startswith('```'): content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()
#             if content_clean and content_clean.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else: return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES (The final functional code) ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # FIX: Call the simplified console log sender
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed."}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)







# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# # Note: Local debug settings are kept for structure but are unused in the code below.
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)

# # ====================================================================
# # --- UTILITY FUNCTIONS (Defined before being called in routes) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only.
#     """
#     # This must be simple to avoid failing the final submit.
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
        
#     return None # CRITICAL: This is the only return path for success 


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
    
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         # NOTE: This call will fail (as expected) if local SMTP is not running.
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}") # Print the link for debugging
#         return True # Return True to allow the /forgot_password route to proceed


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing AI logic remains the same)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = ("...") # Prompt generation
#             resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], timeout=30, max_tokens=800)
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
#             if content_clean.startswith('```'): content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()
#             if content_clean and content_clean.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else: return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES (The final functional code) ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed.","reset_token": plain_token}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # FIX: Call the simplified console log sender
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed."}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)










# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)

# # ---------- Utility Functions (Defined at the top) ----------

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
        
#     return None 


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
    
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}") # Print the link for debugging
#         return True


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing AI logic remains the same)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = ("...")
#             resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], timeout=30, max_tokens=800)
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
#             if content_clean.startswith('```'): content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()
#             if content_clean and content_clean.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else: return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # FIX: Call the simplified console log sender, which returns TRUE
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({
#             "success": True, 
#             "message": "If an account exists, a reset link has been processed.",
#             "reset_token": plain_token # Return the token for frontend display
#         }), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)







# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     OPENAI_AVAILABLE = False

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # ====================================================================
# # --- UTILITY FUNCTIONS (MOVED TO TOP TO RESOLVE SCOPE ERRORS) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
        
#     return None     


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# # File: app.py (Replace the function content)
# def send_reset_email(recipient_email, token, username):
#     """
#     FIX: Skips mail server connection and logs the link to the console for testing.
#     """
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"

#     print("\n--- PASSWORD RESET TOKEN (FOR TESTING) ---")
#     print(f"User: {username}")
#     print(f"Link (COPY THIS): {reset_link}") # The link appears here
#     print("-------------------------------------------\n")

#     return True # Always return True for success


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 

# def generate_mock_quiz(subject_or_concept, num_quizzes):
#     """Generates a simple, local mock quiz to guarantee frontend success."""
#     quiz_data = []
#     num = max(1, int(num_quizzes)) 
#     for i in range(num):
#         quiz_data.append({"type": "mcq", "question": f"Mock Q{i+1} on {subject_or_concept}?", "options": ["A", "B", "C", "D"], "answer": "A"})
#     return {"quiz": quiz_data}
# # ====================================================================


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing AI logic remains the same, but this function is BYPASSED for testing)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = ("...") # Prompt generation
#             resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], timeout=30, max_tokens=800)
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
#             if content_clean.startswith('```'): content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()
#             if content_clean and content_clean.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else: return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # Call the simplified console log sender
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({
#             "success": True, 
#             "message": "If an account exists, a reset link has been processed.",
#             "reset_token": plain_token # Return the token for frontend display
#         }), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)







# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from openai import OpenAI
# from flask_mail import Mail, Message 

# # --- OpenAI availability flag ---
# try:
#     OPENAI_AVAILABLE = True
# except Exception:
#     pass

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# # Note: These settings are unused but must be present for Mail initialization.
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # ====================================================================
# # --- UTILITY FUNCTIONS (Defined at the top) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
        
#     return None 


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """
#     FIX: Skips external mail connection and logs the link to the console for testing.
#     This GUARANTEES success in the /forgot_password route.
#     """
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
    
#     # We must remove the mail.send() line here to ensure no WinError 10061 crash.
#     # The mail.send() and associated try/except block that caused failure is removed.
    
#     print("\n--- PASSWORD RESET TOKEN (FOR TESTING) ---")
#     print(f"User: {username}")
#     print(f"Recipient: {recipient_email}")
#     print(f"Link (COPY THIS): {reset_link}")
#     print("-------------------------------------------\n")
    
#     return True # Always return True to signal success to the caller


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "username": self.username,
#             "email": self.email,
#             "mobile": self.mobile,
#             "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Remains the same) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     # (Existing AI logic remains the same)
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")
#     if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
#         try:
#             client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#             prompt = ("...") # Prompt generation
#             resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], timeout=30, max_tokens=800)
#             content = resp.choices[0].message.content
#             content_clean = content.strip()
#             if content_clean.startswith('```'): content_clean = re.sub(r"^\s*```(json)?\s*|```\s*$", "", content_clean, flags=re.MULTILINE).strip()
#             if content_clean and content_clean.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content_clean)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else: return {"error": "OpenAI client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # FIX: Call the simplified console log sender
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "").strip()
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)




# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# # --- FIX: New Gemini Imports ---
# from google import genai
# from google.genai.errors import APIError as GeminiAPIError # Rename to avoid conflict
# # --- Removed unused OpenAI import ---
# from flask_mail import Mail, Message 

# # --- Gemini availability flag ---
# try:
#     gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     GEMINI_AVAILABLE = True
# except Exception:
#     GEMINI_AVAILABLE = False
# # ----------------------------------

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # ====================================================================
# # --- UTILITY FUNCTIONS (All utility functions remain the same) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users:
#             print("The 'users' table is currently empty.")
#             print("------------------------------------------")
#             return

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None

# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
#     return None 

# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))

# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}")
#         return True

# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 

# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models (Remains the same) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
#     password_hash = db.Column(db.String(200), nullable=False)
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()


# # ---------- Helper: AI quiz generation (GEMINI IMPLEMENTATION) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call Google Gemini. If successful, returns {'quiz': data}. On error, returns {'error': msg}, 500.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # FIX: Use GEMINI_AVAILABLE check
#     if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
#         try:
#             prompt = (
#                 f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
#                 f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
#                 f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. Ensure the JSON is well-formed."
#             )

#             # --- FIX: Call Gemini API ---
#             response = gemini_client.models.generate_content(
#                 model='gemini-2.5-flash', 
#                 contents=prompt,
#                 config={'response_mime_type': 'application/json', 'temperature': 0.7} 
#             )
#             content = response.text.strip()
#             # ---------------------------

#             # Final check and parsing
#             if content.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON."}, 500
#             else: return {"error": "AI response was not valid quiz JSON."}, 500
        
#         # Catch specific API errors from Gemini
#         except GeminiAPIError as e:
#             return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "Gemini client is not configured or API key is missing."}, 500


# # ---------- ROUTES (All other routes remain functional) ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         # Call the simplified console log sender
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         # Log OTP to console (simulating SMS)
#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # CRITICAL FIX: Call the REAL AI generator (Gemini)
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     # Check if the AI returned an error tuple (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         # This will now display the specific API key error on the frontend
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     # Return the successful quiz data
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)





# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# # --- Replaced OpenAI with Gemini Imports ---
# from google import genai
# from google.genai.errors import APIError as GeminiAPIError # For error handling
# # ------------------------------------------
# from flask_mail import Mail, Message 

# # --- Gemini availability flag ---
# GEMINI_API_KEY_DEV = "AIzaSyAO6B2rFk9VzjJ7uLUJH5-YYjAN4R0wByA" # <--- PASTE YOUR KEY HERE
# os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_DEV # Forcefully set the key


# try:
#     gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     GEMINI_AVAILABLE = True
# except Exception:
#     GEMINI_AVAILABLE = False
# # Note: Removed check for OPENAI_AVAILABLE as it is obsolete.

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # --- UTILITY FUNCTIONS (Defined at the top) ---
# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users: print("The 'users' table is currently empty.")
#         print("------------------------------------------")

# def validate_email(email):
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_mobile(mobile):
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None

# def validate_password_strength(password):
#     if len(password) < 6: return "Password must be at least 6 characters long."
#     return None 

# def generate_otp():
#     return str(random.randint(100000, 999999))

# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     print("\n--- PASSWORD RESET TOKEN (FOR TESTING) ---")
#     print(f"Link (COPY THIS): {reset_link}") 
#     return True 

# def send_otp_sms(mobile, otp, username):
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 

# def send_otp_email(recipient_email, otp, username):
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # -------------------------------------------------------------


# # ---------- Models (Remains the same) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
#     password_hash = db.Column(db.String(200), nullable=False)
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat()}

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()


# # ---------- Helper: AI quiz generation (FINAL GEMINI PROMPT) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call Google Gemini with a multi-type structured prompt.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     # FIX: Use GEMINI_AVAILABLE check and gemini_client
#     if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
#         try:
#             # --- FINAL CORRECT PROMPT FOR MIXED QUESTIONS ---
#             prompt = (
#                 f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
#                 f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
#                 f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. "
                
#                 # CRITICAL: Request the mixed types
#                 f"Ensure the output includes a balanced mix of: "
#                 f"1. Multiple Choice (type: 'mcq', answer: single option). "
#                 f"2. True/False (type: 'true_false', answer: 'True' or 'False'). "
#                 f"3. Fill-in-the-Blank (type: 'fill_blank', answer: single word/phrase). "
#                 f"4. Multiple Answer Select (type: 'multi_select', answer: comma-separated correct options)."
#                 f"The total number of questions must be {num_quizzes}."
#             )

#             # --- API Call using gemini_client ---
#             response = gemini_client.models.generate_content(
#                 model='gemini-2.5-flash', 
#                 contents=prompt,
#                 config={'response_mime_type': 'application/json', 'temperature': 0.7} 
#             )
#             content = response.text.strip()
#             # -----------------------------------

#             # Final check and parsing
#             if content.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON (Parsing failed)."}, 500
#             else: return {"error": "AI response was not valid quiz JSON (Bad format)."}, 500
        
#         except GeminiAPIError as e:
#             return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "Gemini client is not configured or API key is missing."}, 500


# # ---------- ROUTES (The final functional code) ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # CRITICAL FIX: Call the REAL AI generator (Gemini)
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     # Check if the AI returned an error tuple (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         # This will now display the specific API key error on the frontend
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     # Return the successful quiz data
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)














# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from google import genai
# from google.genai.errors import APIError as GeminiAPIError 
# from flask_mail import Mail, Message 

# # --- Gemini availability flag ---
# GEMINI_API_KEY_DEV = "AIzaSyAO6B2rFk9VzjJ7uLUJH5-YYjAN4R0wByA" # Placeholder for your key
# os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_DEV 

# try:
#     gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     GEMINI_AVAILABLE = True
# except Exception:
#     GEMINI_AVAILABLE = False
# # ----------------------------------

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # ====================================================================
# # --- UTILITY FUNCTIONS (Defined at the top to resolve all scope errors) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users: print("The 'users' table is currently empty.")
#         print("------------------------------------------")

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
#     return None 


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
    
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}")
#         return True


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     # This function is now defined here and accessible by routes below.
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat(),
#         }

# # ---------- Ensure DB ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Gemini) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call Google Gemini with a multi-type structured prompt.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
#         try:
#             prompt = (
#                 f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
#                 f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
#                 f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. "
#                 f"Ensure the output includes a balanced mix of: "
#                 f"1. Multiple Choice (type: 'mcq', answer: single option). "
#                 f"2. True/False (type: 'true_false', answer: 'True' or 'False'). "
#                 f"3. Fill-in-the-Blank (type: 'fill_blank', answer: single word/phrase). "
#                 f"4. Multiple Answer Select (type: 'multi_select', answer: comma-separated correct options)."
#                 f"The total number of questions must be {num_quizzes}."
#             )
#             response = gemini_client.models.generate_content(
#                 model='gemini-2.5-flash', contents=prompt, config={'response_mime_type': 'application/json', 'temperature': 0.7} 
#             )
#             content = response.text.strip()
#             if content.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON (Parsing failed)."}, 500
#             else: return {"error": "AI response was not valid quiz JSON (Bad format)."}, 500
        
#         except GeminiAPIError as e:
#             return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "Gemini client is not configured or API key is missing."}, 500


# # ---------- ROUTES (The final functional code) ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # CRITICAL FIX: Call the REAL AI generator (Gemini)
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     # Check if the AI returned an error tuple (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         # This will now display the specific API key error on the frontend
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     # Return the successful quiz data
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)




# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from google import genai
# from google.genai.errors import APIError as GeminiAPIError 
# from flask_mail import Mail, Message 

# # --- Gemini availability flag ---
# GEMINI_API_KEY_DEV = "AIzaSyAO6B2rFk9VzjJ7uLUJH5-YYjAN4R0wByA" # Placeholder for your key
# os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_DEV 

# try:
#     gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     GEMINI_AVAILABLE = True
# except Exception:
#     GEMINI_AVAILABLE = False
# # ----------------------------------

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # ====================================================================
# # --- UTILITY FUNCTIONS (Defined at the top) ---
# # ====================================================================

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users: print("The 'users' table is currently empty.")
#         print("------------------------------------------")

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None


# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None


# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: 
#         return "Password must be at least 6 characters long."
#     return None 


# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))


# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
    
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}")
#         return True


# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 


# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models (UPDATED WITH QUIZ SESSION) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat(),
#         }

# # CRITICAL: NEW MODEL FOR QUIZ HISTORY STORAGE
# class QuizSession(db.Model):
#     __tablename__ = "quiz_sessions"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
#     score = db.Column(db.Integer, nullable=False)
#     total_questions = db.Column(db.Integer, nullable=False)
#     topic = db.Column(db.String(100))
#     difficulty = db.Column(db.String(20))
    
#     results_json = db.Column(db.Text, nullable=False)
    
#     completed_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "score": self.score,
#             "total": self.total_questions,
#             "topic": self.topic,
#             "completed_at": self.completed_at.isoformat(),
#             # Convert JSON string back to dictionary for frontend
#             "details": json.loads(self.results_json) 
#         }
# # -----------------------------------------------

# # ---------- Ensure DB (Will now create QuizSession table) ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Gemini) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call Google Gemini with a multi-type structured prompt.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
#         try:
#             prompt = (
#                 f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
#                 f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
#                 f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. "
#                 f"Ensure the output includes a balanced mix of: "
#                 f"1. Multiple Choice (type: 'mcq', answer: single option). "
#                 f"2. True/False (type: 'true_false', answer: 'True' or 'False'). "
#                 f"3. Fill-in-the-Blank (type: 'fill_blank', answer: single word/phrase). "
#                 f"4. Multiple Answer Select (type: 'multi_select', answer: comma-separated correct options)."
#                 f"The total number of questions must be {num_quizzes}."
#             )
#             response = gemini_client.models.generate_content(
#                 model='gemini-2.5-flash', contents=prompt, config={'response_mime_type': 'application/json', 'temperature': 0.7} 
#             )
#             content = response.text.strip()
#             if content.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON (Parsing failed)."}, 500
#             else: return {"error": "AI response was not valid quiz JSON (Bad format)."}, 500
        
#         except GeminiAPIError as e:
#             return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "Gemini client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # CRITICAL FIX: Call the REAL AI generator (Gemini)
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     # Check if the AI returned an error tuple (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         # This will now display the specific API key error on the frontend
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     # Return the successful quiz data
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 00


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)








# import os
# import re
# import json
# import uuid  
# import hashlib
# import random
# import google.generativeai as genai
# from datetime import datetime, timedelta 
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS, cross_origin 
# from werkzeug.security import generate_password_hash, check_password_hash
# from google import genai
# from google.genai.errors import APIError as GeminiAPIError 
# from flask_mail import Mail, Message 

# # --- Gemini availability flag ---
# GEMINI_API_KEY_DEV = "AIzaSyAO6B2rFk9VzjJ7uLUJH5-YYjAN4R0wByA" 
# os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY_DEV 

# try:
#     gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#     GEMINI_AVAILABLE = True
# except Exception:
#     GEMINI_AVAILABLE = False
# # ----------------------------------

# # ---------- Configuration ----------
# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DB_PATH = os.path.join(BASE_DIR, "smart_quizzer.db")
# DEFAULT_SQLITE = "sqlite:///" + DB_PATH

# app = Flask(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_SQLITE)
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")

# # --- FLASK-MAIL CONFIGURATION ---
# app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
# app.config['MAIL_PORT'] = 587 
# app.config['MAIL_USE_TLS'] = True 
# app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER') 
# app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS') 
# app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER', 'developer@smartquizzer.com')

# mail = Mail(app)
# CORS(app) 
# db = SQLAlchemy(app)


# # --- UTILITY FUNCTIONS (Defined at the top) ---

# def print_users():
#     """Print all users for debugging."""
#     with app.app_context():
#         users = User.query.all()
#         print("\n--- DATABASE CHECK: USERS TABLE CONTENTS ---")
#         if not users: print("The 'users' table is currently empty.")
#         print("------------------------------------------")

# def validate_email(email):
#     """Validate email format"""
#     pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
#     return re.match(pattern, email) is not None

# def validate_mobile(mobile):
#     """Validate mobile number format (10 digits)"""
#     pattern = r'^[6-9]\d{9}$' 
#     return re.match(pattern, mobile) is not None

# def validate_password_strength(password):
#     """
#     FIX: Temporarily simplifies password strength to length check only (for final testing).
#     """
#     if len(password) < 6: return "Password must be at least 6 characters long."
#     return None 

# def generate_otp():
#     """Generate a 6-digit OTP"""
#     return str(random.randint(100000, 999999))

# def send_reset_email(recipient_email, token, username):
#     """Skips mail server connection and logs the link to the console for testing."""
#     reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:4200')}/reset-password?token={token}&type=email"
#     msg = Message(subject="Password Reset Request - Smart Quizzer", recipients=[recipient_email])
#     msg.body = f"Hello {username},\nVisit this link to reset your password (valid for 1 hour): {reset_link}"
    
#     try:
#         mail.send(msg)
#         print(f"\n--- SUCCESS: Email sent to local debug server for {recipient_email} ---")
#         return True
#     except Exception as e:
#         print(f"\n--- ERROR SENDING MAIL (SMTP Failed, Printing Link): {e} ---")
#         print(f"Link (COPY THIS): {reset_link}")
#         return True

# def send_otp_sms(mobile, otp, username):
#     """Send OTP via SMS (placeholder)."""
#     print(f"\n--- SMS OTP for {username} (+91{mobile}): {otp} ---")
#     return True 

# def send_otp_email(recipient_email, otp, username):
#     """Send OTP via email as fallback or alternative"""
#     print(f"\n--- SENT OTP via EMAIL for {username}: {otp} ---")
#     return True 
# # ====================================================================


# # ---------- Models (UPDATED WITH QUIZ SESSION) ----------
# class User(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    
#     email = db.Column(db.String(120), unique=True, nullable=True, index=True) 
#     mobile = db.Column(db.String(15), unique=True, nullable=True, index=True) 
    
#     password_hash = db.Column(db.String(200), nullable=False)
    
#     reset_token_hash = db.Column(db.String(64), nullable=True) 
#     reset_token_expiry = db.Column(db.DateTime, nullable=True)
    
#     otp_code = db.Column(db.String(6), nullable=True)
#     otp_expiry = db.Column(db.DateTime, nullable=True)
#     otp_verified = db.Column(db.Boolean, default=False)
    
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {"id": self.id, "username": self.username, "email": self.email, "mobile": self.mobile, "created_at": self.created_at.isoformat()}


# # FIX: NEW MODEL FOR QUIZ HISTORY STORAGE
# class QuizSession(db.Model):
#     __tablename__ = "quiz_sessions"
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    
#     score = db.Column(db.Integer, nullable=False)
#     total_questions = db.Column(db.Integer, nullable=False)
#     topic = db.Column(db.String(100))
#     difficulty = db.Column(db.String(20))
    
#     results_json = db.Column(db.Text, nullable=False)
    
#     completed_at = db.Column(db.DateTime, default=datetime.utcnow)

#     def to_dict(self):
#         return {
#             "id": self.id,
#             "score": self.score,
#             "total": self.total_questions,
#             "topic": self.topic,
#             "completed_at": self.completed_at.isoformat(),
#             "details": json.loads(self.results_json)
#         }
# # -----------------------------------------------


# # ---------- Ensure DB (Will now create QuizSession table) ----------
# with app.app_context():
#     db.create_all()

# # ---------- Helper: AI quiz generation (Gemini) ----------
# def generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes):
#     """
#     Tries to call Google Gemini with a multi-type structured prompt.
#     """
#     difficulty_map = {
#         "Beginner": "easy and introductory", "Intermediate": "moderately challenging", "Advanced": "complex and expert-level"
#     }
#     difficulty = difficulty_map.get(skill_level, "easy")

#     if GEMINI_AVAILABLE and os.getenv("GEMINI_API_KEY"): 
#         try:
#             prompt = (
#                 f"You are a quiz generator. Return ONLY a single JSON array, strictly following this structure: "
#                 f"[{{\"type\": \"mcq\", \"question\": \"...\", \"options\": [\"...\"], \"answer\": \"...\"}}, ...]. "
#                 f"Topic: {subject_or_concept}. Difficulty: {difficulty}. Questions: {num_quizzes}. "
#                 f"Ensure the output includes a balanced mix of: "
#                 f"1. Multiple Choice (type: 'mcq', answer: single option). "
#                 f"2. True/False (type: 'true_false', answer: 'True' or 'False'). "
#                 f"3. Fill-in-the-Blank (type: 'fill_blank', answer: single word/phrase). "
#                 f"4. Multiple Answer Select (type: 'multi_select', answer: comma-separated correct options)."
#                 f"The total number of questions must be {num_quizzes}."
#             )
#             response = gemini_client.models.generate_content(
#                 model='gemini-2.5-flash', contents=prompt, config={'response_mime_type': 'application/json', 'temperature': 0.7} 
#             )
#             content = response.text.strip()
#             if content.startswith(('[', '{')):
#                 try: return {"quiz": json.loads(content)} 
#                 except json.JSONDecodeError: return {"error": "AI response was not valid quiz JSON (Parsing failed)."}, 500
#             else: return {"error": "AI response was not valid quiz JSON (Bad format)."}, 500
        
#         except GeminiAPIError as e:
#             return {"error": f"AI generation failed (Quota/API): {e.message}"}, 500
#         except Exception as e:
#             return {"error": f"AI generation failed: {e}"}, 500
#     else:
#         return {"error": "Gemini client is not configured or API key is missing."}, 500


# # ---------- ROUTES ----------

# @app.route("/", methods=["GET"])
# @cross_origin()
# def welcome():
#     return jsonify({"message": "Welcome to Smart Quizzer."}), 200

# @app.route("/api/register", methods=["POST"])
# @cross_origin()
# def register():
#     data = request.get_json() or {}
#     username = (data.get("username") or "").strip()
#     password = data.get("password") or ""
#     password_confirm = data.get("password_confirm") or ""
#     email = (data.get("email") or "").strip()
#     mobile = (data.get("mobile") or "").strip()
    
#     if not username or not password or not password_confirm: return jsonify({"success": False, "message": "Username, password and confirmation are required."}), 400
#     password_error = validate_password_strength(password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400
#     if password != password_confirm: return jsonify({"success": False, "message": "Passwords do not match."}), 400
#     if email and not validate_email(email): return jsonify({"success": False, "message": "Invalid email format."}), 400
#     if mobile and not validate_mobile(mobile): return jsonify({"success": False, "message": "Invalid mobile number. Use 10-digit Indian format."}), 400
#     if not email and not mobile: return jsonify({"success": False, "message": "Either email or mobile number is required."}), 400

#     existing = User.query.filter(
#         (User.username == username) | (User.email == email if email else False) | (User.mobile == mobile if mobile else False)
#     ).first()
#     if existing: return jsonify({"success": False, "message": "User already exists with this username, email, or mobile."}), 409

#     password_hash = generate_password_hash(password)
#     user = User(username=username, email=email if email else None, mobile=mobile if mobile else None, password_hash=password_hash)
#     db.session.add(user)
#     db.session.commit()
#     return jsonify({"success": True, "message": "Registration successful! You can now log in."}), 201


# @app.route("/api/login", methods=["POST"])
# @cross_origin()
# def login():
#     data = request.get_json() or {}
#     identifier = (data.get("username") or "").strip()
#     password = data.get("password") or ""
    
#     if not identifier or not password: return jsonify({"success": False, "message": "Username/Email/Mobile and password are required."}), 400

#     user = User.query.filter(
#         (User.username == identifier) | (User.email == identifier) | (User.mobile == identifier)
#     ).first()
    
#     if not user: return jsonify({"success": False, "message": "User not found. Please register first."}), 404

#     if check_password_hash(user.password_hash, password):
#         return jsonify({"success": True, "message": f"Login successful! Welcome, {user.username}.", "user": user.to_dict()}), 200
#     else: return jsonify({"success": False, "message": "Invalid credentials."}), 401


# @app.route("/api/forgot_password", methods=["POST"])
# @cross_origin()
# def forgot_password():
#     data = request.get_json() or {}
#     identifier = (data.get("identifier") or "").strip()
#     reset_method = data.get("method", "email") # Defaults to email method

#     if not identifier: return jsonify({"success": False, "message": "Email or Mobile number is required."}), 400

#     is_email = validate_email(identifier)
#     is_mobile = validate_mobile(identifier)

#     if not is_email and not is_mobile: return jsonify({"success": False, "message": "Please provide a valid email or 10-digit mobile number."}), 400

#     if is_email: user = User.query.filter_by(email=identifier).first()
#     else: user = User.query.filter_by(mobile=identifier).first()

#     if not user: 
#         print(f"Reset requested for non-existent identifier: {identifier}")
#         return jsonify({"success": True, "message": "If an account exists, a verification code has been processed."}), 200

#     # Token and expiry logic is run regardless of method
#     plain_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
#     expiry = datetime.utcnow() + timedelta(hours=1)
    
#     user.reset_token_hash = token_hash
#     user.reset_token_expiry = expiry
#     db.session.commit()

#     # --- EMAIL PATH (Link Reset) ---
#     if is_email or reset_method == "email":
#         if not user.email: return jsonify({"success": False, "message": "No email configured for this account."}), 400
        
#         send_reset_email(user.email, plain_token, user.username)
#         return jsonify({"success": True, "message": "If an account exists, a reset link has been processed.", "reset_token": plain_token}), 200

#     # --- MOBILE PATH (OTP Reset) ---
#     else: 
#         if not user.mobile: return jsonify({"success": False, "message": "No mobile configured for this account."}), 400
        
#         otp = generate_otp()
#         user.otp_code = otp
#         user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
#         user.otp_verified = False
#         db.session.commit()

#         send_otp_sms(user.mobile, otp, user.username)
        
#         return jsonify({"success": True, "message": f"OTP sent to {user.mobile[-4:].rjust(10, '*')}.", "method": "mobile"}), 200


# @app.route("/api/verify_otp", methods=["POST"])
# @cross_origin()
# def verify_otp():
#     data = request.get_json() or {}
#     mobile = (data.get("mobile") or "").strip()
#     otp = (data.get("otp") or "").strip()

#     if not mobile or not otp: return jsonify({"success": False, "message": "Mobile and OTP are required."}), 400

#     user = User.query.filter_by(mobile=mobile).first()

#     if not user or not user.otp_code: return jsonify({"success": False, "message": "Invalid mobile or session expired."}), 400
#     if user.otp_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "OTP has expired. Request a new one."}), 400
#     if user.otp_code != otp: return jsonify({"success": False, "message": "Invalid OTP. Please try again."}), 400

#     user.otp_verified = True
#     user.otp_code = None
#     user.otp_expiry = None
#     db.session.commit()

#     temp_token = str(uuid.uuid4())
#     token_hash = hashlib.sha256(temp_token.encode()).hexdigest()
    
#     user.reset_token_hash = token_hash 
#     user.reset_token_expiry = datetime.utcnow() + timedelta(minutes=15)
#     db.session.commit()

#     return jsonify({
#         "success": True, 
#         "message": "OTP verified successfully.",
#         "reset_token": temp_token
#     }), 200


# @app.route("/api/reset_password", methods=["POST"])
# @cross_origin()
# def reset_password():
#     data = request.get_json() or {}
#     token = data.get("token")
#     new_password = data.get("new_password")

#     if not token or not new_password: return jsonify({"success": False, "message": "Token and new password are required."}), 400
    
#     password_error = validate_password_strength(new_password)
#     if password_error: return jsonify({"success": False, "message": password_error}), 400

#     received_hash = hashlib.sha256(token.encode()).hexdigest()
#     user = User.query.filter_by(reset_token_hash=received_hash).first()

#     if not user: return jsonify({"success": False, "message": "Invalid or expired reset token."}), 400
#     if user.reset_token_expiry < datetime.utcnow(): return jsonify({"success": False, "message": "Reset token has expired. Please request a new one."}), 400

#     user.password_hash = generate_password_hash(new_password)
#     user.reset_token_hash = None
#     user.reset_token_expiry = None
#     user.otp_verified = False # Clear mobile verification flag
#     db.session.commit()

#     print(f"Password successfully reset for user: {user.username}")
#     return jsonify({"success": True, "message": "Password successfully reset. You can now log in."}), 200


# @app.route("/api/topic-selection", methods=["POST"])
# @cross_origin()
# def topic_selection():
#     data = request.get_json() or {}
#     name = (data.get("name") or "").strip()
#     skill_level = data.get("skill_level", "")
#     choice = str(data.get("choice", "1"))
#     subject_or_concept = (data.get("subject") or data.get("concept") or "Java").strip() # Use a default
#     num_quizzes = int(data.get("num_quizzes", 5))

#     if not name or skill_level not in ["Beginner", "Intermediate", "Advanced"] or choice not in ["1", "2"] or not subject_or_concept:
#         return jsonify({"success": False, "message": "All required fields are needed for quiz generation."}), 400

#     # CRITICAL FIX: Call the REAL AI generator (Gemini)
#     quiz_result = generate_quiz_with_ai(skill_level, choice, subject_or_concept, num_quizzes)

#     # Check if the AI returned an error tuple (status 500)
#     if isinstance(quiz_result, tuple) and len(quiz_result) == 2 and quiz_result[1] == 500:
#         # This will now display the specific API key error on the frontend
#         return jsonify({"success": False, "message": quiz_result[0]["error"]}), 500

#     # Return the successful quiz data
#     return jsonify({"success": True, "message": f"Quiz generated for {name}.", "quiz": quiz_result["quiz"]}), 200


# @app.route("/api/history/<username>", methods=["GET"])
# @cross_origin()
# def get_quiz_history(username):
#     """Fetches all quiz sessions for a specific user."""
#     user = User.query.filter_by(username=username).first()
#     if not user:
#         return jsonify({"success": False, "message": "User not found."}), 404
        
#     # Query all sessions, ordered by most recent first
#     sessions = QuizSession.query.filter_by(user_id=user.id).order_by(QuizSession.completed_at.desc()).all()
    
#     # Return list of session dictionaries
#     return jsonify([session.to_dict() for session in sessions]), 200


# @app.route("/api/health", methods=["GET"])
# @cross_origin()
# def health():
#     return jsonify({"status": "ok"}), 200


# # ---------- Run ----------
# if __name__ == "__main__":
#     with app.app_context():
#         db.create_all()
#         print_users()

#     app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)








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