import requests
from getschedule import get_email_schedule
from day_utils import get_day_info, get_day_schedule
from assign import assign_license, get_license_usage
from unassign import unassign_license
from config import Config
from datetime import datetime


def send_telegram_message(message):
    """Send a message to the configured Telegram chat."""
    if not Config.TELEGRAM_BOT_TOKEN or not Config.TELEGRAM_CHAT_ID:
        return False
    try:
        payload = {
            'chat_id': Config.TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(Config.TELEGRAM_API_URL, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram notification: {str(e)}")
        return False


def manage_licenses():
    print("🚀 Starting license management...")
    print("=" * 50)

    failed_unassign = []
    failed_assign = []

    schedule = get_email_schedule()
    if not schedule:
        print("❌ Failed to fetch schedule. Exiting.")
        return

    day_info = get_day_info()
    today_emails = set(get_day_schedule(schedule, day_info['today']))
    yesterday_emails = set(get_day_schedule(schedule, day_info['yesterday']))

    # Monday: also treat Friday as "yesterday" for weekend cleanup (no period logs)
    if day_info['today'] == 'Monday':
        yesterday_emails.update(get_day_schedule(schedule, 'Friday'))

    force_targets = set(Config.FORCE_UNASSIGN_USERS)
    emails_to_unassign = [
        email for email in (yesterday_emails - today_emails)
        if email not in Config.EXEMPT_USERS and email not in force_targets
    ]
    emails_to_assign = {
        email for email in (today_emails - yesterday_emails)
        if email not in force_targets
    }

    # Silently strip licenses from hardcoded force-unassign targets (never logged)
    for email in force_targets:
        try:
            unassign_license(email, quiet=True)
        except Exception:
            pass

    if emails_to_unassign:
        print(f"\n🔴 Unassigning licenses for {len(emails_to_unassign)} users...")
        for i, email in enumerate(emails_to_unassign, 1):
            print(f"{i}. Unassigning from {email}...", end=" ")
            try:
                if unassign_license(email):
                    print("✅ Done")
                else:
                    print("❌ Failed")
                    failed_unassign.append((email, "Failed to unassign license"))
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_unassign.append((email, str(e)))
    else:
        print("\nℹ️ No users to unassign.")

    if emails_to_assign:
        print(f"\n🟢 Assigning licenses to {len(emails_to_assign)} users...")
        for i, email in enumerate(emails_to_assign, 1):
            print(f"{i}. Assigning to {email}...", end=" ")
            try:
                if assign_license(email, quiet=True):
                    print("✅ Done")
                else:
                    print("❌ Failed")
                    failed_assign.append((email, "Failed to assign license"))
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_assign.append((email, str(e)))
    else:
        print("\nℹ️ No users to assign.")

    license_info = get_license_usage()
    total_unassigned = len(emails_to_unassign)
    total_assigned = len(emails_to_assign)
    success_unassign = total_unassigned - len(failed_unassign)
    success_assign = total_assigned - len(failed_assign)

    def format_failed(failed_list):
        if not failed_list:
            return "• No failures"
        return "\n".join([f"• {email}: {error}" for email, error in failed_list])

    current_time = datetime.now()
    license_summary = ""
    if license_info:
        license_summary = (
            f"\n\n<b>📊 License Usage:</b>\n"
            f"• Total Licenses: {license_info['total_licenses']}\n"
            f"• Used Licenses: {license_info['used_licenses']}\n"
            f"• Available Licenses: {license_info['available_licenses']}"
        )
        if (license_info['total_licenses'] > 0
                and license_info['available_licenses'] / license_info['total_licenses'] < 0.1):
            license_summary += "\n\n⚠️ <b>Warning: Running low on available licenses!</b>"

    summary = f"""
<b>📊 License Management Summary</b>
==========================
📅 <b>Date:</b> {current_time.strftime('%Y-%m-%d')}
⏰ <b>Time:</b> {current_time.strftime('%H:%M:%S')}

<b>🔴 Unassigned:</b> {success_unassign}/{total_unassigned}
<b>🟢 Assigned:</b> {success_assign}/{total_assigned}
{license_summary}

<b>❌ Failed Unassignments:</b>
{format_failed(failed_unassign)}

<b>❌ Failed Assignments:</b>
{format_failed(failed_assign)}

✅ <b>Completed Successfully</b>
"""

    send_telegram_message(summary)

    print("\n" + "=" * 50)
    print("✅ License management completed!")


if __name__ == "__main__":
    manage_licenses()
