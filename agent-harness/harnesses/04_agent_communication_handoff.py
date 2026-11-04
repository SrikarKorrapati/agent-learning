from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"


def call_agent(instructions, message):
    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=message,
    )

    return response.output_text


question = "What are the benefits of SQLite?"

# Agent 1 does the research.
research = call_agent(
    "You are a research agent. Return the important facts.",
    question,
)

# Python passes Agent 1's message to Agent 2.
final_answer = call_agent(
    "You are a writer agent. Turn the research into a clear answer.",
    f"Question:\n{question}\n\nResearch from Agent 1:\n{research}",
)

print(final_answer)
