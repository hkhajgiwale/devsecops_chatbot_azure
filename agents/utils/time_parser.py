from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re

def parse_time_range(time_str: str):
    if not time_str:
        return None, None

    time_str = time_str.lower()

    now = datetime.utcnow()

    if "last 24 hours" in time_str or "yesterday" in time_str:
        return now - timedelta(days=1), now
    if "last 7 days" in time_str:
        return now - timedelta(days=7), now
    if "last 30 days" in time_str:
        return now - timedelta(days=30), now

    # Custom date parsing: "from 2024-06-01 to 2024-06-10"
    match = re.search(r"from\s+(.*?)\s+to\s+(.*)", time_str)
    if match:
        try:
            start = date_parser.parse(match.group(1))
            end = date_parser.parse(match.group(2))
            return start, end
        except:
            return None, None

    return None, None
