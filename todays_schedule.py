from getschedule import get_email_schedule
from day_utils import get_day_info, get_day_schedule

def main():
    # Get today's and yesterday's information
    day_info = get_day_info()
    
    # Get the full schedule
    schedule = get_email_schedule()
    
    if not schedule:
        print("❌ Failed to fetch schedule.")
        return
    
    # Get today's and yesterday's schedules
    today_emails = get_day_schedule(schedule, day_info['today'])
    yesterday_emails = get_day_schedule(schedule, day_info['yesterday'])
    
    # Print the information
    print("\n📅 Schedule Information")
    print("=" * 30)
    
    print(f"\n📆 Today is: {day_info['today']}")
    print(f"📅 Yesterday was: {day_info['yesterday']}")
    
    print(f"\n👥 Today's Schedule ({day_info['today']}):")
    print("-" * (len(day_info['today']) + 20))
    if today_emails:
        for email in today_emails:
            print(f"  • {email}")
    else:
        print("  No scheduled emails for today.")
    
    print(f"\n👥 Yesterday's Schedule ({day_info['yesterday']}):")
    print("-" * (len(day_info['yesterday']) + 23))
    if yesterday_emails:
        for email in yesterday_emails:
            print(f"  • {email}")
    else:
        print("  No scheduled emails for yesterday.")
    
    print("\n" + "=" * 30)

if __name__ == "__main__":
    main()
