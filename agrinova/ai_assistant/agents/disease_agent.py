def get_disease_context(farm_id):
    # Currently no persistent disease history in DB
    return {
        "available": False,
        "message": "No recent disease detection history is available for this farm."
    }
