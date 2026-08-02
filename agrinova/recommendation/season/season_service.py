import datetime

def determine_season() -> str:
    """
    Determines current agricultural season automatically based on month.
    - Kharif: June to September (Months 6-9)
    - Rabi: October to March (Months 10-12, 1-3)
    - Zaid: April to May (Months 4-5)
    """
    current_month = datetime.datetime.now().month

    if 6 <= current_month <= 9:
        return "Kharif"
    elif current_month in [10, 11, 12, 1, 2, 3]:
        return "Rabi"
    elif 4 <= current_month <= 5:
        return "Zaid"
    
    return "Kharif"
