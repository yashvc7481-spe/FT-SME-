"""
CyberGuard SME - Cyber Health Assessment Module
Server-side scoring, gap analysis, and history tracking.
"""

import json
import logging
from flask import Blueprint, request, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.assessment")

assessment_bp = Blueprint("assessment", __name__, url_prefix="/api/assessment")

ASSESSMENT_QUESTIONS = [
    {
        "id": "q1_passwords",
        "category": "Password Security",
        "question": "Does your organization use strong passwords?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Enforce a strong password policy requiring 12+ characters and unique passwords across all accounts."
    },
    {
        "id": "q2_mfa",
        "category": "Access Control",
        "question": "Is Multi-Factor Authentication (MFA) enabled?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Mandate Multi-Factor Authentication (MFA) across email, cloud services, and administrative consoles."
    },
    {
        "id": "q3_updates",
        "category": "Software Updates",
        "question": "Are operating systems and software regularly updated?",
        "options": ["Yes", "Sometimes", "No"],
        "recommendation": "Enable automatic patching and maintain a strict schedule for operating system and application updates."
    },
    {
        "id": "q4_backups",
        "category": "Backup and Recovery",
        "question": "Does your organization maintain regular backups?",
        "options": ["Yes", "Sometimes", "No"],
        "recommendation": "Implement the 3-2-1 backup strategy with immutable or offline backups tested regularly for ransomware recovery."
    },
    {
        "id": "q5_phishing_training",
        "category": "Employee Awareness",
        "question": "Are employees trained to identify phishing attacks?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Conduct regular interactive phishing simulations and security awareness training for all staff."
    },
    {
        "id": "q6_antivirus",
        "category": "Endpoint Protection",
        "question": "Is antivirus or endpoint protection installed?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Deploy managed Next-Gen Antivirus (NGAV) or Endpoint Detection and Response (EDR) on all workstations."
    },
    {
        "id": "q7_incident_plan",
        "category": "Incident Response",
        "question": "Does your organization have an incident response plan?",
        "options": ["Yes", "In Progress", "No"],
        "recommendation": "Draft and rehearse an Incident Response Plan detailing roles, external contacts, and breach notification steps."
    },
    {
        "id": "q8_access_control",
        "category": "Data Protection",
        "question": "Are sensitive company files access-controlled?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Enforce the principle of least privilege, restricting sensitive customer and financial records to authorized personnel."
    },
    {
        "id": "q9_testing",
        "category": "Security Testing",
        "question": "Is employee cybersecurity awareness regularly tested?",
        "options": ["Yes", "Sometimes", "No"],
        "recommendation": "Schedule quarterly cybersecurity quizzes and drills to measure knowledge retention."
    },
    {
        "id": "q10_monitoring",
        "category": "Security Monitoring",
        "question": "Does your organization monitor suspicious security activity?",
        "options": ["Yes", "Partially", "No"],
        "recommendation": "Enable centralized audit logging and alerts for abnormal login attempts or unauthorized data transfers."
    }
]


@assessment_bp.route("/questions", methods=["GET"])
@login_required
def get_questions():
    """Return assessment questions for the frontend to render."""
    return jsonify({
        "success": True,
        "questions": ASSESSMENT_QUESTIONS,
        "total": len(ASSESSMENT_QUESTIONS)
    })


@assessment_bp.route("/submit", methods=["POST"])
@login_required
def submit_assessment():
    """
    Accept user answers, calculate score securely on the backend,
    identify security gaps, save to database, and return results.
    """
    data = request.get_json(silent=True) or {}
    answers = data.get("answers", {})

    if not isinstance(answers, dict):
        return jsonify({
            "success": False,
            "message": "Answers must be supplied as an object."
        }), 400

    total_questions = len(ASSESSMENT_QUESTIONS)
    earned_points = 0
    max_points = total_questions * 10
    weaknesses = []
    recommendations = []

    for idx, item in enumerate(ASSESSMENT_QUESTIONS):
        qid = item["id"]
        # Accept ID, question index ("0", "question0", "q1", etc.)
        val = (
            answers.get(qid)
            or answers.get(f"question{idx}")
            or answers.get(str(idx))
            or answers.get(f"q{idx + 1}")
            or answers.get(f"question{idx + 1}")
        )

        val_str = str(val or "").strip().lower()

        if val_str in ("yes", "true", "1"):
            earned_points += 10
        elif val_str in ("partially", "sometimes", "in progress", "partial"):
            earned_points += 5
            weaknesses.append({
                "area": item["category"],
                "issue": f"{item['question']} (Partially implemented)"
            })
            recommendations.append(item["recommendation"])
        else:
            weaknesses.append({
                "area": item["category"],
                "issue": f"{item['question']} (Not implemented)"
            })
            recommendations.append(item["recommendation"])

    score_percentage = round((earned_points / max_points) * 100)

    if score_percentage >= 80:
        risk_level = "Low"
    elif score_percentage >= 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    user_id = g.current_user["id"]
    db = g.get("db")

    try:
        db.execute("""
            INSERT INTO assessments (user_id, score, risk_level, answers_json, total_questions)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, score_percentage, risk_level, json.dumps(answers), total_questions))

        # If high risk posture, automatically trigger an alert
        if risk_level == "High":
            db.execute("""
                INSERT INTO alerts (user_id, title, message, severity)
                VALUES (?, 'High Cybersecurity Risk Detected', 'Your latest security assessment indicates high exposure. Please review critical recommendations.', 'high')
            """, (user_id,))

        db.commit()

        logger.info(f"Assessment completed: user_id={user_id}, score={score_percentage}%, risk={risk_level}")

        return jsonify({
            "success": True,
            "message": "Assessment evaluated successfully.",
            "score": score_percentage,
            "risk_level": risk_level,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }), 201

    except Exception:
        db.rollback()
        logger.exception("Error saving assessment result")
        return jsonify({
            "success": False,
            "message": "Failed to record assessment result."
        }), 500


@assessment_bp.route("/history", methods=["GET"])
@login_required
def assessment_history():
    """Retrieve historical assessment results for current user."""
    user_id = g.current_user["id"]
    db = g.get("db")

    rows = db.execute("""
        SELECT id, score, risk_level, answers_json, total_questions, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 50
    """, (user_id,)).fetchall()

    history = []
    for r in rows:
        item = dict(r)
        try:
            item["answers"] = json.loads(item.pop("answers_json", "{}"))
        except Exception:
            item["answers"] = {}
        history.append(item)

    return jsonify({
        "success": True,
        "history": history
    })


@assessment_bp.route("/latest", methods=["GET"])
@login_required
def latest_assessment():
    """Retrieve latest assessment result for current user."""
    user_id = g.current_user["id"]
    db = g.get("db")

    row = db.execute("""
        SELECT id, score, risk_level, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    if not row:
        return jsonify({
            "success": True,
            "has_assessment": False,
            "score": 0,
            "risk_level": "Not assessed"
        })

    return jsonify({
        "success": True,
        "has_assessment": True,
        "score": row["score"],
        "risk_level": row["risk_level"],
        "created_at": row["created_at"]
    })
