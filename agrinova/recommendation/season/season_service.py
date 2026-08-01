import datetime

def determine_season() -> str:
    """
    Determines the current agricultural season based on the month.
    Mapping:
    - June to September: Kharif
    - October to March: Rabi
    - April to May: Zaid
    """
    current_month = datetime.datetime.now().month

    if 6 <= current_month <= 9:
        return "Kharif"
    elif current_month in [10, 11, 12, 1, 2, 3]:
        return "Rabi"
    elif 4 <= current_month <= 5:
        return "Zaid"
    
    return "Unknown"
