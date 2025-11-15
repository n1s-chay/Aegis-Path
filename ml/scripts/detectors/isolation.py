def calculate_isolation(crowd_score, camera_present=True):
    """
    Returns isolation score: higher = more isolated = risky
    """
    return round((1 - crowd_score) * (0.5 if camera_present else 1.0), 2)
