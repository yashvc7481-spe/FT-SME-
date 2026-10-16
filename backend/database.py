"""
CyberGuard SME - Database Module
Safe migrations, parameterized queries, and connection management.
"""

import os
import sqlite3
import logging
from pathlib import Path

logger = logging.getLogger("cyberguard.database")

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "cyberguard.db"


def get_db_connection():
    """Create and return a configured connection to the SQLite database."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def get_existing_columns(connection, table_name):
    """Return a set of column names for a given table."""
    cursor = connection.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def table_exists(connection, table_name):
    """Check if a table exists in the database."""
    cursor = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def safe_add_column(connection, table_name, column_name, column_def):
    """Safely add a column to an existing table if it does not already exist."""
    existing_cols = get_existing_columns(connection, table_name)
    if column_name not in existing_cols:
        logger.info(f"Adding column '{column_name}' to table '{table_name}'")
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")


def init_db():
    """
    Safely initialize and migrate the database schema.
    Never drops or recreates existing tables. Preserves all data.
    """
    connection = get_db_connection()
    try:
        # Base schema creation (IF NOT EXISTS ensures no existing tables are dropped)
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                company_name TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'Medium',
                answers_json TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS phishing_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                url TEXT NOT NULL,
                risk_score INTEGER NOT NULL DEFAULT 0,
                risk_level TEXT NOT NULL DEFAULT 'Low',
                reasons_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );

            CREATE TABLE IF NOT EXISTS training_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS training_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                total_questions INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'info',
                is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );
        """)

        # Safe migrations: check and add columns if they are missing
        if table_exists(connection, "profiles"):
            safe_add_column(connection, "profiles", "company_size", "TEXT DEFAULT ''")
            safe_add_column(connection, "profiles", "industry", "TEXT DEFAULT ''")

        if table_exists(connection, "assessments"):
            safe_add_column(connection, "assessments", "total_questions", "INTEGER DEFAULT 10")

        if table_exists(connection, "phishing_scans"):
            safe_add_column(connection, "phishing_scans", "score", "INTEGER DEFAULT 0")
            safe_add_column(connection, "phishing_scans", "findings_json", "TEXT DEFAULT '[]'")

        if table_exists(connection, "training_questions"):
            safe_add_column(connection, "training_questions", "category", "TEXT DEFAULT 'General'")

        if table_exists(connection, "training_results"):
            safe_add_column(connection, "training_results", "answers_json", "TEXT DEFAULT '{}'")

        # Create useful indexes
        connection.executescript("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
            CREATE INDEX IF NOT EXISTS idx_profiles_user ON profiles(user_id);
            CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments(user_id);
            CREATE INDEX IF NOT EXISTS idx_phishing_user ON phishing_scans(user_id);
            CREATE INDEX IF NOT EXISTS idx_training_results_user ON training_results(user_id);
            CREATE INDEX IF NOT EXISTS idx_alerts_user ON alerts(user_id);
        """)

        # Safe seed of training questions ONLY if table is empty
        cursor = connection.execute("SELECT COUNT(*) as count FROM training_questions")
        row = cursor.fetchone()
        if row and row["count"] == 0:
            seed_training_questions(connection)

        connection.commit()
    finally:
        connection.close()


def seed_training_questions(connection):
    """Seed all 20 quiz questions matching frontend quiz.js into database."""
    questions = [
        (
            "What should you do if you receive a suspicious email link?",
            "Click it immediately",
            "Verify the sender and link before clicking",
            "Forward it to everyone",
            "Enter your password",
            "Verify the sender and link before clicking",
            "Always inspect URLs and verify sender details through a trusted channel before clicking links.",
            "Phishing"
        ),
        (
            "Which password is the strongest?",
            "password123",
            "company2026",
            "Yash123",
            "A9!kP#72zL@4",
            "A9!kP#72zL@4",
            "Strong passwords combine uppercase, lowercase, numbers, and special symbols with sufficient length.",
            "Passwords"
        ),
        (
            "Which is a common sign of phishing?",
            "Urgent request for sensitive information",
            "Normal company newsletter",
            "Expected meeting invitation",
            "Known internal message",
            "Urgent request for sensitive information",
            "Attackers frequently manufacture urgency or panic to compel victims to bypass security checks.",
            "Phishing"
        ),
        (
            "What is malware?",
            "A security policy",
            "Malicious software",
            "A backup system",
            "A password manager",
            "Malicious software",
            "Malware is intrusive software designed to damage, exploit, or disable computers and devices.",
            "Malware"
        ),
        (
            "What does MFA stand for?",
            "Multiple File Access",
            "Multi-Factor Authentication",
            "Main Firewall Application",
            "Managed File Account",
            "Multi-Factor Authentication",
            "MFA requires two or more verification factors to gain access to a resource.",
            "Authentication"
        ),
        (
            "Why are software updates important?",
            "They change computer colors",
            "They fix bugs and security vulnerabilities",
            "They delete all passwords",
            "They disable firewalls",
            "They fix bugs and security vulnerabilities",
            "Vendors release security patches to remediate actively exploited vulnerabilities.",
            "System Security"
        ),
        (
            "Why do attackers often create a sense of urgency?",
            "To encourage careful thinking",
            "To pressure users into making quick decisions",
            "To improve security",
            "To reduce email traffic",
            "To pressure users into making quick decisions",
            "Emotional urgency impedes critical thinking, increasing the likelihood of falling for scams.",
            "Phishing"
        ),
        (
            "Should you reuse the same password for important accounts?",
            "Yes, always",
            "Only for banking",
            "No, use unique passwords",
            "Only on weekends",
            "No, use unique passwords",
            "Credential stuffing exploits reused passwords across different websites and services.",
            "Passwords"
        ),
        (
            "Which data should businesses regularly back up?",
            "Only images",
            "Only emails",
            "Important business data",
            "Nothing",
            "Important business data",
            "Comprehensive, isolated backups enable rapid disaster and ransomware recovery.",
            "Backups"
        ),
        (
            "What is the safest response to an unknown attachment?",
            "Open it immediately",
            "Verify it before opening",
            "Send it to customers",
            "Rename it and open it",
            "Verify it before opening",
            "Malicious attachments frequently contain macros, scripts, or executables.",
            "Email Security"
        ),
        (
            "What should you check before entering credentials on a website?",
            "The URL and website domain",
            "The screen brightness",
            "The computer wallpaper",
            "The browser color",
            "The URL and website domain",
            "Always verify the URL and domain before entering any credentials.",
            "Phishing"
        ),
        (
            "Which action helps reduce malware risk?",
            "Download software from unknown sites",
            "Keep software updated",
            "Disable security tools",
            "Open every attachment",
            "Keep software updated",
            "Keeping software updated patches security vulnerabilities that malware exploits.",
            "Malware"
        ),
        (
            "Why should software be updated regularly?",
            "To fix security vulnerabilities",
            "To remove the keyboard",
            "To reduce storage",
            "To disable protection",
            "To fix security vulnerabilities",
            "Regular updates patch known security vulnerabilities that attackers could exploit.",
            "System Security"
        ),
        (
            "What does BEC stand for?",
            "Business Email Compromise",
            "Business Encryption Control",
            "Basic Email Connection",
            "Backup Email Center",
            "Business Email Compromise",
            "BEC is a sophisticated scam targeting organizations through email fraud.",
            "BEC"
        ),
        (
            "What is an insider threat?",
            "A threat originating from someone with authorized access",
            "Only an internet virus",
            "A hardware failure",
            "A software update",
            "A threat originating from someone with authorized access",
            "Insider threats come from employees or contractors who misuse authorized access.",
            "Insider Threat"
        ),
        (
            "What can help a business recover after ransomware?",
            "Reliable backups",
            "Weak passwords",
            "Unknown downloads",
            "Disabling security",
            "Reliable backups",
            "Reliable, offline backups are the primary defense against ransomware data loss.",
            "Ransomware"
        ),
        (
            "What is the purpose of cybersecurity awareness training?",
            "Teach users to recognize and reduce cyber risks",
            "Make computers slower",
            "Remove all software",
            "Disable passwords",
            "Teach users to recognize and reduce cyber risks",
            "Cybersecurity awareness training helps employees recognize threats and follow safe practices.",
            "Training"
        ),
        (
            "What should you do with a suspicious email?",
            "Report it using the organization's process",
            "Reply with your password",
            "Click every link",
            "Forward it externally",
            "Report it using the organization's process",
            "Reporting suspicious emails helps protect the organization and prevents others from falling victim.",
            "Phishing"
        ),
        (
            "Who is responsible for cybersecurity in an organization?",
            "Only the IT department",
            "Only the manager",
            "Everyone in the organization",
            "Only new employees",
            "Everyone in the organization",
            "Cybersecurity is a shared responsibility - every employee plays a role.",
            "General Security"
        ),
        (
            "What does ransomware typically do?",
            "Improves computer performance",
            "Encrypts or blocks access to data",
            "Creates backups",
            "Updates software",
            "Encrypts or blocks access to data",
            "Ransomware encrypts files and demands payment to restore access.",
            "Ransomware"
        ),
    ]

    connection.executemany("""
        INSERT INTO training_questions
        (question, option_a, option_b, option_c, option_d, correct_answer, explanation, category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, questions)
    logger.info(f"Seeded {len(questions)} training questions into database.")


if __name__ == "__main__":
    init_db()
    print("Database verified and safe migrations applied successfully.")
