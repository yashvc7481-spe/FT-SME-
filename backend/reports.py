"""
CyberGuard SME - Reports Module
Executive summaries, audit reports, and security posture breakdowns from real database metrics.
"""

import json
import logging
from flask import Blueprint, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.reports")

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.route("/summary", methods=["GET"])
@login_required
def get_report_summary():
    """
    Produce an executive cybersecurity posture report combining
    assessment findings, phishing defense metrics, and staff quiz results.
    """
    user_id = g.current_user["id"]
    db = g.get("db")

    # 1. Assessment records
    assessments = db.execute("""
        SELECT id, score, risk_level, total_questions, created_at
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    latest_assessment = assessments[0] if assessments else None

    # 2. Phishing scan distribution
    phishing_scans = db.execute("""
        SELECT id, url, risk_score, risk_level, created_at
        FROM phishing_scans
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    phishing_counts = {
        "low": sum(1 for s in phishing_scans if s["risk_level"] == "Low"),
        "medium": sum(1 for s in phishing_scans if s["risk_level"] == "Medium"),
        "high": sum(1 for s in phishing_scans if s["risk_level"] in ("High", "Critical")),
        "total": len(phishing_scans)
    }

    # 3. Training / Quiz metrics
    training_results = db.execute("""
        SELECT id, score, total_questions, created_at
        FROM training_results
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,)).fetchall()

    avg_score = 0
    if training_results:
        pcts = [(r["score"] / r["total_questions"] * 100) for r in training_results if r["total_questions"] > 0]
        avg_score = round(sum(pcts) / len(pcts)) if pcts else 0

    # 4. Overall Health Score Calculation
    assessment_score = latest_assessment["score"] if latest_assessment else 0
    if latest_assessment and training_results:
        overall_health = round((assessment_score * 0.65) + (avg_score * 0.35))
    elif latest_assessment:
        overall_health = assessment_score
    else:
        overall_health = 0

    # Qualitative evaluation
    if overall_health >= 80:
        health_status = "Good Security Posture"
        health_color = "#10b981"
        summary_text = "Your organization demonstrates solid security practices. Continue ongoing employee training and regular audits."
    elif overall_health >= 60:
        health_status = "Moderate Security Posture"
        health_color = "#f59e0b"
        summary_text = "Your organization maintains foundational controls, but critical gaps in MFA, backups, or training require attention."
    elif overall_health > 0:
        health_status = "Elevated Risk Posture"
        health_color = "#ef4444"
        summary_text = "Immediate security hardening is required to mitigate high vulnerability exposure."
    else:
        health_status = "Pending Initial Assessment"
        health_color = "#6b7280"
        summary_text = "Please complete the Cyber Health Assessment to generate your baseline risk rating."

    profile = db.execute("""
        SELECT company_name, phone FROM profiles WHERE user_id = ?
    """, (user_id,)).fetchone()

    return jsonify({
        "success": True,
        "metadata": {
            "organization": profile["company_name"] if profile and profile["company_name"] else "CyberGuard SME Enterprise",
            "evaluated_by": g.current_user["name"],
            "email": g.current_user["email"]
        },
        "summary": {
            "health_score": overall_health,
            "health_status": health_status,
            "assessment_score": assessment_score,
            "average_training": avg_score
        },
        "overall_health": {
            "score": overall_health,
            "status": health_status,
            "color": health_color,
            "summary": summary_text
        },
        "breakdown": {
            "assessment": {
                "latest_score": assessment_score,
                "risk_level": latest_assessment["risk_level"] if latest_assessment else "Not assessed",
                "completed_count": len(assessments)
            },
            "phishing": phishing_counts,
            "training": {
                "quizzes_taken": len(training_results),
                "average_score": avg_score
            }
        },
        "recent_scans": [dict(s) for s in phishing_scans[:5]],
        "recent_assessments": [dict(a) for a in assessments[:5]],
        "recent_quizzes": [
            {
                "id": t["id"],
                "score": t["score"],
                "total": t["total_questions"],
                "percentage": round(t["score"] / t["total_questions"] * 100) if t["total_questions"] > 0 else 0,
                "created_at": t["created_at"]
            }
            for t in training_results[:5]
        ]
    })
