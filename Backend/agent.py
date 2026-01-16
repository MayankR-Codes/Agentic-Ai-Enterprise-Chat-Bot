import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

from .prompts import ISSUE_DETECTION_PROMPT
from .tools import create_it_ticket, schedule_meeting
from .rag_engine import load_vector_db


# ==================== ENV ====================
load_dotenv(override=True)

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY missing")


# ==================== LLM (SUPPORTED MODEL) ====================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",   # ✅ ACTIVE + FREE
    temperature=0,
    groq_api_key=API_KEY,
)

def create_llm():
    models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    for model in models:
        try:
            return ChatGroq(
                model=model,
                temperature=0,
                groq_api_key=os.getenv("GROQ_API_KEY"),
            )
        except Exception:
            continue

    raise RuntimeError("No supported Groq model found")

llm = create_llm()

# ==================== AGENT ====================
class EnterpriseAgent:
    """
    Single-entry enterprise agent:
    - Intent detection
    - Issue confirmation
    - RAG-based answering
    """

    def __init__(self, user_info: dict = None):
        try:
            self.vector_db = load_vector_db()
            self.retriever = self.vector_db.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 10, "fetch_k": 20}
            )
        except Exception:
            self.retriever = None

        self.pending_action = None
        self.user_info = user_info or {}


    # ==================== MAIN ENTRY ====================
    def invoke(self, user_input: str) -> dict:
        """
        EXACTLY ONE LLM CALL per user message
        """

        # 1️⃣ Confirmation flow (NO LLM CALL)
        if self.pending_action:
            return self._handle_confirmation(user_input)

        # 2️⃣ Intent detection (ONE LLM CALL)
        prompt = ISSUE_DETECTION_PROMPT.format(query=user_input)

        try:
            response = llm.invoke(prompt)
            raw = response.content.strip()

            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("No JSON found")

            decision = json.loads(raw[start:end + 1])

        except Exception:
            decision = {
                "type": "query",
                "severity": "low",
                "category": "general_query",
                "requires_action": False,
                "has_abuse": False
            }

        # 3️⃣ Abuse handling
        if decision.get("has_abuse"):
            return {
                "output": (
                    "I cannot assist with that request. "
                    "Please keep our conversation professional and respectful."
                )
            }

        # 4️⃣ ISSUE FLOW
        if decision["type"] == "issue" and decision["requires_action"]:
            self.pending_action = {
                "category": decision.get("category"),
                "query": user_input
            }
            
            action_text = "schedule an HR meeting" if decision.get("category") == "hr_meeting" else "create an IT ticket"
            
            return {
                "output": (
                    f"I'll help you {action_text}.\n\n"
                    "Do you want me to proceed?\n"
                    "Reply **yes** or **no**."
                )
            }

        # 5️⃣ QUERY FLOW (RAG)
        return self._handle_query(user_input)


    # ==================== CONFIRMATION ====================
    def _handle_confirmation(self, reply: str) -> dict:
        reply = reply.lower().strip()

        if reply not in ("yes", "no"):
            return {"output": "Please reply with **yes** or **no**."}

        action = self.pending_action
        self.pending_action = None

        if reply == "no":
            return {"output": "Action cancelled. How else can I help?"}

        # Get user information
        user_name = self.user_info.get('full_name', 'User')
        user_email = self.user_info.get('email', '')
        user_id = self.user_info.get('id', None)

        if action["category"] == "hr_meeting":
            result = schedule_meeting(
                department="HR",
                reason=action["query"],
                user_name=user_name,
                user_email=user_email,
                user_id=user_id
            )
        else:
            result = create_it_ticket(
                issue=action["query"],
                user_name=user_name,
                user_email=user_email,
                user_id=user_id
            )

        return {"output": result["message"]}


    # ==================== QUERY HANDLER ====================
    def _handle_query(self, query: str) -> dict:
        if not self.retriever:
            return {"output": "Knowledge base unavailable."}

        docs = self.retriever.invoke(query)

        if not docs:
            return {
                "output": (
                    "This question is OUT OF DOCUMENTS - "
                    "I can only answer questions related to the provided enterprise documents."
                )
            }

        # Build context with page information for each chunk
        context_with_pages = ""
        for idx, d in enumerate(docs[:3], 1):
            page = d.metadata.get("page", "N/A")
            content = d.page_content[:800]
            context_with_pages += f"(Page {page})\n{content}\n\n---\n\n"

        answer_prompt = f"""
You are an expert enterprise assistant. Provide clear, well-structured answers using the context provided.

INSTRUCTIONS:
1. Answer ONLY using the context below - do NOT use outside knowledge
2. Format your response as follows:
   - Start with a brief summary paragraph (2-3 sentences) that answers the main question
   - Then provide key details in bullet points below
3. FOR EACH FACT IN BULLET POINTS: Include [Page X] citation showing the page number where that information comes from
4. Keep each bullet point focused on one key piece of information
5. Be professional and informative

CITATION FORMAT:
- Add [Page X] at the end of each bullet point with the actual page number
- Example: "Total complaints reported: 44 [Page 12]"
- Example: "Percentage of female employees: 0.09% [Page 3]"
- Example: "Policy details in Corporate Governance Report [Page 8]"

RULES:
- Do NOT use outside knowledge
- ALWAYS include [Page X] citations in bullet points for all factual statements
- Start with a summary paragraph, then use bullet points with page citations
- If the answer is completely missing from context, reply exactly:
"This question is OUT OF DOCUMENTS - I can only answer questions related to the provided enterprise documents."

Context with Page Numbers:
{context_with_pages}

Question: {query}

Answer:
"""

        response = llm.invoke(answer_prompt)

        return {
            "output": response.content
        }


# ==================== FACTORY ====================
def get_agent(user_info: dict = None):
    return EnterpriseAgent(user_info=user_info)
