"""
CyberGuard SME - Authentication & Authorization Module
Secure password hashing (PBKDF2-SHA256), token generation, rate limiting, and auth guards.
"""

import os
import re
import time
import logging
from collections import defaultdict
from functools import wraps
from flask import Blueprint, request, jsonify, g, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

logger = logging.getLogger("cyberguard.auth")

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Token revocation blacklist (in-memory, token string or jti)
REVOKED_TOKENS = set()

# In-memory sliding window rate limiter: ip -> list of timestamps
RATE_LIMIT_STORE = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_ATTEMPTS = 15  # requests per window


def is_rate_limited(client_ip):
    now = time.time()
    timestamps = RATE_LIMIT_STORE[client_ip]
    # Remove older timestamps outside the window
    RATE_LIMIT_STORE[client_ip] = [ts for ts in timestamps if now - ts < RATE_LIMIT_WINDOW]
    if len(RATE_LIMIT_STORE[client_ip]) >= RATE_LIMIT_MAX_ATTEMPTS:
        return True
    RATE_LIMIT_STORE[client_ip].append(now)
    return False


def get_serializer():
    secret_key = os.getenv("APP_SECRET", "cyberguard-fallback-secret-2026")
    return URLSafeTimedSerializer(secret_key)


def generate_token(user_id, email, role):
    s = get_serializer()
    return s.dumps({
        "user_id": user_id,
        "email": email,
        "role": role,
        "iat": int(time.time())
    })


def decode_token(token, max_age=86400):
    """Decode and validate authentication token. Default expiry: 24 hours."""
    if token in REVOKED_TOKENS:
        return None
    s = get_serializer()
    try:
        data = s.loads(token, max_age=max_age)
        return data
    except (BadSignature, SignatureExpired):
        return None


def get_current_user():
    """Extract authenticated user from request header or cookies."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    elif request.cookies.get("cyberguard_token"):
        token = request.cookies.get("cyberguard_token")

    if not token:
        return None

    payload = decode_token(token)
    if not payload or "user_id" not in payload:
        return None

    db = g.get("db")
    if not db:
        from database import get_db_connection
        db = get_db_connection()
        g.db = db

    user = db.execute(
        "SELECT id, name, email, role, created_at FROM users WHERE id = ?",
        (payload["user_id"],)
    ).fetchone()

    return user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({
                "success": False,
                "message": "Authentication required. Please log in."
            }), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def validate_password_strength(password):
    """
    Validate that password meets security requirements:
    - Minimum 8 characters
    - At least one letter
    - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""


EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


@auth_bp.route("/register", methods=["POST"])
def register():
    client_ip = request.remote_addr or "unknown"
    if is_rate_limited(client_ip):
        return jsonify({
            "success": False,
            "message": "Too many requests. Please wait a minute before trying again."
        }), 429

    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    company = str(data.get("company") or data.get("company_name") or "").strip()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email, and password are required."
        }), 400

    if not EMAIL_REGEX.match(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    is_valid_pw, pw_error = validate_password_strength(password)
    if not is_valid_pw:
        return jsonify({
            "success": False,
            "message": pw_error
        }), 400

    db = g.get("db")
    if not db:
        from database import get_db_connection
        db = get_db_connection()
        g.db = db

    # Check for duplicate email
    existing_user = db.execute(
        "SELECT id FROM users WHERE LOWER(email) = ?",
        (email,)
    ).fetchone()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "An account with this email address already exists."
        }), 409

    # Use secure PBKDF2-SHA256 password hash
    password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    try:
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, 'employee')",
            (name, email, password_hash)
        )
        user_id = cursor.lastrowid

        # Create user profile record
        db.execute(
            "INSERT INTO profiles (user_id, company_name, phone) VALUES (?, ?, '')",
            (user_id, company)
        )
        db.commit()

        token = generate_token(user_id, email, "employee")

        logger.info(f"User registered successfully: user_id={user_id}")

        return jsonify({
            "success": True,
            "message": "Registration successful.",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email,
                "company": company,
                "role": "employee"
            }
        }), 201

    except Exception as e:
        db.rollback()
        logger.exception("Error creating user account")
        return jsonify({
            "success": False,
            "message": "Failed to create account due to a server error."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    client_ip = request.remote_addr or "unknown"
    if is_rate_limited(client_ip):
        return jsonify({
            "success": False,
            "message": "Too many login attempts. Please wait a minute."
        }), 429

    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required."
        }), 400

    db = g.get("db")
    if not db:
        from database import get_db_connection
        db = get_db_connection()
        g.db = db

    user = db.execute(
        "SELECT id, name, email, password_hash, role, created_at FROM users WHERE LOWER(email) = ?",
        (email,)
    ).fetchone()

    # Generic error message to prevent account enumeration
    if not user or not check_password_hash(user["password_hash"], password):
        logger.warning(f"Failed login attempt for email: {email}")
        return jsonify({
            "success": False,
            "message": "Invalid email or password."
        }), 401

    # Fetch profile
    profile = db.execute(
        "SELECT company_name, phone FROM profiles WHERE user_id = ?",
        (user["id"],)
    ).fetchone()

    company_name = profile["company_name"] if profile else ""

    token = generate_token(user["id"], user["email"], user["role"])

    logger.info(f"User logged in successfully: user_id={user['id']}")

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "company": company_name,
            "role": user["role"]
        }
    }), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
        REVOKED_TOKENS.add(token)
    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    }), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    db = g.get("db")
    user = g.current_user
    profile = db.execute(
        "SELECT company_name, phone, company_size, industry FROM profiles WHERE user_id = ?",
        (user["id"],)
    ).fetchone()

    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"],
            "company": profile["company_name"] if profile else "",
            "phone": profile["phone"] if profile else "",
            "company_size": profile["company_size"] if profile and "company_size" in profile.keys() else "",
            "industry": profile["industry"] if profile and "industry" in profile.keys() else ""
        }
    })
