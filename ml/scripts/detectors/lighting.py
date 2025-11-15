import cv2

def estimate_lighting(frame):
    """
    Returns lighting score between 0 (dark) and 1 (bright)
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lighting_score = gray.mean() / 255
    return round(lighting_score, 2)
