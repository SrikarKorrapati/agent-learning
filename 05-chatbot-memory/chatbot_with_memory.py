import json
from langgraph.graph.message import MessagesState
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from tavily import TavilyClient


load_dotenv()

DATABASE_PATH = Path(__file__).with_name("chatbot.sqlite")


# Web search client

tavily = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)

# Tools

@tool
def web_search(query: str) -> str:
    """Search the web for current information."""

    response = tavily.search(
        query=query,
        max_results=3,
    )

    return json.dumps(response["results"])


tools = [web_search]


# Model

llm = ChatOpenAI(
    model="gpt-6-astra",
    use_responses_api=True,
)

llm_with_tools = llm.bind_tools(tools)


# Chatbot node

def chatbot(state: MessagesState):
    messages = [
        SystemMessage(
            content=(
                "You are a helpful assistant. "
                "Use web search when current information "
                "is required."
            )
        ),
        *state["messages"],
    ]

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


# Persistent memory

connection = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False,
)

memory = SqliteSaver(connection)


# Build graph

graph = StateGraph[MessagesState, None, MessagesState, MessagesState](MessagesState)

graph.add_node("chatbot", chatbot)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "chatbot")

graph.add_conditional_edges(
    "chatbot",
    tools_condition,
)

graph.add_edge("tools", "chatbot")

app = graph.compile(
    checkpointer=memory
)


# Conversation identity

config = {
    "configurable": {
        "thread_id": "user-1"
    }
}


# Chat loop

while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "end"]:
        break

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ]
        },
        config=config,
    )

    print("AI:", result["messages"][-1].text)
