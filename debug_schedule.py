
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from getschedule import get_email_schedule
from day_utils import get_day_schedule

def debug_schedule():
    print("🔍 Fetching schedule from DB...")
    schedule = get_email_schedule()
    
    print(f"\n🔑 Schedule Keys found: {list(schedule.keys())}")
    
    friday_users = get_day_schedule(schedule, 'Friday')
    print(f"\n📅 Friday Users (Count: {len(friday_users)}):")
    for user in friday_users[:5]:
        print(f"  - {user}")
    if len(friday_users) > 5:
        print(f"  ... and {len(friday_users) - 5} more")
        
    sunday_users = get_day_schedule(schedule, 'Sunday')
    print(f"\n📅 Sunday Users (Count: {len(sunday_users)}):")
    for user in sunday_users:
        print(f"  - {user}")
        
    monday_users = get_day_schedule(schedule, 'Monday')
    print(f"\n📅 Monday Users (Count: {len(monday_users)}):")
    print(f"  (Sample): {monday_users[:3]}")

if __name__ == "__main__":
    debug_schedule()
