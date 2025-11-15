import joblib
import numpy as np

model = joblib.load("../model/accident_model.pkl")

def detect_accident(frame):
    """
    Dummy accident detection.
    Features: mean and std deviation of frame
    Returns: True if accident detected, False otherwise
    """
    features = np.array([frame.mean(), frame.std()]).reshape(1, -1)
    return bool(model.predict(features)[0])