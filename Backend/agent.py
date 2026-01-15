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
    model="llama-3.1-8b-instant",   # ✅ ACTIVE + FREE
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

    def __init__(self):
        try:
            self.vector_db = load_vector_db()
            self.retriever = self.vector_db.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 10, "fetch_k": 20}
            )
        except Exception:
            self.retriever = None

        self.pending_action = None


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
            return {
                "output": (
                    "⚠️ I detected this as an issue.\n\n"
                    "Do you want me to proceed?\n"
                    "👉 Reply **yes** or **no**."
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
            return {"output": "✅ Action cancelled. How else can I help?"}

        if action["category"] == "hr_meeting":
            result = schedule_meeting(
                department="HR",
                reason=action["query"],
                user_name="User",
                user_email=""
            )
        else:
            result = create_it_ticket(
                issue=action["query"],
                user_name="User",
                user_email=""
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
                    "⚠️ This question is OUT OF DOCUMENTS - "
                    "I can only answer questions related to the provided enterprise documents."
                )
            }

        context = "\n---\n".join(d.page_content[:1000] for d in docs[:3])
        sources = ", ".join(
            d.metadata.get("source", "Unknown") for d in docs[:3]
        )

        answer_prompt = f"""
Answer ONLY using the context below.

RULES:
- Do NOT use outside knowledge
- If answer is missing, reply exactly:
"⚠️ This question is OUT OF DOCUMENTS - I can only answer questions related to the provided enterprise documents."

Context:
{context}

Question: {query}

Answer:
"""

        response = llm.invoke(answer_prompt)

        return {
            "output": f"{response.content}\n\n📄 Source: {sources}"
        }


# ==================== FACTORY ====================
def get_agent():
    return EnterpriseAgent()
