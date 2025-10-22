from datetime import datetime

def get_greeting(now: datetime | None = None) -> str:
    """Return a greeting based on the time of day.

    Args:
        now: optional datetime to use for testing; defaults to current system time.
    """
    if now is None:
        now = datetime.now()
    hour = now.hour
    if 5 <= hour < 12:
        return "Good morning."
    if 12 <= hour < 18:
        return "Good afternoon."
    return "Good evening."
