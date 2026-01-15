import json
import smtplib
import sqlite3
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# ============ DB CONFIGURATION ============
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "enterprise_db.sqlite")

def init_db():
    """Initialize the SQLite database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create Tickets Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        issue TEXT,
        user_name TEXT,
        user_email TEXT,
        status TEXT,
        priority TEXT,
        assigned_to TEXT,
        created_at TEXT
    )
    """)
    
    # Create Meetings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meetings (
        meeting_id TEXT PRIMARY KEY,
        department TEXT,
        date TEXT,
        time TEXT,
        reason TEXT,
        user_name TEXT,
        user_email TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    
    conn.commit()
    conn.close()

# Initialize DB on module load (or call explicitly from app.py)
init_db()

# ============ EMAIL CONFIGURATION ============
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
HR_EMAIL = os.getenv("HR_EMAIL", "hr@hcltech.com")

def send_email(recipient: str, subject: str, body: str) -> bool:
    """Send email notification"""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠️ Email credentials not configured. Skipping email.")
        return False
    
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False


def create_it_ticket(issue: str, user_name: str = "User", user_email: str = "") -> dict:
    """
    Create an IT support ticket
    """
    # Generate ID
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Simple ID generation logic based on count
    cursor.execute("SELECT COUNT(*) FROM tickets")
    count = cursor.fetchone()[0]
    ticket_id = f"TICKET-{count + 1001}"
    
    timestamp = datetime.now().isoformat()
    status = "OPEN"
    priority = "MEDIUM"
    assigned_to = "IT Support Team"
    
    cursor.execute("""
        INSERT INTO tickets (ticket_id, issue, user_name, user_email, status, priority, assigned_to, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (ticket_id, issue, user_name, user_email, status, priority, assigned_to, timestamp))
    
    conn.commit()
    conn.close()
    
    # Send confirmation email
    email_body = f"""
    <h2>IT Support Ticket Created</h2>
    <p><strong>Ticket ID:</strong> {ticket_id}</p>
    <p><strong>Issue:</strong> {issue}</p>
    <p><strong>Status:</strong> {status}</p>
    <p><strong>Created:</strong> {timestamp}</p>
    <p>Our IT team will investigate and contact you shortly.</p>
    """
    
    if user_email:
        send_email(user_email, f"IT Ticket {ticket_id} Created", email_body)
    
    return {
        "action": "create_it_ticket",
        "ticket_id": ticket_id,
        "status": "SUBMITTED",
        "message": f"✅ IT ticket {ticket_id} has been created. Our support team will contact you shortly."
    }


def schedule_meeting(
    department: str,
    date: str = "",
    time: str = "",
    reason: str = "",
    user_name: str = "User",
    user_email: str = ""
) -> dict:
    """
    Schedule a meeting with HR or other department
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM meetings")
    count = cursor.fetchone()[0]
    meeting_id = f"MEETING-{count + 2001}"
    
    timestamp = datetime.now().isoformat()
    status = "PENDING"
    date_val = date or "To be scheduled"
    time_val = time or "To be scheduled"
    
    cursor.execute("""
        INSERT INTO meetings (meeting_id, department, date, time, reason, user_name, user_email, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (meeting_id, department, date_val, time_val, reason, user_name, user_email, status, timestamp))
    
    conn.commit()
    conn.close()
    
    # Send email to HR
    email_body = f"""
    <h2>New Meeting Request</h2>
    <p><strong>Meeting ID:</strong> {meeting_id}</p>
    <p><strong>Department:</strong> {department}</p>
    <p><strong>Requested Date:</strong> {date_val}</p>
    <p><strong>Requested Time:</strong> {time_val}</p>
    <p><strong>Reason:</strong> {reason}</p>
    <p><strong>Requester:</strong> {user_name} ({user_email})</p>
    <p>Please review and confirm availability.</p>
    """
    
    send_email(HR_EMAIL, f"Meeting Request {meeting_id}", email_body)
    
    if user_email:
        confirmation_body = f"""
        <h2>Meeting Request Submitted</h2>
        <p><strong>Meeting ID:</strong> {meeting_id}</p>
        <p>Your request has been sent to {department}. You'll receive confirmation shortly.</p>
        """
        send_email(user_email, f"Meeting Request {meeting_id} Submitted", confirmation_body)
    
    return {
        "action": "schedule_meeting",
        "meeting_id": meeting_id,
        "status": "PENDING",
        "message": f"✅ Meeting request {meeting_id} submitted to {department}. You'll receive confirmation email shortly."
    }


def issue_detector(query: str) -> dict:
    """
    Simple rule-based issue detection (can be enhanced with ML)
    Returns classification for routing
    """
    query_lower = query.lower()
    
    # Issue keywords
    it_keywords = ["error", "crash", "bug", "not working", "broken", "system down", "issue", "fail"]
    hr_keywords = ["meeting", "hr", "schedule", "appointment", "complaint", "issue", "problem", "discuss"]
    
    has_it_issue = any(kw in query_lower for kw in it_keywords)
    has_hr_need = any(kw in query_lower for kw in hr_keywords)
    
    if has_it_issue:
        return {"type": "issue", "category": "it_issue", "requires_action": True}
    elif has_hr_need:
        return {"type": "issue", "category": "hr_meeting", "requires_action": True}
    else:
        return {"type": "query", "category": "general_query", "requires_action": False}


def get_ticket_status(ticket_id: str) -> dict:
    """Get status of a support ticket"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return {"error": "Ticket not found"}


def get_all_tickets() -> list:
    """Get all tickets (for admin dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_all_meetings() -> list:
    """Get all meeting requests (for HR dashboard)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM meetings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
