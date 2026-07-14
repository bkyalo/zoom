# Zoom License Manager

Automated license management system for Zoom that assigns and unassigns licenses based on a predefined schedule.

## Features

- **Automated license management**: Assigns and unassigns Zoom licenses from a database schedule
- **License usage tracking**: Reports total, used, and available licenses
- **Low license alerts**: Warns when available licenses are running low
- **Schedule-based**: Uses teaching/exam schedules from MySQL/MariaDB
- **Monday cleanup**: On Mondays, also clears Friday-only users who are not scheduled today
- **Optional Telegram notifications**: Sends a run summary when Telegram credentials are configured
- **Manual tools**: Bulk unassign from CSV, and assign everyone scheduled for today

## Scheduling with Cron

To run the license manager at 1 AM Monday–Friday:

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add:
   ```
   0 1 * * 1-5 cd /path/to/zoom && /path/to/venv/bin/python app.py >> /var/log/zoom_license_manager.log 2>&1
   ```

   Replace the paths with your project directory and venv Python.

3. (Optional) Tail logs:
   ```bash
   tail -f /var/log/zoom_license_manager.log
   ```

### Log rotation (recommended)

Create `/etc/logrotate.d/zoom-license-manager`:

```
/var/log/zoom_license_manager.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 root root
}
```

## Getting started

### Prerequisites

- Python 3.8+
- Zoom account with admin privileges
- Zoom OAuth app credentials
- MySQL/MariaDB database
- (Optional) Telegram bot for notifications

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:bkyalo/zoom.git
   cd zoom
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and fill in credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your Zoom and database credentials
   ```

## Configuration

Edit `.env` (see `.env.example`):

```ini
# Zoom API Configuration
ZOOM_ACCOUNT_ID=your_zoom_account_id
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret

# Database Configuration
DB_HOST=localhost
DB_USER=your_db_username
DB_PASSWORD=your_db_password
DB_NAME=your_database_name

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

Optional (not required to run):

```ini
# Telegram notifications (skipped if unset)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

## Usage

Daily automation:

```bash
python app.py
# or
./run.sh
```

### Single-user CLI

```bash
python assign.py user@example.com
python unassign.py user@example.com
```

### Manual license management

#### 1. Massive unassignment

Bulk-clear licenses from users listed in `zoomus_users.csv` (e.g. end of semester).

- Dry run:
  ```bash
  python3 unassign_massive.py
  ```
- Execute:
  ```bash
  python3 unassign_massive.py --execute
  ```

#### 2. Today's schedule assignment

Assign licenses to everyone scheduled for today (full set, not a diff):

- Dry run:
  ```bash
  python3 assign_today.py
  ```
- Execute:
  ```bash
  python3 assign_today.py --execute
  ```

### License usage

Each run reports total / used / available licenses and warns when fewer than 10% remain.

```python
from assign import get_license_usage

usage = get_license_usage()
if usage:
    print(f"Total: {usage['total_licenses']}")
    print(f"Used: {usage['used_licenses']}")
    print(f"Available: {usage['available_licenses']}")
```

### Expected output

```
🚀 Starting license management...
==================================================
📅 Today is: Friday
📅 Yesterday was: Thursday

📋 Fetching schedule...
✅ Successfully connected to the database.

📊 License Usage:
• Total Licenses: 100
• Used Licenses: 85
• Available Licenses: 15

📊 Summary:
- Found 5 users to unassign
- Found 3 users to assign

🔴 Unassigning licenses for 5 users...
1. Unassigning from user1@example.com... ✅ Done
...

🟢 Assigning licenses to 3 users...
1. Assigning to newuser@example.com... ✅ Done
...

==================================================
✅ License management completed!
```

## License management rules

1. Users are assigned licenses from the database schedule for the current day
2. Users scheduled yesterday but not today have licenses unassigned
3. On Monday, Friday-only users who are not on today's schedule are also unassigned
4. If Telegram credentials are set, a summary is sent after each run

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python
- Uses the Zoom API for license management
