from langgraph.graph.message import MessagesState
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, MessagesState, StateGraph

load_dotenv()

# Prompts

# system -> define behaviour
# human -> prompt
# ai -> prev ai response

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a Twitter tech influencer assistant tasked with writing "
            "excellent Twitter posts. Generate the best Twitter post possible "
            "for the user's request. If the user provides critique, respond "
            "with a revised version of your previous attempt.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a viral Twitter influencer grading a tweet. Generate "
            "critique and recommendations for the tweet. Provide detailed "
            "recommendations about length, virality, style, clarity, and impact.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


# Model and chains

llm = ChatOpenAI(model="gpt-6-astra")

generation_chain = generation_prompt | llm
reflection_chain = reflection_prompt | llm


# Graph nodes

def generate_node(state: MessagesState):
    response = generation_chain.invoke(
        {"messages": state["messages"]}
    )

    return {"messages": [response]}


def reflect_node(state: MessagesState):
    response = reflection_chain.invoke(
        {"messages": state["messages"]}
    )

    # HumanMessage makes the critique look like feedback
    # given back to the tweet generator.
    return {
        "messages": [
            HumanMessage(content=response.content)
        ]
    }


def should_continue(state: MessagesState):
    if len(state["messages"]) > 6:
        return END

    return "reflect"


# Build the graph

graph = StateGraph[MessagesState, None, MessagesState, MessagesState](MessagesState)

graph.add_node("generate", generate_node)
graph.add_node("reflect", reflect_node)

graph.add_edge(START, "generate")
graph.add_conditional_edges("generate", should_continue)
graph.add_edge("reflect", "generate")

app = graph.compile()


# Run the reflection loop

result = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="AI agents taking over content creation"
            )
        ]
    }
)

print(result["messages"][-1].content)