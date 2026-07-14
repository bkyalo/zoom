import argparse
from getschedule import get_email_schedule
from day_utils import get_day_info, get_day_schedule
from assign import assign_license
from config import Config

def assign_today(dry_run=True):
    # 1. Get today's information
    day_info = get_day_info()
    today = day_info['today']
    
    print(f"📅 Today is: {today}")
    
    # 2. Fetch the full schedule
    print("📋 Fetching schedule from database...")
    schedule = get_email_schedule()
    if not schedule:
        print("❌ Failed to fetch schedule.")
        return
    
    # 3. Get today's emails
    today_emails = set(get_day_schedule(schedule, today))
    
    # Note: We assign to everyone scheduled today, regardless of previous state.
    # We also include EXEMPT_USERS just in case, though they should already be licensed.
    # Never assign FORCE_UNASSIGN_USERS.
    force_blocked = set(Config.FORCE_UNASSIGN_USERS)
    all_to_assign = (today_emails.union(set(Config.EXEMPT_USERS))) - force_blocked
    
    print(f"📊 Summary:")
    print(f"- Scheduled for today: {len(today_emails)}")
    print(f"- Exempt users: {len(Config.EXEMPT_USERS)}")
    print(f"- Force-unassign blocked: {len(force_blocked)}")
    print(f"- Total users to ensure licensed: {len(all_to_assign)}")
    
    if dry_run:
        print("\n📝 Dry Run results (no changes made):")
        for email in sorted(all_to_assign):
            source = "Schedule" if email in today_emails else "Exempt List"
            print(f"  - WOULD ASSIGN: {email} ({source})")
        print("\nRun with --execute to perform the actual assignment.")
        return

    print("\n🚀 Starting actual assignment...")
    success_count = 0
    fail_count = 0
    
    for email in sorted(all_to_assign):
        print(f"🔄 Assigning to {email}...", end=" ", flush=True)
        if assign_license(email):
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1
            
    print(f"\n--- Final Results ---")
    print(f"✅ Successfully assigned: {success_count}")
    print(f"❌ Failed: {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Assign Zoom licenses to all users scheduled for today.")
    parser.add_argument("--execute", action="store_true", help="Perform the actual assignment (default is dry-run)")
    
    args = parser.parse_args()
    
    assign_today(dry_run=not args.execute)
