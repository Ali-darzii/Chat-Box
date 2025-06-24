import random
from datetime import datetime, timedelta

def generate_tk() -> str:
    return str(random.randint(100000, 999999))

def timestamp_to_real_time(timestamp:int, delta=timedelta(seconds=0)) -> str:
    time_format = "%Y-%m-%dT%H:%M:%SZ"
    return datetime.fromtimestamp(timestamp - delta).strftime(time_format)