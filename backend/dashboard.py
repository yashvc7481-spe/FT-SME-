"""
CyberGuard SME - Dashboard Module
Aggregated organizational metrics and recent security activities calculated from real database records.
"""

import logging
from flask import Blueprint, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.dashboard")

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.route("/summary", methods=["GET"])
@login_required
def get_dashboard_summary():
    """
    Calculate real statistics strictly from database records for the logged-in user.
    Never fabricates statistics.
    """
    user_id = g.current_user["id"]
    db = g.get("db")

    # 1. Latest assessment
    latest_assessment = db.execute("""
        SELECT id, score, risk_level, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    total_assessments = db.execute("""
        SELECT COUNT(*) as count FROM assessments WHERE user_id = ?
    """, (user_id,)).fetchone()["count"]

    # 2. Phishing scans
    total_scans = db.execute("""
        SELECT COUNT(*) as count FROM phishing_scans WHERE user_id = ?
    """, (user_id,)).fetchone()["count"]

    latest_scan = db.execute("""
        SELECT id, url, risk_score, risk_level, created_at
        FROM phishing_scans
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    # 3. Quizzes & training
    total_quizzes = db.execute("""
        SELECT COUNT(*) as count FROM training_results WHERE user_id = ?
    """, (user_id,)).fetchone()["count"]

    quiz_stats = db.execute("""
        SELECT AVG(CAST(score AS FLOAT) / total_questions * 100) as avg_pct
        FROM training_results
        WHERE user_id = ? AND total_questions > 0
    """, (user_id,)).fetchone()

    avg_quiz_score = round(quiz_stats["avg_pct"]) if (quiz_stats and quiz_stats["avg_pct"] is not None) else 0

    # 4. Unread alerts
    unread_alerts = db.execute("""
        SELECT COUNT(*) as count FROM alerts WHERE user_id = ? AND is_read = 0
    """, (user_id,)).fetchone()["count"]

    # 5. Composite Cyber Health Score
    # If user has an assessment, start with that score; factor in quiz knowledge
    if latest_assessment:
        base_score = latest_assessment["score"]
        if total_quizzes > 0:
            health_score = round((base_score * 0.7) + (avg_quiz_score * 0.3))
        else:
            health_score = base_score
    else:
        # Default baseline if no assessment has been conducted yet
        health_score = 0

    # 6. Recent activities log
    activities = []

    recent_assessments = db.execute("""
        SELECT 'assessment' as type, 'Completed Security Assessment' as title,
               'Score: ' || score || '% (' || risk_level || ' Risk)' as description,
               created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 3
    """, (user_id,)).fetchall()
    activities.extend([dict(r) for r in recent_assessments])

    recent_scans = db.execute("""
        SELECT 'phishing' as type, 'Analyzed Suspicious URL' as title,
               url || ' - ' || risk_level || ' Risk (' || risk_score || '/100)' as description,
               created_at
        FROM phishing_scans
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 3
    """, (user_id,)).fetchall()
    activities.extend([dict(r) for r in recent_scans])

    recent_quizzes = db.execute("""
        SELECT 'quiz' as type, 'Completed Cybersecurity Quiz' as title,
               'Scored ' || score || '/' || total_questions as description,
               created_at
        FROM training_results
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 3
    """, (user_id,)).fetchall()
    activities.extend([dict(r) for r in recent_quizzes])

    # Sort combined activities descending by created_at
    activities.sort(key=lambda x: x["created_at"], reverse=True)

    # 7. User profile details
    profile = db.execute("""
        SELECT company_name, phone FROM profiles WHERE user_id = ?
    """, (user_id,)).fetchone()

    return jsonify({
        "success": True,
        "user": {
            "id": g.current_user["id"],
            "name": g.current_user["name"],
            "email": g.current_user["email"],
            "company": profile["company_name"] if profile else "",
            "role": g.current_user["role"]
        },
        "stats": {
            "health_score": health_score,
            "has_assessment": latest_assessment is not None,
            "latest_assessment_score": latest_assessment["score"] if latest_assessment else 0,
            "risk_level": latest_assessment["risk_level"] if latest_assessment else "Not Assessed",
            "total_assessments": total_assessments,
            "total_phishing_scans": total_scans,
            "latest_phishing_score": latest_scan["risk_score"] if latest_scan else 0,
            "latest_phishing_level": latest_scan["risk_level"] if latest_scan else "None",
            "completed_quizzes": total_quizzes,
            "average_quiz_score": avg_quiz_score,
            "unread_alerts": unread_alerts
        },
        "health_score": health_score,
        "recent_activities": activities[:5],
        "recent_activity": activities[:5]
    })
