import sys
from datetime import datetime
def get_current_time() -> str:
    """Get the current time"""
    return datetime.now().strftime("%H:%M:%S")

print(get_current_time())

