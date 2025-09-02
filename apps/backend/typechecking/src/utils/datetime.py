from datetime import datetime


def get_datetime_now() -> str:
    """Get the current date and time in ISO format."""
    return datetime.now().isoformat()
