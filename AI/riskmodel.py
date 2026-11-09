from sklearn.tree import DecisionTreeClassifier


# ==================================================
# TRAINING DATA
# [failed_login_attempts, device_type, resource_sensitivity]
#
# Device:
# 0 = Laptop
# 1 = Desktop
# 2 = Mobile
#
# Resource sensitivity:
# 0 = Normal resource
# 1 = Sensitive resource
#
# Labels:
# 0 = LOW
# 1 = MEDIUM
# 2 = HIGH
# ==================================================

X = [
    # LOW RISK
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [1, 2, 0],

    # MEDIUM RISK
    [2, 0, 0],
    [1, 1, 1],
    [2, 1, 0],
    [2, 0, 1],

    # HIGH RISK
    [3, 0, 0],
    [3, 1, 0],
    [2, 2, 1],
    [2, 1, 1],
    [3, 2, 1],
]

y = [
    0, 0, 0, 0,
    1, 1, 1, 1,
    2, 2, 2, 2, 2
]


# ==================================================
# TRAIN DECISION TREE
# ==================================================

model = DecisionTreeClassifier(random_state=42)

model.fit(X, y)


# ==================================================
# PREDICT RISK
# ==================================================

def predict_risk(
    login_attempts,
    device_type,
    resource_sensitivity
):
    login_attempts = max(0, int(login_attempts))
    device_type = int(device_type)
    resource_sensitivity = int(resource_sensitivity)

    if device_type not in [0, 1, 2]:
        device_type = 0

    if resource_sensitivity not in [0, 1]:
        resource_sensitivity = 0

    # 3 or more failed attempts indicate HIGH risk.
    if login_attempts >= 3:
        return "HIGH"

    # 2 failed attempts increase the risk to at least MEDIUM.
    if login_attempts >= 2:

        # Mobile + sensitive resource is HIGH risk.
        if device_type == 2 and resource_sensitivity == 1:
            return "HIGH"

        # Desktop + sensitive resource is HIGH risk.
        if device_type == 1 and resource_sensitivity == 1:
            return "HIGH"

        return "MEDIUM"

    # Use the trained Decision Tree for other cases.
    prediction = model.predict([[
        login_attempts,
        device_type,
        resource_sensitivity
    ]])[0]

    if prediction == 0:
        return "LOW"

    elif prediction == 1:
        return "MEDIUM"

    return "HIGH"