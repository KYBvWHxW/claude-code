from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from llm import chat

class State(TypedDict):
    messages: List[Dict[str, Any]]

def llm_node(state: State) -> State:
    answer = chat(state["messages"])
    return {"messages": state["messages"] + [{"role": "assistant", "content": answer}]}

def build_graph():
    g = StateGraph(State)
    g.add_node("llm", llm_node)
    g.add_edge(START, "llm")
    g.add_edge("llm", END)
    return g.compile()