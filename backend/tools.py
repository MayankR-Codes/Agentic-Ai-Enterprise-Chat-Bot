import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# ============ TICKET DATABASE (In-Memory) ============
TICKETS_DB = []
MEETINGS_DB = []

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
    
    Args:
        issue: Description of the IT issue
        user_name: Name of the person reporting
        user_email: Email for updates
    
    Returns:
        Ticket confirmation with ID
    """
    ticket_id = f"TICKET-{len(TICKETS_DB) + 1001}"
    timestamp = datetime.now().isoformat()
    
    ticket = {
        "ticket_id": ticket_id,
        "issue": issue,
        "user_name": user_name,
        "user_email": user_email,
        "status": "OPEN",
        "priority": "MEDIUM",
        "created_at": timestamp,
        "assigned_to": "IT Support Team"
    }
    
    TICKETS_DB.append(ticket)
    
    # Send confirmation email
    email_body = f"""
    <h2>IT Support Ticket Created</h2>
    <p><strong>Ticket ID:</strong> {ticket_id}</p>
    <p><strong>Issue:</strong> {issue}</p>
    <p><strong>Status:</strong> OPEN</p>
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
    
    Args:
        department: Department to meet (HR, Management, etc.)
        date: Preferred date (YYYY-MM-DD)
        time: Preferred time (HH:MM)
        reason: Reason for meeting
        user_name: Name of person scheduling
        user_email: Email for confirmation
    
    Returns:
        Meeting confirmation with ID
    """
    meeting_id = f"MEETING-{len(MEETINGS_DB) + 2001}"
    timestamp = datetime.now().isoformat()
    
    meeting = {
        "meeting_id": meeting_id,
        "department": department,
        "date": date or "To be scheduled",
        "time": time or "To be scheduled",
        "reason": reason,
        "user_name": user_name,
        "user_email": user_email,
        "status": "PENDING",
        "created_at": timestamp
    }
    
    MEETINGS_DB.append(meeting)
    
    # Send email to HR
    email_body = f"""
    <h2>New Meeting Request</h2>
    <p><strong>Meeting ID:</strong> {meeting_id}</p>
    <p><strong>Department:</strong> {department}</p>
    <p><strong>Requested Date:</strong> {date or 'TBD'}</p>
    <p><strong>Requested Time:</strong> {time or 'TBD'}</p>
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
    it_keywords = ["error", "crash", "bug", "not working", "broken", "system down", "issue"]
    hr_keywords = ["meeting", "hr", "schedule", "appointment", "complaint", "issue", "problem"]
    
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
    for ticket in TICKETS_DB:
        if ticket["ticket_id"] == ticket_id:
            return ticket
    return {"error": "Ticket not found"}


def get_all_tickets() -> list:
    """Get all tickets (for admin dashboard)"""
    return TICKETS_DB


def get_all_meetings() -> list:
    """Get all meeting requests (for HR dashboard)"""
    return MEETINGS_DB
