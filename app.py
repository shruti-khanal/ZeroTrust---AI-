from flask import Flask, render_template, request, jsonify, session
import random
import os

from database import (
    register_user,
    authenticate_user,
    save_access_request,
    get_access_history,
    save_security_alert,
    get_security_alerts
)

from risk_model import predict_risk

from dsa import (
    process_access_request,
    get_dsa_information
)


# ==================================================
# FLASK APPLICATION
# ==================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "ZEROTRUSTAI_SECRET_KEY",
    "change-this-secret-key-for-local-project"
)

# Demo OTP storage
pending_verifications = {}


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def make_error(message, status=400):

    return jsonify({
        "success": False,
        "message": message
    }), status


def is_logged_in():

    return bool(
        session.get("logged_in")
        and session.get("username")
    )


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():

    return render_template("index.html")


# ==================================================
# REGISTER
# ==================================================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not name or not username or not password:

        return make_error(
            "Please fill all registration fields."
        )

    if len(username) < 3:

        return make_error(
            "Username must contain at least 3 characters."
        )

    if len(password) < 4:

        return make_error(
            "Password must contain at least 4 characters."
        )

    if register_user(name, username, password):

        return jsonify({
            "success": True,
            "message": "Registration successful. You can now login."
        })

    return make_error(
        "Username already exists."
    )


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:

        return jsonify({
            "success": False,
            "message": "Enter username and password.",
            "failed_attempts": 0,
            "blocked": False
        })

    result = authenticate_user(username, password)

    attempts = int(
        result.get(
            "attempts",
            result.get("failed_attempts", 0)
        ) or 0
    )

    if not result.get("success"):

        return jsonify({
            "success": False,
            "message": result.get(
                "message",
                "Invalid username or password."
            ),
            "failed_attempts": attempts,
            "attempts": attempts,
            "max_attempts": 3,
            "blocked": bool(
                result.get(
                    "locked",
                    result.get("blocked", False)
                )
            )
        })

    session.clear()

    session["logged_in"] = True
    session["username"] = result["username"]
    session["name"] = result["name"]

    # Failed attempts come from the server-side database.
    session["login_attempts"] = min(
        3,
        max(0, attempts)
    )

    session["access_granted"] = False

    return jsonify({
        "success": True,
        "message": "Login successful.",
        "name": result["name"],
        "username": result["username"],
        "failed_attempts": attempts,
        "attempts": attempts,
        "max_attempts": 3
    })


# ==================================================
# AI RISK ANALYSIS
# ==================================================

@app.route("/analyze-risk", methods=["POST"])
def analyze_risk():

    if not is_logged_in():

        return make_error(
            "Please login first.",
            401
        )

    data = request.get_json(silent=True) or {}

    resource = str(
        data.get("resource", "")
    ).strip()

    device = str(
        data.get("device", "Laptop")
    ).strip()

    if not resource:

        return make_error(
            "Please enter a resource name."
        )

    if device not in ["Laptop", "Desktop", "Mobile"]:

        return make_error(
            "Invalid device type."
        )

    # Browser location received from script.js.
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    accuracy = data.get("location_accuracy")

    if latitude is None or longitude is None:

        return make_error(
            "Live location is required. Please allow location access."
        )

    try:

        latitude = float(latitude)
        longitude = float(longitude)

        if accuracy is not None:
            accuracy = float(accuracy)

        if not (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            raise ValueError

    except (TypeError, ValueError):

        return make_error(
            "Invalid location coordinates."
        )

    username = session["username"]

    login_attempts = min(
        3,
        max(0, int(session.get("login_attempts", 0)))
    )

    # Must match risk_model.py device encoding.
    device_type = {
        "Laptop": 0,
        "Desktop": 1,
        "Mobile": 2
    }[device]

    sensitive_terms = [
        "database",
        "admin",
        "server",
        "password",
        "finance",
        "student records",
        "payroll",
        "private",
        "confidential"
    ]

    resource_sensitivity = int(
        any(
            term in resource.lower()
            for term in sensitive_terms
        )
    )

    risk = predict_risk(
        login_attempts,
        device_type,
        resource_sensitivity
    )

    risk = str(risk).upper()

    if risk not in ["LOW", "MEDIUM", "HIGH"]:
        risk = "HIGH"

    risk_scores = {
        "LOW": 20,
        "MEDIUM": 50,
        "HIGH": 80
    }

    decisions = {
        "LOW": "ACCESS ALLOWED",
        "MEDIUM": "ADDITIONAL VERIFICATION REQUIRED",
        "HIGH": "ACCESS BLOCKED"
    }

    risk_score = risk_scores[risk]
    decision = decisions[risk]

    alert_message = ""

    # Save security alert for medium and high risk.
    if risk in ["MEDIUM", "HIGH"]:

        if risk == "MEDIUM":

            alert_message = (
                "Medium-risk access detected. "
                "Additional verification is required."
            )

        else:

            alert_message = (
                "High-risk access attempt detected. "
                "Access has been blocked."
            )

        save_security_alert(
            username,
            resource,
            risk_score,
            risk,
            alert_message
        )

    location_data = {
        "latitude": latitude,
        "longitude": longitude,
        "location_accuracy": accuracy
    }

    # --------------------------------------------------
    # MEDIUM RISK: OTP REQUIRED
    # --------------------------------------------------

    if risk == "MEDIUM":

        otp = str(
            random.randint(100000, 999999)
        )

        pending_verifications[username] = {
            "otp": otp,
            "resource": resource,
            "device": device,
            "login_attempts": login_attempts,
            "risk_score": risk_score,
            "risk_level": risk,
            **location_data
        }

        session["access_granted"] = False

        return jsonify({
            "success": True,
            "risk": risk,
            "risk_score": risk_score,
            "decision": decision,
            "verification_required": True,
            "demo_otp": otp,
            "login_attempts": login_attempts,
            "alert_message": alert_message
        })

    # --------------------------------------------------
    # HIGH RISK: BLOCK ACCESS
    # --------------------------------------------------

    if risk == "HIGH":

        session["access_granted"] = False

        save_access_request(
            username,
            resource,
            device,
            login_attempts,
            risk_score,
            risk,
            decision,
            latitude,
            longitude,
            accuracy
        )

        return jsonify({
            "success": True,
            "risk": risk,
            "risk_score": risk_score,
            "decision": decision,
            "verification_required": False,
            "access_granted": False,
            "login_attempts": login_attempts,
            "alert_message": alert_message
        })

    # --------------------------------------------------
    # LOW RISK: GRANT ACCESS
    # --------------------------------------------------

    process_access_request(
        username,
        resource,
        device,
        risk_score,
        risk
    )

    save_access_request(
        username,
        resource,
        device,
        login_attempts,
        risk_score,
        risk,
        decision,
        latitude,
        longitude,
        accuracy
    )

    session["access_granted"] = True

    return jsonify({
        "success": True,
        "risk": risk,
        "risk_score": risk_score,
        "decision": decision,
        "verification_required": False,
        "access_granted": True,
        "login_attempts": login_attempts,
        "alert_message": alert_message
    })


# ==================================================
# VERIFY MEDIUM RISK OTP
# ==================================================

@app.route("/verify-medium-risk", methods=["POST"])
def verify_medium_risk():

    if not is_logged_in():

        return make_error(
            "Please login first.",
            401
        )

    data = request.get_json(silent=True) or {}

    username = session["username"]

    entered_otp = str(
        data.get("otp", "")
    ).strip()

    pending = pending_verifications.get(username)

    if pending is None:

        return make_error(
            "No pending verification. Please request access again."
        )

    if not entered_otp.isdigit() or len(entered_otp) != 6:

        return make_error(
            "Please enter the 6-digit OTP."
        )

    if entered_otp != pending["otp"]:

        return make_error(
            "Invalid verification OTP."
        )

    # OTP is correct: record the approved request in DSA.
    process_access_request(
        username,
        pending["resource"],
        pending["device"],
        pending["risk_score"],
        pending["risk_level"]
    )

    decision = "ACCESS ALLOWED AFTER VERIFICATION"

    save_access_request(
        username,
        pending["resource"],
        pending["device"],
        pending["login_attempts"],
        pending["risk_score"],
        pending["risk_level"],
        decision,
        pending["latitude"],
        pending["longitude"],
        pending["location_accuracy"]
    )

    pending_verifications.pop(username, None)

    session["access_granted"] = True

    return jsonify({
        "success": True,
        "message": "Verification successful. Access approved.",
        "decision": decision,
        "risk": "MEDIUM",
        "risk_score": 50,
        "access_granted": True
    })


# ==================================================
# DSA DASHBOARD
# ==================================================

@app.route("/dsa-information")
def dsa_information():

    if not is_logged_in():

        return make_error(
            "Please login first.",
            401
        )

    return jsonify({
        "success": True,
        "data": get_dsa_information()
    })


# ==================================================
# SECURITY ALERTS
# ==================================================

@app.route("/security-alerts")
def security_alerts():

    if not is_logged_in():

        return make_error(
            "Please login first.",
            401
        )

    return jsonify({
        "success": True,
        "alerts": get_security_alerts()
    })


# ==================================================
# ACCESS HISTORY
# ==================================================

@app.route("/access-history")
def access_history():

    if not is_logged_in():

        return make_error(
            "Please login first.",
            401
        )

    return jsonify({
        "success": True,
        "history": get_access_history()
    })


# ==================================================
# SESSION STATUS
# ==================================================

@app.route("/session-status")
def session_status():

    return jsonify({
        "logged_in": is_logged_in(),
        "access_granted": bool(
            session.get("access_granted")
        ),
        "username": session.get("username", ""),
        "name": session.get("name", "")
    })


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout", methods=["POST"])
def logout():

    username = session.get("username")

    if username:
        pending_verifications.pop(username, None)

    session.clear()

    return jsonify({
        "success": True,
        "message": "Logged out successfully."
    })


# ==================================================
# RUN APPLICATION
# ==================================================

if __name__ == "__main__":

    app.run(debug=True)