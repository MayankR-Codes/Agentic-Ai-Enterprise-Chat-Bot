# Backend module initialization
from .agent import get_agent
from .rag_engine import load_vector_db
from .tools import create_it_ticket, schedule_meeting, issue_detector
from .prompts import AGENT_SYSTEM_PROMPT, ISSUE_DETECTION_PROMPT

__all__ = [
    'get_agent',
    'load_vector_db',
    'create_it_ticket',
    'schedule_meeting',
    'issue_detector',
    'AGENT_SYSTEM_PROMPT',
    'ISSUE_DETECTION_PROMPT'
]
