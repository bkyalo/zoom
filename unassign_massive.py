import csv
import sys
import argparse
from config import Config
from unassign import unassign_license

def read_users_from_csv(csv_path):
    users = []
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        sys.exit(1)
    return users

def mass_unassign(csv_path, dry_run=True):
    users = read_users_from_csv(csv_path)
    exempt_users = [email.lower() for email in Config.EXEMPT_USERS]
    
    to_unassign = []
    skipped_exempt = []
    skipped_basic = []
    
    for user in users:
        email = user.get('Email', '').lower()
        license_info = user.get('Licenses', '')
        
        if not email:
            continue
            
        if email in exempt_users:
            skipped_exempt.append(email)
            continue
            
        # Check if already basic (to minimize API calls)
        if "Basic" in license_info:
            skipped_basic.append(email)
            continue
            
        to_unassign.append(email)
    
    print(f"\n--- Mass Unassign Report (Dry Run: {dry_run}) ---")
    print(f"Total users in CSV: {len(users)}")
    print(f"Users found in exempt list: {len(skipped_exempt)}")
    print(f"Users already on Basic license: {len(skipped_basic)}")
    print(f"Users to be unassigned: {len(to_unassign)}")
    
    if dry_run:
        print("\n📝 Dry Run results (no changes made):")
        for email in to_unassign:
            print(f"  - WOULD UNASSIGN: {email}")
        print("\nRun with --execute to perform the actual unassignment.")
        return

    print("\n🚀 Starting actual unassignment...")
    success_count = 0
    fail_count = 0
    
    for email in to_unassign:
        print(f"🔄 Unassigning {email}...", end=" ", flush=True)
        if unassign_license(email):
            print("✅")
            success_count += 1
        else:
            print("❌")
            fail_count += 1
            
    print(f"\n--- Final Results ---")
    print(f"✅ Successfully unassigned: {success_count}")
    print(f"❌ Failed: {fail_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unassign Zoom licenses from users in a CSV file.")
    parser.add_argument("--csv", default="zoomus_users.csv", help="Path to the users CSV file")
    parser.add_argument("--execute", action="store_true", help="Perform the actual unassignment (default is dry-run)")
    
    args = parser.parse_args()
    
    mass_unassign(args.csv, dry_run=not args.execute)
