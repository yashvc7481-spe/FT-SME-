"""
CyberGuard SME - Security Alerts Module
User alert dispatch, retrieval, status updates, and ownership validation.
"""

import logging
from flask import Blueprint, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.alerts")

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


def create_user_alert(db, user_id, title, message, severity="info"):
    """Internal helper to dispatch an alert to a specific user's feed."""
    try:
        db.execute("""
            INSERT INTO alerts (user_id, title, message, severity, is_read)
            VALUES (?, ?, ?, ?, 0)
        """, (user_id, title, message, severity))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Error dispatching alert to user")


@alerts_bp.route("", methods=["GET"])
@login_required
def get_alerts():
    """Retrieve security alerts for the authenticated user only."""
    user_id = g.current_user["id"]
    db = g.get("db")

    rows = db.execute("""
        SELECT id, title, message, severity, is_read, created_at
        FROM alerts
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 100
    """, (user_id,)).fetchall()

    alerts = [dict(r) for r in rows]
    unread_count = sum(1 for a in alerts if not a["is_read"])

    return jsonify({
        "success": True,
        "total": len(alerts),
        "unread_count": unread_count,
        "alerts": alerts
    })


@alerts_bp.route("/<int:alert_id>/read", methods=["PUT"])
@login_required
def mark_alert_read(alert_id):
    """Mark a single alert as read with strict ownership validation."""
    user_id = g.current_user["id"]
    db = g.get("db")

    cursor = db.execute("""
        UPDATE alerts
        SET is_read = 1
        WHERE id = ? AND user_id = ?
    """, (alert_id, user_id))
    db.commit()

    if cursor.rowcount == 0:
        return jsonify({
            "success": False,
            "message": "Alert not found or access denied."
        }), 404

    return jsonify({
        "success": True,
        "message": "Alert marked as read."
    })


@alerts_bp.route("/read-all", methods=["PUT"])
@login_required
def mark_all_read():
    """Mark all alerts as read for the authenticated user."""
    user_id = g.current_user["id"]
    db = g.get("db")

    db.execute("""
        UPDATE alerts
        SET is_read = 1
        WHERE user_id = ? AND is_read = 0
    """, (user_id,))
    db.commit()

    return jsonify({
        "success": True,
        "message": "All alerts marked as read."
    })
