import json
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"

# Short-term conversation state
conversation = []

# Long-term memory
memory = {}

# Reusable instructions
skills = {
    "research": "Compare reliable sources and include links.",
    "explain": "Explain simply, in execution order, with one example.",
}

active_skill = "explain"

def remember(key, value):
    memory[key] = value

def use_skill(name):
    global active_skill
    active_skill = name


def build_instructions():
    memory_text = json.dumps(memory)
    skill_text = skills[active_skill]

    instructions = (
        "You are a helpful agent.\n\n"
        f"Memory:\n{memory_text}\n\n"
        f"Skill:\n{skill_text}"
    )

    return instructions


def compact():
    global conversation

    if len(conversation) > 8:
        result = client.responses.compact(
            model=model,
            input=conversation,
        )

        conversation = list(result.output)


def ask(prompt):
    conversation.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    response = client.responses.create(
        model=model,
        instructions=build_instructions(),
        input=conversation,
    )

    conversation.extend(response.output)
    compact()

    return response.output_text


def run_subagents(tasks):
    def run_one_subagent(task):
        response = client.responses.create(
            model=model,
            instructions="Complete only this focused subtask.",
            input=task,
        )

        return response.output_text

    with ThreadPoolExecutor() as executor:
        results = list(
            executor.map(run_one_subagent, tasks)
        )

    final_response = client.responses.create(
        model=model,
        instructions="Combine the subagent results into one answer.",
        input=json.dumps(results),
    )

    return final_response.output_text


# Example

remember("preferred_language", "Python")
use_skill("explain")

print(ask("What is a Python decorator?"))

# Subagent example:
# print(run_subagents(["Research SQLite", "Research PostgreSQL"]))

