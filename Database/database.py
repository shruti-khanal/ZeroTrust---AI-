import sqlite3
from pathlib import Path

DATABASE = str(Path(__file__).resolve().with_name("zerotrust.db"))


def get_connection():
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


# ==================================================
# CREATE / UPDATE USERS TABLE
# =================================================
def create_users_table():
    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked INTEGER DEFAULT 0
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(users)"
            )
        }

        if "failed_attempts" not in columns:
            connection.execute("""
                ALTER TABLE users
                ADD COLUMN failed_attempts INTEGER DEFAULT 0
            """)

        if "locked" not in columns:
            connection.execute("""
                ALTER TABLE users
                ADD COLUMN locked INTEGER DEFAULT 0
            """)


# ==================================================
# REGISTER USER
# ==================================================

def register_user(name, username, password):

    try:
        with get_connection() as connection:

            connection.execute("""
                INSERT INTO users
                (name, username, password, failed_attempts, locked)
                VALUES (?, ?, ?, 0, 0)
            """, (name, username, password))

        return True

    except sqlite3.IntegrityError:
        return False


# ==================================================
# AUTHENTICATE USER
# ==================================================

def authenticate_user(username, password):

    with get_connection() as connection:

        user = connection.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        if user is None:
            return {
                "success": False,
                "message": "Invalid username or password.",
                "attempts": 0,
                "failed_attempts": 0,
                "locked": False
            }

        if user["locked"]:

            return {
                "success": False,
                "message": "Account locked after 3 failed login attempts.",
                "attempts": 3,
                "failed_attempts": 3,
                "locked": True
            }

        # Compatibility with the existing demo database.
        if password != user["password"]:

            attempts = min(
                3,
                int(user["failed_attempts"] or 0) + 1
            )

            locked = 1 if attempts >= 3 else 0

            connection.execute("""
                UPDATE users
                SET failed_attempts = ?, locked = ?
                WHERE id = ?
            """, (attempts, locked, user["id"]))

            if locked:
                message = "3 failed attempts reached. Account locked."
            else:
                message = (
                    f"Invalid username or password. "
                    f"Failed attempts: {attempts}/3"
                )

            return {
                "success": False,
                "message": message,
                "attempts": attempts,
                "failed_attempts": attempts,
                "locked": bool(locked)
            }

        # Keep the previous failed-attempt count available to the risk model.
        attempts_before_success = int(
            user["failed_attempts"] or 0
        )

        connection.execute("""
            UPDATE users
            SET failed_attempts = 0
            WHERE id = ?
        """, (user["id"],))

        return {
            "success": True,
            "name": user["name"],
            "username": user["username"],
            "attempts": attempts_before_success,
            "failed_attempts": attempts_before_success,
            "locked": False
        }


# ==================================================
# ACCESS HISTORY TABLE
# ==================================================

def create_access_table():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS access_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                resource TEXT,
                device TEXT,
                login_attempts INTEGER,
                risk_score INTEGER,
                risk_level TEXT,
                decision TEXT,
                latitude REAL,
                longitude REAL,
                location_accuracy REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(access_requests)"
            )
        }

        additions = {
            "username": "TEXT",
            "resource": "TEXT",
            "device": "TEXT",
            "login_attempts": "INTEGER",
            "risk_score": "INTEGER",
            "risk_level": "TEXT",
            "decision": "TEXT",
            "latitude": "REAL",
            "longitude": "REAL",
            "location_accuracy": "REAL",
            "created_at": "TIMESTAMP"
        }

        for column, definition in additions.items():

            if column not in columns:

                connection.execute(
                    f"ALTER TABLE access_requests "
                    f"ADD COLUMN {column} {definition}"
                )


# ==================================================
# Save Access Request
# ==================================================

def save_access_request(
    username,
    resource,
    device,
    login_attempts,
    risk_score,
    risk_level,
    decision,
    latitude=None,
    longitude=None,
    location_accuracy=None
):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO access_requests (
                username,
                resource,
                device,
                login_attempts,
                risk_score,
                risk_level,
                decision,
                latitude,
                longitude,
                location_accuracy
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            resource,
            device,
            login_attempts,
            risk_score,
            risk_level,
            decision,
            latitude,
            longitude,
            location_accuracy
        ))


# ==================================================
# GET ACCESS HISTORY
# ==================================================

def get_access_history():

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT
                id,
                username,
                resource,
                device,
                login_attempts,
                risk_score,
                risk_level,
                decision,
                latitude,
                longitude,
                location_accuracy,
                created_at
            FROM access_requests
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# ==================================================
# SECURITY ALERTS TABLE
# ==================================================

def create_alerts_table():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS security_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                resource TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                alert_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ==================================================
# SAVE SECURITY ALERT
# ==================================================

def save_security_alert(
    username,
    resource,
    risk_score,
    risk_level,
    alert_message
):

    with get_connection() as connection:

        connection.execute("""
            INSERT INTO security_alerts (
                username,
                resource,
                risk_score,
                risk_level,
                alert_message
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            username,
            resource,
            risk_score,
            risk_level,
            alert_message
        ))


# ==================================================
# GET SECURITY ALERTS
# ==================================================

def get_security_alerts():

    with get_connection() as connection:

        rows = connection.execute("""
            SELECT
                id,
                username,
                resource,
                risk_score,
                risk_level,
                alert_message,
                created_at
            FROM security_alerts
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# ==================================================
# INITIALIZE DATABASE
# ==================================================

create_users_table()

create_access_table()

create_alerts_table()
