"""
CyberGuard SME - Main Flask Application
Modular architecture, centralized error handling, and secure RESTful APIs.
"""

import os
import json
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

# Setup logging without leaking sensitive data
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
)
logger = logging.getLogger("cyberguard.app")

# Import database and blueprints
from database import init_db, get_db_connection
from auth import auth_bp, login_required, get_current_user
from assessment import assessment_bp
from training import training_bp
from recommendations import recommendations_bp
from alerts import alerts_bp, create_user_alert
from dashboard import dashboard_bp
from reports import reports_bp
from phishing_detector import analyze_phishing_url


def create_app():
    """Application factory for CyberGuard SME API."""
    init_db()
    app = Flask(__name__)

    # Secret configuration
    app.config["SECRET_KEY"] = os.getenv("APP_SECRET", "cyberguard-sme-secret-2026")

    # Configure CORS for frontend access
    allowed_origin = os.getenv("FRONTEND_ORIGIN", "*")
    CORS(app, resources={r"/api/*": {"origins": allowed_origin}}, supports_credentials=True)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reports_bp)

    # -----------------------------------------------------------------------
    # DATABASE CONTEXT LIFECYCLE
    # -----------------------------------------------------------------------
    @app.before_request
    def attach_db():
        if "db" not in g:
            g.db = get_db_connection()

    @app.teardown_appcontext
    def close_db(error=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # -----------------------------------------------------------------------
    # HEALTH CHECK & SYSTEM STATUS
    # -----------------------------------------------------------------------
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "success": True,
            "project": "CyberGuard SME",
            "description": "Cybersecurity Awareness & Protection Platform API",
            "version": "1.0.0",
            "status": "online"
        })

    @app.route("/api/health", methods=["GET"])
    def health_check():
        try:
            g.db.execute("SELECT 1")
            return jsonify({
                "success": True,
                "status": "healthy",
                "database": "connected",
                "version": "1.0.0"
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                "success": False,
                "status": "unhealthy",
                "database": "error"
            }), 500

    # -----------------------------------------------------------------------
    # PHISHING DETECTION ENDPOINTS
    # -----------------------------------------------------------------------
    @app.route("/api/phishing/check", methods=["POST"])
    def check_phishing():
        """
        Analyze a submitted URL using the rule-based phishing detection engine.
        Supports both authenticated employees and anonymous checks.
        """
        data = request.get_json(silent=True) or {}
        raw_url = str(data.get("url", "")).strip()

        if not raw_url:
            return jsonify({
                "success": False,
                "message": "Please enter a website URL to scan."
            }), 400

        # Perform comprehensive heuristic detection
        result = analyze_phishing_url(raw_url)

        # Check if user is logged in to associate scan history
        user = get_current_user()
        user_id = user["id"] if user else None

        db = g.db
        try:
            reasons_json_str = json.dumps(result["indicators"])
            db.execute("""
                INSERT INTO phishing_scans
                (user_id, url, risk_score, risk_level, reasons_json, score, findings_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                result["normalized_url"] or raw_url,
                result["risk_score"],
                result["risk_level"],
                reasons_json_str,
                result["risk_score"],
                reasons_json_str
            ))

            # Dispatch security alert if critical phishing URL was tested by user
            if user_id and result["risk_level"] in ("High", "Critical"):
                create_user_alert(
                    db,
                    user_id,
                    f"Suspicious URL Detected: {result['risk_level']} Risk",
                    f"Analyzed URL: {raw_url}. Risk Score: {result['risk_score']}/100. Action: {result['recommended_action']}",
                    severity="high" if result["risk_level"] == "Critical" else "warning"
                )

            db.commit()
        except Exception:
            db.rollback()
            logger.exception("Error recording phishing scan in database")

        return jsonify({
            "success": True,
            "url": raw_url,
            "normalized_url": result["normalized_url"],
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "is_phishing": result.get("is_phishing", result["risk_level"] in ("High", "Critical") or result["risk_score"] >= 50),
            "risk_classification": result["risk_classification"],
            "indicators": result["indicators"],
            "rule_results": result["rule_results"],
            "recommended_action": result["recommended_action"],
            "timestamp": result["timestamp"],
            "external_check_performed": result["external_check_performed"],
            "disclaimer": result["disclaimer"]
        }), 200

    @app.route("/api/phishing/history", methods=["GET"])
    @login_required
    def phishing_history():
        """Retrieve recent phishing scans for authenticated user."""
        user_id = g.current_user["id"]
        rows = g.db.execute("""
            SELECT id, url, risk_score, risk_level, reasons_json, created_at
            FROM phishing_scans
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 50
        """, (user_id,)).fetchall()

        history = []
        for r in rows:
            item = dict(r)
            try:
                item["indicators"] = json.loads(item.pop("reasons_json", "[]"))
            except Exception:
                item["indicators"] = []
            history.append(item)

        return jsonify({
            "success": True,
            "total": len(history),
            "history": history
        })

    # -----------------------------------------------------------------------
    # USER PROFILE MANAGEMENT
    # -----------------------------------------------------------------------
    @app.route("/api/profile", methods=["GET"])
    @app.route("/api/auth/profile", methods=["GET"])
    @login_required
    def get_profile():
        user = g.current_user
        profile = g.db.execute("""
            SELECT company_name, phone, company_size, industry
            FROM profiles
            WHERE user_id = ?
        """, (user["id"],)).fetchone()

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

    @app.route("/api/profile", methods=["PUT"])
    @app.route("/api/auth/profile", methods=["PUT"])
    @login_required
    def update_profile():
        user = g.current_user
        data = request.get_json(silent=True) or {}

        name = str(data.get("name", user["name"])).strip()
        company_name = str(data.get("company_name") or data.get("company") or "").strip()
        phone = str(data.get("phone", "")).strip()
        company_size = str(data.get("company_size", "")).strip()
        industry = str(data.get("industry", "")).strip()

        try:
            if name and name != user["name"]:
                g.db.execute("UPDATE users SET name = ? WHERE id = ?", (name, user["id"]))

            g.db.execute("""
                INSERT INTO profiles (user_id, company_name, phone, company_size, industry)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    company_name = excluded.company_name,
                    phone = excluded.phone,
                    company_size = excluded.company_size,
                    industry = excluded.industry
            """, (user["id"], company_name, phone, company_size, industry))

            g.db.commit()

            return jsonify({
                "success": True,
                "message": "Profile updated successfully."
            })
        except Exception:
            g.db.rollback()
            logger.exception("Error updating user profile")
            return jsonify({
                "success": False,
                "message": "Failed to update profile."
            }), 500

    # -----------------------------------------------------------------------
    # CENTRALIZED ERROR HANDLERS
    # -----------------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            "success": False,
            "message": str(e.description) if hasattr(e, "description") else "Bad request."
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            "success": False,
            "message": "Unauthorized access. Authentication required."
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            "success": False,
            "message": "Forbidden. You do not have permission to access this resource."
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            "success": False,
            "message": "The requested API endpoint was not found."
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({
            "success": False,
            "message": "HTTP method not allowed for this endpoint."
        }), 405

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({
            "success": False,
            "message": "Too many requests. Please slow down."
        }), 429

    @app.errorhandler(500)
    def server_error(e):
        logger.exception("Central internal server error caught")
        return jsonify({
            "success": False,
            "message": "An unexpected server error occurred."
        }), 500

    return app


app = create_app()

if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting CyberGuard SME Flask API on host {host} port {port}...")
    app.run(
        host=host,
        port=port,
        debug=False
    )
