
import datetime
import json
import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from tavily import TavilyClient


load_dotenv()

tavily = TavilyClient(
    api_key=os.environ["TAVILY_API_KEY"]
)

# 1. Define tools

@tool
def get_system_time() -> str:
    """Return the current date and time."""

    return datetime.datetime.now().isoformat()


@tool
def web_search(query: str) -> str:
    """Search the web for current information."""

    response = tavily.search(
        query=query,
        max_results=3,
    )

    return json.dumps(response["results"])


tools = [
    get_system_time,
    web_search,
]


# 2. Give the tools to the model

llm = ChatOpenAI(
    model="gpt-6-astra",
    use_responses_api=True,
)

llm_with_tools = llm.bind_tools(tools)


# 3. Reasoning node

def reason(state: MessagesState):
    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {"messages": [response]}


# 4. Build the ReAct graph

graph = StateGraph(MessagesState)

graph.add_node("reason", reason)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "reason")

# If the model requested a tool, go to "tools".
# Otherwise, end the graph.
graph.add_conditional_edges(
    "reason",
    tools_condition,
)

# After executing a tool, return to the model.
graph.add_edge("tools", "reason")

app = graph.compile()


# 5. Run the agent

result = app.invoke(
    {
        "messages": [
            HumanMessage(
                content=(
                    "How many days ago was the latest "
                    "SpaceX launch?"
                )
            )
        ]
    }
)

final_message = result["messages"][-1]

print(final_message.text)