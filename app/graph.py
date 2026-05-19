import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

from app.tools import (
    search_wiki, search_web, scrape_website,
    get_pending_tasks, search_ideas, save_action_item, save_idea, save_note,
    run_python
)
from app.google_tools import (
    check_google_calendar, create_google_calendar_event,
    read_recent_emails, search_gmail
)

# ─────────────────────────────────────────────
# 1. Global State
# ─────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    phone_number: str
    next: str
    reply_message: str

llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ─────────────────────────────────────────────
# 2. Worker Agents
# ─────────────────────────────────────────────
librarian_agent = create_react_agent(
    llm,
    tools=[search_wiki],
    prompt=(
        "You are the Librarian. You search the user's personal wiki (ChromaDB) "
        "for context from uploaded PDFs and documents. Give a concise, well-formatted "
        "summary of what you find, citing the source document."
    )
)

researcher_agent = create_react_agent(
    llm,
    tools=[search_web, scrape_website],
    prompt=(
        "You are the Researcher. You search the live internet for information. "
        "Use DuckDuckGo to search, and if you find a very promising URL, use "
        "scrape_website to read its full content. Synthesize your findings into "
        "a coherent, well-cited answer."
    )
)

pm_agent = create_react_agent(
    llm,
    tools=[save_action_item, save_idea, save_note, get_pending_tasks, search_ideas],
    prompt=(
        "You are the Project Manager. You interact with the user's SQLite database. "
        "You can save action items, ideas, and notes, or retrieve pending tasks and "
        "ideas based on keywords. Always confirm what you have saved or retrieved."
    )
)

analyst_agent = create_react_agent(
    llm,
    tools=[run_python],
    prompt=(
        "You are the Analyst. You write and execute Python code to answer math, logic, "
        "or data-related questions. You MUST use the run_python tool to execute your code "
        "and get the result before answering. Always call print() so you can see the output."
    )
)

executive_assistant_agent = create_react_agent(
    llm,
    tools=[check_google_calendar, create_google_calendar_event, read_recent_emails, search_gmail],
    prompt=(
        "You are the Executive Assistant. You manage the user's Google Calendar and Gmail. "
        "You can check their schedule for any date, create new calendar events to block time, "
        "read their latest unread emails, and search their inbox for specific threads. "
        "Always confirm actions clearly and format responses in a readable way. "
        "If a tool returns a configuration error, let the user know they need to run the "
        "Google authentication setup first."
    )
)

# ─────────────────────────────────────────────
# 3. Graph Node Adapters
# ─────────────────────────────────────────────
def librarian_node(state: AgentState):
    result = librarian_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"][len(state["messages"]):]}

def researcher_node(state: AgentState):
    result = researcher_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"][len(state["messages"]):]}

def pm_node(state: AgentState):
    sys_msg = SystemMessage(content=f"IMPORTANT: The user's phone_number is {state['phone_number']}. Pass this exact string to your tools.")
    result = pm_agent.invoke({"messages": [sys_msg] + list(state["messages"])})
    return {"messages": result["messages"][len(state["messages"]) + 1:]}

def analyst_node(state: AgentState):
    result = analyst_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"][len(state["messages"]):]}

def executive_assistant_node(state: AgentState):
    result = executive_assistant_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"][len(state["messages"]):]}

# ─────────────────────────────────────────────
# 4. Supervisor Node
# ─────────────────────────────────────────────
class Route(BaseModel):
    next: Literal["Librarian", "Researcher", "ProjectManager", "Analyst", "ExecutiveAssistant", "FINISH"]

supervisor_prompt = """You are a Supervisor orchestrating a team of AI agents.
The user is texting you on WhatsApp. Analyze their request and delegate to the correct worker.

WORKERS:
- Librarian: Searches the user's personal Wiki (uploaded PDFs/documents in ChromaDB).
- Researcher: Searches the live internet and can scrape web pages for full article content.
- ProjectManager: Saves to or reads from the user's SQLite database (action items, tasks, ideas, notes).
- Analyst: Writes and executes Python code for precise math, logic, or data analysis.
- ExecutiveAssistant: Manages Google Calendar (check schedule, create events) and Gmail (read inbox, search emails). Use this for ANY request about calendar, schedule, meetings, or emails.

If the request is fully answered or needs no specialized tools (normal conversation), output FINISH.
"""

def supervisor_node(state: AgentState):
    messages = [SystemMessage(content=supervisor_prompt)] + list(state["messages"])
    response = llm.with_structured_output(Route).invoke(messages)
    return {"next": response.next}

def generate_reply_node(state: AgentState):
    last_msg = state["messages"][-1]
    if isinstance(last_msg, AIMessage) and last_msg.content:
        return {"reply_message": last_msg.content}
    reply = llm.invoke(
        [SystemMessage(content="You are a helpful, conversational AI Second Brain. Respond naturally.")] +
        list(state["messages"])
    )
    return {"reply_message": reply.content}

# ─────────────────────────────────────────────
# 5. Build the Graph
# ─────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Librarian", librarian_node)
workflow.add_node("Researcher", researcher_node)
workflow.add_node("ProjectManager", pm_node)
workflow.add_node("Analyst", analyst_node)
workflow.add_node("ExecutiveAssistant", executive_assistant_node)
workflow.add_node("Reply", generate_reply_node)

workflow.add_edge(START, "Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next"],
    {
        "Librarian":          "Librarian",
        "Researcher":         "Researcher",
        "ProjectManager":     "ProjectManager",
        "Analyst":            "Analyst",
        "ExecutiveAssistant": "ExecutiveAssistant",
        "FINISH":             "Reply",
    }
)

workflow.add_edge("Librarian",          "Supervisor")
workflow.add_edge("Researcher",         "Supervisor")
workflow.add_edge("ProjectManager",     "Supervisor")
workflow.add_edge("Analyst",            "Supervisor")
workflow.add_edge("ExecutiveAssistant", "Supervisor")
workflow.add_edge("Reply",              END)

app_graph = workflow.compile()
