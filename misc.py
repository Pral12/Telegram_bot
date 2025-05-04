from datetime import datetime

def on_start():
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'The bot has started at {time_now}')


def on_shutdown():
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'The bot has down at {time_now}')