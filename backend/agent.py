import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from .prompts import ISSUE_DETECTION_PROMPT
from .tools import create_it_ticket, schedule_meeting
from .rag_engine import load_vector_db


# ==================== ENVIRONMENT SETUP ====================
load_dotenv(override=True)

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY missing")


# ==================== LLM INITIALIZATION ====================
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
    google_api_key=API_KEY,
)


# ==================== ENTERPRISE AGENT CLASS ====================
class EnterpriseAgent:
    """
    Main agent class that handles:
    1. Intent classification (ISSUE vs QUERY)
    2. Action confirmation for issues
    3. RAG-based query answering
    """

    def __init__(self):
        """Initialize the agent with vector database and retriever."""
        try:
            self.vector_db = load_vector_db()
            # MMR (Maximum Marginal Relevance) retriever for better document ranking
            self.retriever = self.vector_db.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 10, "fetch_k": 20}
            )
        except Exception:
            self.retriever = None

        self.pending_action = None  # For confirmation flow

    # ==================== MAIN ENTRY POINT ====================
    def invoke(self, user_input: str) -> dict:
        """
        Main entry point for processing user queries.
        Ensures exactly ONE LLM call per invocation.
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with 'output' key containing response text
        """

        # Step 1: Handle confirmation if pending
        if self.pending_action:
            return self._handle_confirmation(user_input)

        # Step 2: Classify intent (ISSUE or QUERY)
        prompt = ISSUE_DETECTION_PROMPT.format(query=user_input)

        try:
            response = llm.invoke(prompt)
            raw = response.content.strip()

            # Extract JSON from response
            start = raw.find("{")
            end = raw.rfind("}")

            if start == -1 or end == -1:
                raise ValueError(f"No JSON found in response: {raw[:100]}")

            json_str = raw[start:end + 1]
            decision = json.loads(json_str)

            # Validate required fields
            if "type" not in decision or "requires_action" not in decision:
                raise ValueError("Missing required fields in JSON")

        except Exception as e:
            # Default to QUERY if classification fails
            print(f"Classification error: {e}")
            decision = {
                "type": "query",
                "severity": "low",
                "category": "general_query",
                "requires_action": False
            }

        # Step 3: Handle ISSUE flow
        if decision.get("type") == "issue" and decision.get("requires_action"):
            self.pending_action = {
                "category": decision.get("category"),
                "query": user_input,
            }
            return {
                "output": (
                    "⚠️ I detected this as an issue.\n\n"
                    "Do you want me to proceed?\n"
                    "👉 Reply **yes** or **no**."
                )
            }

        # Step 4: Handle QUERY flow (RAG)
        return self._handle_query(user_input)

    # ==================== CONFIRMATION HANDLER ====================
    def _handle_confirmation(self, reply: str) -> dict:
        """
        Handle user confirmation for issue actions.
        
        Args:
            reply: User's yes/no response
            
        Returns:
            Dictionary with 'output' key containing response
        """
        reply = reply.lower().strip()

        if reply not in ["yes", "no"]:
            return {"output": "Please reply with **yes** or **no**."}

        action = self.pending_action
        self.pending_action = None

        if reply == "no":
            return {"output": "✅ Action cancelled. How else can I help?"}

        # Execute action based on category
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

    # ==================== QUERY HANDLER (RAG) ====================
    def _handle_query(self, query: str) -> dict:
        """
        Handle informational queries using RAG (Retrieval Augmented Generation).
        
        Args:
            query: User's question
            
        Returns:
            Dictionary with 'output' key containing LLM response
        """
        if not self.retriever:
            return {"output": "Knowledge base unavailable."}

        # Retrieve relevant documents
        docs = self.retriever.invoke(query)
        context = "\n---\n".join(d.page_content for d in docs[:3])

        # Build answer prompt
        answer_prompt = f"""
Answer using ONLY the context below.
If not found, say: "Information not found in documents."

Context:
{context}

Question: {query}
"""

        response = llm.invoke(answer_prompt)
        return {"output": response.content}


# ==================== FACTORY FUNCTION ====================
def get_agent() -> EnterpriseAgent:
    """
    Factory function to create and return an EnterpriseAgent instance.
    
    Returns:
        EnterpriseAgent: Initialized agent instance
    """
    return EnterpriseAgent()