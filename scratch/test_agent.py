import os
import sys
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

load_dotenv(dotenv_path=os.path.join(parent_dir, '.env'), override=True)

from langchain_core.messages import HumanMessage
from app.graph import app_graph

def test_query(message_text: str):
    print(f"\n[{'-'*40}]")
    print(f"USER: {message_text}")
    print(f"[{'-'*40}]")
    
    initial_state = {
        "messages": [HumanMessage(content=message_text)], 
        "phone_number": "TEST_USER_123"
    }
    
    # We can stream the events to see which agents are called!
    try:
        for event in app_graph.stream(initial_state):
            for node_name, state_update in event.items():
                print(f"\n>>> [Node: {node_name}] Executed <<<")
                
                # If there is a reply_message, this is the final reply node
                if "reply_message" in state_update:
                    print(f"\nFINAL AI REPLY:\n{state_update['reply_message']}")
                
                # If it's the Supervisor routing
                elif "next" in state_update:
                    print(f"Supervisor decided to route to: {state_update['next']}")
                    
                # If it's a worker agent returning a message
                elif "messages" in state_update and state_update["messages"]:
                    last_msg = state_update["messages"][-1]
                    # Print the tool calls or the response
                    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                        print(f"Tool Calls: {last_msg.tool_calls}")
                    elif last_msg.content:
                        print(f"Agent Output: {last_msg.content[:500]}...")
                        
    except Exception as e:
        print(f"Error during graph execution: {e}")

if __name__ == "__main__":
    print("Starting Multi-Agent Architecture Tests...\n")
    
    # Test 1: Analyst Agent (Math)
    test_query("If I invest $1000 at 5% APY compounding daily for 10 years, exactly how much will I have?")
    
    # Test 2: Project Manager (Database)
    test_query("What are my pending tasks?")
    
    # Test 3: Researcher (Web Search + Scrape)
    test_query("Search the web for the latest breaking news about LangGraph Python and summarize it.")
