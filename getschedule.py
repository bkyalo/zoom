import mysql.connector
from mysql.connector import Error
from collections import defaultdict
from config import Config
from datetime import datetime, timedelta

def get_exam_users_for_date(connection, target_date):
    """
    Checks if the target_date falls within an active exam period and fetches
    the assigned users (invigilators) for that specific date.
    
    Args:
        connection: Active MySQL connection.
        target_date (date): The date to check (datetime.date object).
        
    Returns:
        list: List of user emails if exam exists, else None.
    """
    cursor = connection.cursor()
    
    # 1. Check if the date is within an active exam schedule
    # We check if there exists an active schedule where target_date is between start and end
    check_schedule_query = """
    SELECT id 
    FROM exam_schedules 
    WHERE is_active = 1 
      AND %s BETWEEN start_date AND end_date
    LIMIT 1;
    """
    
    cursor.execute(check_schedule_query, (target_date,))
    schedule_row = cursor.fetchone()
    
    if not schedule_row:
        return None
        
    schedule_id = schedule_row[0]
    # print(f"DEBUG: Found active exam schedule ID: {schedule_id} for date {target_date}")
    
    # 2. Fetch users assigned to exams on this specific date for this schedule
    # Join with users table to get emails
    exam_users_query = """
    SELECT DISTINCT u.email
    FROM exams e
    JOIN users u ON e.user_id = u.id
    WHERE e.exam_schedule_id = %s
      AND e.exam_date = %s
      AND u.email IS NOT NULL;
    """
    
    cursor.execute(exam_users_query, (schedule_id, target_date))
    rows = cursor.fetchall()
    
    if not rows:
        return [] # Exam period active, but no exams scheduled for this specific day? Return empty list to override teaching schedule.
        
    return [row[0] for row in rows]

def check_exam_period(target_date=None):
    """
    Checks if the given date (default today) falls within an active exam period.
    
    Returns:
        bool: True if active exam period, False otherwise.
    """
    if target_date is None:
        target_date = datetime.now()
        
    connection = None
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            check_schedule_query = """
            SELECT id 
            FROM exam_schedules 
            WHERE is_active = 1 
              AND %s BETWEEN start_date AND end_date
            LIMIT 1;
            """
            cursor.execute(check_schedule_query, (target_date,))
            return cursor.fetchone() is not None
            
    except Error as e:
        print(f"❌ Error checking exam period: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            connection.close()

def get_email_schedule():
    """
    Connects to the database, fetches user emails mapped to days,
    and returns them as a dictionary.
    
    Prioritizes Exam Schedule over Teaching Schedule:
    - If today/yesterday is an Exam Day, returns exam users.
    - Otherwise, returns standard teaching schedule users.
    """
    # Use defaultdict to easily append to lists
    schedule = defaultdict(list)
    connection = None  # Initialize connection to None
    
    # The SQL query joins the tables to get unique user emails by day for academic session 2
    teaching_query = """
    SELECT DISTINCT
        d.id AS day_id,
        d.name AS day_name,
        u.email AS user_email
    FROM 
        course_unit_programme_mappings AS m
    JOIN 
        users AS u ON m.user_id = u.id
    JOIN 
        days AS d ON m.day_id = d.id
    WHERE 
        m.academic_session_id = 5
    ORDER BY
        d.id, u.email;
    """

    try:
        # Establish the database connection using Config
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # --- 1. Fetch Standard Teaching Schedule (Baseline) ---
            cursor.execute(teaching_query)
            rows = cursor.fetchall()
            
            for row in rows:
                _, day_name, user_email = row
                schedule[day_name].append(user_email)
            
            # --- 2. Check and Override for Exam Schedule ---
            # We need to check specifically for 'today' and 'yesterday' because
            # the license logic depends on these two days.
            
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            
            # Helper to process a specific date
            def process_exam_override(date_obj):
                exam_users = get_exam_users_for_date(connection, date_obj.date())
                
                if exam_users is not None:
                    day_name_full = date_obj.strftime('%A') # e.g., "Monday"
                    # Replace teaching schedule for that day with exam users
                    schedule[day_name_full] = exam_users
                    
            process_exam_override(today)
            process_exam_override(yesterday)
            
            return schedule

    except Error as e:
        print(f"❌ Error while connecting to MySQL: {e}")
        return None
        
    finally:
        # Ensure the connection is closed
        if connection and connection.is_connected():
            connection.close()


def print_schedule(schedule):
    """Formats and prints the schedule to the console."""
    if not schedule:
        print("\nNo schedule to display.")
        return

    print("\n--- User Email Schedule ---")
    for day, emails in schedule.items():
        print(f"\n🗓️ {day.upper()}")
        print("-" * (len(day) + 3))
        if emails:
            for email in emails:
                print(f"  - {email}")
        else:
             print("  - (No users scheduled)")
    print("\n---------------------------\n")


if __name__ == "__main__":
    # 1. Fetch the data from the database
    email_schedule = get_email_schedule()
    
    # 2. Print the formatted schedule
    if email_schedule:
        print_schedule(email_schedule)