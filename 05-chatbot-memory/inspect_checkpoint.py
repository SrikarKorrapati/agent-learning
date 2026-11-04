import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver


DATABASE_PATH = Path(__file__).with_name("chatbot.sqlite")

THREAD_ID = "user-1"

CHECKPOINT_ID = (
    "1f1d8209-e740-6b5a-bfff-99a12c89bed4"
)


connection = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False,
)

memory = SqliteSaver(connection)


config = {
    "configurable": {
        "thread_id": THREAD_ID,
        "checkpoint_ns": "",
        "checkpoint_id": CHECKPOINT_ID,
    }
}


saved_checkpoint = memory.get_tuple(config)

state = saved_checkpoint.checkpoint["channel_values"]


print("Complete state:")
print(state)

print("\nMessages:")

for message in state.get("messages", []):
    print(f"{message.type}: {message.content}")


connection.close()