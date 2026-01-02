from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.tools import create_it_ticket, schedule_meeting
from backend.prompts import AGENT_SYSTEM_PROMPT
from backend.rag_engine import load_vector_db


def get_agent():
    # 1️⃣ Gemini LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0
    )

    # 2️⃣ Load FAISS vector DB
    vector_db = load_vector_db()
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    # 3️⃣ Tools
    tools = [
        Tool(
            name="IT Ticket Tool",
            func=create_it_ticket,
            description="Use when user reports IT issues or system problems"
        ),
        Tool(
            name="Meeting Scheduler",
            func=schedule_meeting,
            description="Use when user asks to schedule or arrange a meeting"
        ),
        Tool(
            name="Company Knowledge Base",
            func=retriever.invoke,
            description="Use to answer questions from internal company documents"
        )
    ]

    # 4️⃣ ReAct prompt (MANDATORY in new LangChain)
    prompt = PromptTemplate.from_template(
        AGENT_SYSTEM_PROMPT + """
        
        You have access to the following tools:
        {tools}

        Use the following format:

        Question: {input}
        Thought: think step by step
        Action: the action to take
        Action Input: the input to the action
        Observation: the result
        Final Answer: the final response

        Begin!

        Question: {input}
        Thought:
        """
    )

    # 5️⃣ Create agent
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # 6️⃣ Executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True
    )

    return agent_executor
