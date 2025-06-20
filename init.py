def analyze_eoc(text: str) -> float:
    """
    Dummy logic - replace with real scoring rules
    """
    points = 0
    if "preventive care" in text.lower():
        points += 1
    if "member satisfaction" in text.lower():
        points += 1
    if "access to care" in text.lower():
        points += 1
    if "quality improvement" in text.lower():
        points += 1
    if "plan performance" in text.lower():
        points += 1

    # Max score = 5 stars
    return round(points * 1.0, 1)
