def create_it_ticket(issue: str):
    return {
        "action": "create_it_ticket",
        "issue": issue,
        "status": "submitted"
    }

def schedule_meeting(department: str, date: str, time: str):
    return {
        "action": "schedule_meeting",
        "department": department,
        "date": date,
        "time": time
    }
