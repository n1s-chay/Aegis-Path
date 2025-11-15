import cv2
from detectors.accident import detect_accident
from detectors.crowdness import estimate_crowdness
from detectors.lighting import estimate_lighting
from detectors.isolation import calculate_isolation
from detectors.safety_score import compute_final_safety

def analyze_frame(frame, camera_present=True):
    """
    Input: frame (numpy array)
    Output: dictionary with all detection layers and final safety score
    """

    # Accident detection
    accident = detect_accident(frame)

    # Crowdness
    crowd_score = estimate_crowdness(frame)

    # Lighting
    lighting_score = estimate_lighting(frame)

    # Isolation
    isolation_score = calculate_isolation(crowd_score, camera_present)

    # Final safety score
    safety_score = compute_final_safety(accident, crowd_score, lighting_score, isolation_score)

    # Return all results
    return {
        "accident_detected": accident,
        "crowd_score": crowd_score,
        "lighting_score": lighting_score,
        "isolation_score": isolation_score,
        "final_safety_score": safety_score
    }

# ---------------------------
# Test code (run locally)
# ---------------------------
if __name__ == "__main__":
    # Replace 'test.jpg' with your sample frame
    frame = cv2.imread("test.jpg")
    if frame is None:
        print("Error: test.jpg not found")
    else:
        result = analyze_frame(frame)
        print("Detection Results:")
        for k, v in result.items():
            print(f"{k}: {v}")
