from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"


def call_agent(name, instructions, message):
    print(f"\nMessage sent to {name}:\n{message}")

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=message,
    )

    print(f"\n{name} replied:\n{response.output_text}")

    return response.output_text


task = "Design a Python function that checks whether a number is prime."

# Developer sends a proposal to the reviewer.
proposal = call_agent(
    "Developer Agent",
    "You are a developer. Propose a short solution for the task.",
    task,
)

# Reviewer sends feedback back to the developer.
feedback = call_agent(
    "Reviewer Agent",
    "You are a code reviewer. Find problems and suggest improvements.",
    f"Task:\n{task}\n\nDeveloper's proposal:\n{proposal}",
)

# Developer uses the reviewer's message to revise the solution.
final_solution = call_agent(
    "Developer Agent",
    "You are a developer. Revise your solution using the feedback.",
    (
        f"Task:\n{task}\n\n"
        f"Your first proposal:\n{proposal}\n\n"
        f"Reviewer's feedback:\n{feedback}"
    ),
)

print(f"\nFinal solution:\n{final_solution}")
