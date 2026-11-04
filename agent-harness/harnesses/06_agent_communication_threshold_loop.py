from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"

threshold = 8
max_rounds = 3


class Review(BaseModel):
    score: int
    feedback: str


def developer(message):
    response = client.responses.create(
        model=model,
        instructions="You are a developer. Write a simple, correct solution.",
        input=message,
    )

    return response.output_text


def reviewer(task, solution):
    response = client.responses.parse(
        model=model,
        instructions="Score the solution from 1 to 10 and explain how to improve it.",
        input=f"Task:\n{task}\n\nSolution:\n{solution}",
        text_format=Review,
    )

    return response.output_parsed


task = "Write a Python function that checks whether a number is prime."
solution = developer(task)

for round_number in range(1, max_rounds + 1):
    review = reviewer(task, solution)

    print(f"Round: {round_number}")
    print(f"Score: {review.score}")
    print(f"Feedback: {review.feedback}\n")

    if review.score >= threshold:
        break

    solution = developer(
        f"Task:\n{task}\n\n"
        f"Current solution:\n{solution}\n\n"
        f"Reviewer feedback:\n{review.feedback}"
    )

print("Final solution:")
print(solution)
