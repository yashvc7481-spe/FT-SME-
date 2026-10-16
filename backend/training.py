"""
CyberGuard SME - Training and Quiz Module
Server-side quiz grading, question delivery, and progress tracking.
"""

import json
import logging
from flask import Blueprint, request, jsonify, g
from auth import login_required

logger = logging.getLogger("cyberguard.training")

training_bp = Blueprint("training", __name__, url_prefix="/api/training")


@training_bp.route("/questions", methods=["GET"])
@login_required
def get_training_questions():
    """
    Fetch quiz questions for the authenticated employee.
    CRITICAL: Never return correct_answer or explanation to the client.
    """
    db = g.get("db")

    rows = db.execute("""
        SELECT id, question, option_a, option_b, option_c, option_d, category
        FROM training_questions
        ORDER BY id ASC
    """).fetchall()

    questions = []
    for r in rows:
        questions.append({
            "id": r["id"],
            "question": r["question"],
            "options": [r["option_a"], r["option_b"], r["option_c"], r["option_d"]],
            "category": r["category"] if "category" in r.keys() else "General"
        })

    return jsonify({
        "success": True,
        "questions": questions,
        "total": len(questions)
    })


@training_bp.route("/submit", methods=["POST"])
@login_required
def submit_quiz():
    """
    Grade user answers on the backend.
    Accepts: { "answers": { "<question_id>": "<selected_option_index_or_string>" } }
    """
    data = request.get_json(silent=True) or {}
    user_answers = data.get("answers", {})

    if not isinstance(user_answers, dict):
        return jsonify({
            "success": False,
            "message": "Answers must be submitted as a dictionary/object."
        }), 400

    db = g.get("db")

    # Fetch all questions with answers from database
    rows = db.execute("""
        SELECT id, question, option_a, option_b, option_c, option_d, correct_answer, explanation
        FROM training_questions
        ORDER BY id ASC
    """).fetchall()

    if not rows:
        return jsonify({
            "success": False,
            "message": "No training questions are currently configured."
        }), 500

    score = 0
    total = len(rows)
    evaluations = []

    for r in rows:
        qid_str = str(r["id"])
        user_val = user_answers.get(qid_str)

        options = [r["option_a"], r["option_b"], r["option_c"], r["option_d"]]
        correct = r["correct_answer"].strip()

        # Check if user submitted an integer index (e.g. 0, 1, 2, 3) or the option string
        is_correct = False
        if user_val is not None:
            if isinstance(user_val, int) and 0 <= user_val < len(options):
                submitted_text = options[user_val]
            else:
                submitted_text = str(user_val).strip()

            is_correct = (submitted_text.lower() == correct.lower())

        if is_correct:
            score += 1

        evaluations.append({
            "question_id": r["id"],
            "question": r["question"],
            "is_correct": is_correct,
            "correct_answer": correct,
            "explanation": r["explanation"]
        })

    percentage = round((score / total) * 100) if total > 0 else 0
    user_id = g.current_user["id"]

    try:
        db.execute("""
            INSERT INTO training_results (user_id, score, total_questions, answers_json)
            VALUES (?, ?, ?, ?)
        """, (user_id, score, total, json.dumps(user_answers)))

        db.commit()

        logger.info(f"Quiz completed: user_id={user_id}, score={score}/{total} ({percentage}%)")

        return jsonify({
            "success": True,
            "score": score,
            "total_questions": total,
            "percentage": percentage,
            "results": evaluations
        }), 201

    except Exception:
        db.rollback()
        logger.exception("Error saving quiz results")
        return jsonify({
            "success": False,
            "message": "Failed to save quiz performance."
        }), 500


@training_bp.route("/history", methods=["GET"])
@login_required
def training_history():
    """Retrieve user's quiz attempt history."""
    user_id = g.current_user["id"]
    db = g.get("db")

    rows = db.execute("""
        SELECT id, score, total_questions, answers_json, created_at
        FROM training_results
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 50
    """, (user_id,)).fetchall()

    history = []
    for r in rows:
        percentage = round((r["score"] / r["total_questions"]) * 100) if r["total_questions"] > 0 else 0
        history.append({
            "id": r["id"],
            "score": r["score"],
            "total_questions": r["total_questions"],
            "percentage": percentage,
            "created_at": r["created_at"]
        })

    return jsonify({
        "success": True,
        "history": history
    })
