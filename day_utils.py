from datetime import datetime, timedelta

def get_day_info():
    """
    Returns a dictionary with information about today and yesterday.
    
    Returns:
        dict: {
            'today': 'Monday',  # Full day name
            'yesterday': 'Sunday',  # Full day name
            'today_short': 'Mon',  # Short day name
            'yesterday_short': 'Sun'  # Short day name
        }
    """
    # Get today's date
    today = datetime.now()
    
    # Get yesterday's date
    yesterday = today - timedelta(days=1)
    
    return {
        'today': today.strftime('%A'),
        'yesterday': yesterday.strftime('%A'),
        'today_short': today.strftime('%a'),
        'yesterday_short': yesterday.strftime('%a')
    }

def get_day_schedule(schedule, day_name=None):
    """
    Get the schedule for a specific day or today if no day is specified.
    
    Args:
        schedule (dict): The schedule dictionary from get_email_schedule()
        day_name (str, optional): The day name to get schedule for. Defaults to today.
        
    Returns:
        list: List of emails for the specified day
    """
    if not day_name:
        day_name = get_day_info()['today']
    
    # Try full day name first, then try short name
    return schedule.get(day_name, schedule.get(day_name.upper()[:3], []))

if __name__ == "__main__":
    # Example usage
    day_info = get_day_info()
    print(f"Today is: {day_info['today']}")
    print(f"Yesterday was: {day_info['yesterday']}")
    print(f"Today (short): {day_info['today_short']}")
    print(f"Yesterday (short): {day_info['yesterday_short']}")
