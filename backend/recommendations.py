"""
CyberGuard SME - Recommendations Module
Dynamic, prioritized remediation guidance based on assessment, phishing scans, and quiz metrics.
"""

import json
import logging
from flask import Blueprint, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.recommendations")

recommendations_bp = Blueprint("recommendations", __name__, url_prefix="/api/recommendations")


@recommendations_bp.route("", methods=["GET"])
@login_required
def get_recommendations():
    """
    Generate prioritized recommendations tailored to the user's
    assessment gaps, phishing scan history, and training performance.
    """
    user_id = g.current_user["id"]
    db = g.get("db")

    # 1. Fetch latest assessment
    assessment = db.execute("""
        SELECT score, risk_level, answers_json
        FROM assessments
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    # 2. Fetch phishing scans summary
    high_risk_scans = db.execute("""
        SELECT COUNT(*) as count
        FROM phishing_scans
        WHERE user_id = ? AND (risk_level = 'High' OR risk_level = 'Critical' OR risk_score >= 50)
    """, (user_id,)).fetchone()["count"]

    # 3. Fetch latest quiz score
    latest_quiz = db.execute("""
        SELECT score, total_questions
        FROM training_results
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,)).fetchone()

    recommendations = []

    # Parse assessment answers if available
    answers = {}
    if assessment and assessment["answers_json"]:
        try:
            answers = json.loads(assessment["answers_json"])
        except Exception:
            answers = {}

    def get_ans(key, fallback_idx=None):
        v = answers.get(key)
        if v is None and fallback_idx is not None:
            v = answers.get(f"question{fallback_idx}") or answers.get(str(fallback_idx))
        return str(v or "").strip().lower()

    # Category 1: Passwords & MFA
    pw_ans = get_ans("q1_passwords", 0)
    mfa_ans = get_ans("q2_mfa", 1)

    if mfa_ans not in ("yes", "true", "1"):
        recommendations.append({
            "id": "REC_MFA",
            "title": "Enable Multi-Factor Authentication (MFA)",
            "priority": "High",
            "category": "Access Control",
            "issue": "MFA is either disabled or only partially configured across corporate accounts.",
            "why_it_matters": "MFA blocks over 99.2% of automated credential stuffing and password-spraying attacks.",
            "recommended_action": "Require MFA on all email accounts, VPNs, cloud portals, and password managers immediately."
        })

    if pw_ans not in ("yes", "true", "1"):
        recommendations.append({
            "id": "REC_PASSWORDS",
            "title": "Enforce Strong Password Policies",
            "priority": "High",
            "category": "Credentials",
            "issue": "Weak or reused passwords may be utilized across company workstations.",
            "why_it_matters": "Short or common passwords can be cracked in seconds using offline wordlists and rainbow tables.",
            "recommended_action": "Mandate passphrases of at least 14 characters and deploy an enterprise password manager."
        })

    # Category 2: Backups & Ransomware Defense
    backup_ans = get_ans("q4_backups", 3)
    if backup_ans not in ("yes", "true", "1"):
        recommendations.append({
            "id": "REC_BACKUPS",
            "title": "Implement 3-2-1 Automated Backups",
            "priority": "High",
            "category": "Disaster Recovery",
            "issue": "Regular, isolated backups of critical business data are incomplete.",
            "why_it_matters": "Backups are the primary defense against catastrophic data loss from ransomware.",
            "recommended_action": "Keep 3 copies of data on 2 different media, with at least 1 copy stored offsite/cloud and air-gapped."
        })

    # Category 3: Updates & Patching
    updates_ans = get_ans("q3_updates", 2)
    if updates_ans not in ("yes", "true", "1"):
        recommendations.append({
            "id": "REC_PATCHING",
            "title": "Automate Security Patching",
            "priority": "Medium",
            "category": "Vulnerability Management",
            "issue": "Operating systems or software packages are updated irregularly.",
            "why_it_matters": "Unpatched vulnerabilities are one of the most common initial access vectors for cybercriminals.",
            "recommended_action": "Configure automatic updates for Windows/macOS and third-party software like browsers and PDF readers."
        })

    # Category 4: Phishing & Awareness
    training_ans = get_ans("q5_phishing_training", 4)
    if training_ans not in ("yes", "true", "1") or high_risk_scans > 0:
        recommendations.append({
            "id": "REC_PHISHING_TRAINING",
            "title": "Train Employees to Detect Phishing",
            "priority": "High" if high_risk_scans > 0 else "Medium",
            "category": "Human Defense",
            "issue": f"{high_risk_scans} high-risk phishing scan(s) observed or staff training is not yet formalized.",
            "why_it_matters": "Over 80% of reported security incidents begin with deceptive social engineering or phishing emails.",
            "recommended_action": "Train staff using CyberGuard's Training & Quiz modules and establish a simple protocol for reporting suspicious links."
        })

    # Category 5: Incident Response
    ir_ans = get_ans("q7_incident_plan", 6)
    if ir_ans not in ("yes", "true", "1"):
        recommendations.append({
            "id": "REC_INCIDENT_PLAN",
            "title": "Formulate an Incident Response Plan",
            "priority": "Medium",
            "category": "Preparedness",
            "issue": "The organization lacks a documented incident response procedure.",
            "why_it_matters": "Prompt containment within the first hour of a breach minimizes financial, operational, and legal damages.",
            "recommended_action": "Document clear steps for isolating compromised systems and list emergency IT, forensic, and legal contacts."
        })

    # Fallback default recommendations if user has no assessment yet
    if not recommendations:
        recommendations = [
            {
                "id": "REC_DEFAULT_ASSESSMENT",
                "title": "Complete Your Cyber Health Assessment",
                "priority": "High",
                "category": "Baseline Assessment",
                "issue": "Baseline organizational cybersecurity posture has not been evaluated yet.",
                "why_it_matters": "Without an assessment, critical vulnerabilities remain hidden from leadership.",
                "recommended_action": "Take the 10-question Cyber Assessment to receive tailored, prioritized recommendations."
            },
            {
                "id": "REC_DEFAULT_MFA",
                "title": "Enable Multi-Factor Authentication (MFA)",
                "priority": "High",
                "category": "Access Control",
                "issue": "Ensure all accounts have secondary authentication enabled.",
                "why_it_matters": "Drastically reduces the risk of account takeover via stolen credentials.",
                "recommended_action": "Deploy authenticator apps for all corporate email and business software."
            },
            {
                "id": "REC_DEFAULT_TRAINING",
                "title": "Complete Staff Cybersecurity Quizzes",
                "priority": "Medium",
                "category": "Employee Awareness",
                "issue": "Employee awareness is the frontline defense against targeted spear-phishing.",
                "why_it_matters": "Trained employees recognize urgency tactics and malicious attachments.",
                "recommended_action": "Encourage employees to take the 10-question cybersecurity training quiz."
            }
        ]

    return jsonify({
        "success": True,
        "total": len(recommendations),
        "recommendations": recommendations
    })
