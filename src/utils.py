from datetime import datetime

def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def print_with_timestamp(message):
    print(f"{get_timestamp()} - {message}")
