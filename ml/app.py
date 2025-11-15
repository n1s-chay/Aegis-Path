from flask import Flask, request, jsonify
import cv2
import numpy as np
import joblib

app = Flask(__name__)
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/safe-route", methods=["POST"])
def safe_route():
    data = request.get_json()
    return jsonify({"status": "ok", "received": data})


# Load accident model




# --------------------------
# Helper functions
# --------------------------

def detect_accident(frame):
    """Dummy accident prediction using frame stats"""
    features = np.array([frame.mean(), frame.std()]).reshape(1, -1)
    prediction = model.predict(features)[0]
    return bool(prediction)

def estimate_crowdness(frame):
    """Crowdness heuristic: normalize white pixel count"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 80, 255, cv2.THRESH_BINARY)[1]
    count = cv2.countNonZero(thresh)
    crowd_score = min(count / 50000, 1.0)
    return round(crowd_score, 2)

def estimate_lighting(frame):
    """Lighting score 0-1 based on brightness"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lighting_score = gray.mean() / 255
    return round(lighting_score, 2)

def calculate_isolation(crowd_score, camera_present=True):
    """Isolation score: higher = more isolated = risky"""
    return round((1 - crowd_score) * (0.5 if camera_present else 1.0), 2)

def compute_final_safety(accident, crowd_score, lighting_score, isolation_score):
    """Combine all layers into final safety score 0-1"""
    accident_score = 1 if accident else 0
    # weighted sum
    safety_score = (0.4 * (1 - crowd_score)) + (0.3 * lighting_score) + (0.3 * (1 - isolation_score))
    return round(safety_score, 2)
# --------------------------
# Routes
# --------------------------

@app.route("/ping", methods=["GET"])
def ping():
    return "ML Server Running"

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Read image
        file = request.files['frame']
        npimg = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Run all detections
        accident = detect_accident(frame)
        crowd_score = estimate_crowdness(frame)
        lighting_score = estimate_lighting(frame)
        isolation_score = calculate_isolation(crowd_score, camera_present=True)
        safety_score = compute_final_safety(accident, crowd_score, lighting_score, isolation_score)

        return jsonify({
            "accident_detected": accident,
            "crowd_score": crowd_score,
            "lighting_score": lighting_score,
            "isolation_score": isolation_score,
            "final_safety_score": safety_score
        })

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(port=5001, debug=True)
