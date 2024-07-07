from datetime import datetime
from tzlocal import get_localzone


def japan_to_user_time(date_string):
    # Replace the colon in the timezone offset
    date_string = date_string.replace(':', '', 1)

    # Convert the date string from Japan time to the user's local time
    japan_time = datetime.strptime(date_string, '%Y-%m-%dT%H%M%z')
    user_time = japan_time.astimezone(get_localzone())
    return user_time.strftime('%Y-%m-%d %H:%M:%S')
