import requests
import base64
from config import Config
from typing import Dict, Optional, Tuple

# Step 1: Get an access token
def get_access_token():
    url = Config.ZOOM_AUTH_URL
    auth_string = f"{Config.ZOOM_CLIENT_ID}:{Config.ZOOM_CLIENT_SECRET}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # URL-encoded form data
    data = f"grant_type=account_credentials&account_id={Config.ZOOM_ACCOUNT_ID}"
    
    # Debug output (commented out by default for security)
    # print("\n🔍 Debug Info:")
    # print(f"Account ID: {Config.ZOOM_ACCOUNT_ID}")
    # print(f"Client ID: {Config.ZOOM_CLIENT_ID}")
    # print(f"Auth Header: Basic {'*' * 20}")
    # print(f"Request Data: {data}\n")
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print("❌ Failed to fetch token:")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        raise

# Step 2: Assign license by setting type=2 (Licensed user)
def get_license_usage():
    """
    Get information about license usage
    
    Returns:
        dict: Dictionary containing total_licenses, used_licenses, and available_licenses
    """
    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get account plan information which includes license counts
        response = requests.get(
            f"{Config.ZOOM_API_BASE_URL}/accounts/me/plans",
            headers=headers
        )
        response.raise_for_status()
        
        plan_data = response.json()
        
        # Find the plan that contains license information
        for plan in plan_data.get('plans', []):
            if plan.get('type') == 2:  # 2 represents the main plan with licenses
                total_licenses = plan.get('hosts', 0)
                break
        else:
            total_licenses = 0
            
        # Get number of active users with licenses
        users_response = requests.get(
            f"{Config.ZOOM_API_BASE_URL}/users?status=active&page_size=300&page_number=1",
            headers=headers
        )
        users_response.raise_for_status()
        
        users_data = users_response.json()
        used_licenses = sum(1 for user in users_data.get('users', []) 
                           if user.get('type') == 2)  # Type 2 is licensed user
        
        return {
            'total_licenses': total_licenses,
            'used_licenses': used_licenses,
            'available_licenses': max(0, total_licenses - used_licenses)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to get license usage: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        return None

def assign_license(user_email, license_type=2, quiet=False):
    """
    Assign a Zoom license to a user
    
    Args:
        user_email (str): Email of the user to assign license to
        license_type (int, optional): Type of license to assign. Defaults to 2 (Licensed user).
                                     1: Basic (Free)
                                     2: Licensed (Paid)
                                     3: On-premise
        quiet (bool): If True, suppress success/failure prints
    """
    token = get_access_token()
    url = f"https://api.zoom.us/v2/users/{user_email}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Payload to assign a license (type=2 for Licensed user)
    payload = {
        "type": license_type
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        if response.status_code == 204:
            if not quiet:
                print(f"✅ License assigned successfully for {user_email}")
            return True
        else:
            if not quiet:
                print(f"❌ Failed to assign license: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        if not quiet:
            print(f"❌ Error assigning license: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python assign.py <user_email>")
        sys.exit(1)
    assign_license(sys.argv[1])
    
    # Example of getting license usage
    usage = get_license_usage()
    if usage:
        print(f"\n📊 License Usage:")
        print(f"Total Licenses: {usage['total_licenses']}")
        print(f"Used Licenses: {usage['used_licenses']}")
        print(f"Available Licenses: {usage['available_licenses']}")
