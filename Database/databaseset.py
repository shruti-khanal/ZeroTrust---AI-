import sqlite3


def create_database():

    conn = sqlite3.connect(
        "zerotrust.db"
    )

    cursor = conn.cursor()


    cursor.execute("""
    

        CREATE TABLE IF NOT EXISTS access_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        device TEXT,
        attempts INTEGER,
        login_time INTEGER,
        sensitivity TEXT,
        latitude TEXT,
        longitude TEXT,
        risk TEXT

        )

    """)


    conn.commit()

    conn.close()


def save_request(

    username,
    device,
    attempts,
    login_time,
    sensitivity,
    latitude,
    longitude,
    risk

):

    conn = sqlite3.connect(
        "zerotrust.db"
    )

    cursor = conn.cursor()


    cursor.execute("""

        INSERT INTO access_requests

        (
            username,
            device,
            attempts,
            login_time,
            sensitivity,
            latitude,
            longitude,
            risk
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        username,
        device,
        attempts,
        login_time,
        sensitivity,
        latitude,
        longitude,
        risk

    ))


    conn.commit()

    conn.close()


create_database()
