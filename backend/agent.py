import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.tools import create_it_ticket, schedule_meeting, issue_detector
from backend.prompts import AGENT_SYSTEM_PROMPT, ISSUE_DETECTION_PROMPT
from backend.rag_engine import load_vector_db
import json
from dotenv import load_dotenv

# Initialize LLM
load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

def detect_issue(user_query: str) -> dict:
    """
    Classify query as ISSUE or INFORMATIONAL
    Returns: {"type": "issue" or "query", "severity": "high/medium/low", "category": "..."}
    """
    classification_prompt = ISSUE_DETECTION_PROMPT.format(query=user_query)
    
    try:
        response = llm.invoke(classification_prompt)
        result = json.loads(response.content)
        return result
    except Exception as e:
        # If JSON parsing fails, default to query
        return {"type": "query", "severity": "low", "category": "unknown"}


def get_agent():
    """
    Returns an agent-like object that can process queries and execute tools.
    Uses a simpler approach without AgentExecutor for compatibility.
    """
    # 1️⃣ Gemini LLM
    llm_instance = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    # 2️⃣ Load FAISS vector DB
    try:
        vector_db = load_vector_db()
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    except Exception as e:
        print(f"⚠️ Vector DB not found: {e}")
        retriever = None

    # 3️⃣ Create a simple agent wrapper
    class SimpleAgent:
        def __init__(self, llm, retriever):
            self.llm = llm
            self.retriever = retriever

        def invoke(self, input_dict, *args, **kwargs):
            """Process user query and route to appropriate tool/RAG.

            Accepts either a dict with an `input` key or a plain string.
            Accepts and ignores extra kwargs (e.g. `return_intermediate_steps`) passed
            by calling frameworks to maintain compatibility.
            """
            # Support being called with a plain string instead of a dict
            if isinstance(input_dict, str):
                user_query = input_dict
            else:
                user_query = input_dict.get("input", "")
            
            # Classify if it's an issue
            issue_check = detect_issue(user_query)
            
            if issue_check.get("type") == "issue":
                # Handle as issue - create ticket or schedule meeting
                if "meeting" in user_query.lower() or "hr" in user_query.lower():
                    result = schedule_meeting(
                        department="HR",
                        reason=user_query,
                        user_name="User",
                        user_email=""
                    )
                else:
                    result = create_it_ticket(
                        issue=user_query,
                        user_name="User",
                        user_email=""
                    )
                return {"output": json.dumps(result)}
            else:
                # Handle as query - use RAG
                if self.retriever:
                    docs = self.retriever.invoke(user_query)
                    doc_texts = [d.page_content if hasattr(d, 'page_content') else str(d) for d in docs]
                    context = "\n---\n".join(doc_texts[:3])
                    
                    # Generate answer with LLM using context
                    prompt = f"""Based on the following context, answer the question:

Context:
{context}

Question: {user_query}

Answer: """
                    response = self.llm.invoke(prompt)
                    return {"output": response.content}
                else:
                    return {"output": "Knowledge base unavailable. Please check your system."}
    
    agent = SimpleAgent(llm_instance, retriever)
    return agent
