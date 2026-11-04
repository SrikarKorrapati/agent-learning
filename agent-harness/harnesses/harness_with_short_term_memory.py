import sqlite3
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, MessagesState, StateGraph


load_dotenv()

model = ChatOpenAI(
    model="gpt-6-astra",
    use_responses_api=True,
)


def chatbot(state: MessagesState):
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        *state["messages"],
    ]

    response = model.invoke(messages)

    return {"messages": [response]}


# SQLite checkpointer

database_path = (
    Path(__file__).parent.parent
    / "runtime"
    / "checkpoints.sqlite"
)

database = sqlite3.connect(
    database_path,
    check_same_thread=False,
)

checkpointer = SqliteSaver(database)


# Graph

graph = StateGraph(MessagesState)

graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

app = graph.compile(checkpointer=checkpointer)


# The thread ID connects multiple calls to one conversation.

config = {
    "configurable": {
        "thread_id": "user-1",
    }
}


def ask(prompt):
    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=prompt)
            ]
        },
        config=config,
    )

    print("AI:", result["messages"][-1].text)


# Two turns create multiple checkpoints and writes.

ask("Remember that my name is Hari.")
ask("What is my name?")


# Checkpoints contain saved versions of the graph state.

checkpoints = database.execute(
    """
    SELECT checkpoint_id, parent_checkpoint_id
    FROM checkpoints
    ORDER BY checkpoint_id
    """
).fetchall()

print("\nCheckpoints:")

for checkpoint in checkpoints:
    print(checkpoint)


# Writes contain node updates before they are merged into state.

writes = database.execute(
    """
    SELECT checkpoint_id, task_id, channel
    FROM writes
    ORDER BY checkpoint_id, idx
    """
).fetchall()

print("\nWrites:")

for write in writes:
    print(write)


database.close()
