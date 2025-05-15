import humanize
from datetime import datetime

def make_time(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    return humanize.naturaltime(now - dt).replace(" ago", "")
