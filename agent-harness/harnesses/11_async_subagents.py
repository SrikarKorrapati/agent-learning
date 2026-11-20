"""Two subagents run concurrently while the main agent prepares a comparison."""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
model = os.getenv("OPENAI_MODEL", "gpt-6-astra")


async def call_agent(client, name, instructions, message):
    print(f"{name}: started")
    response = await client.responses.create(
        model=model,
        instructions=instructions,
        input=message,
    )
    print(f"{name}: finished")
    return name, response.output_text


async def main():
    question = "Should a small, single-server Python app use SQLite or PostgreSQL?"

    async with AsyncOpenAI() as client:
        # Schedule both subagents now; do not wait for one before starting the other.
        tasks = [
            asyncio.create_task(call_agent(
                client,
                database,
                f"Evaluate {database} for the user's question. "
                "Give benefits and limitations in three short bullets.",
                question,
            ))
            for database in ("SQLite", "PostgreSQL")
        ]

        try:
            # The main agent can do independent work while subagents await the API.
            _, criteria = await call_agent(
                client,
                "Main agent: criteria",
                "List three criteria for this decision. Do not choose a database yet.",
                question,
            )

            # Consume whichever subagent finishes next, rather than submission order.
            results = []
            for finished in asyncio.as_completed(tasks):
                name, answer = await finished
                print(f"Main agent received {name}:\n{answer}\n")
                results.append(f"{name}:\n{answer}")

            _, final_answer = await call_agent(
                client,
                "Main agent: answer",
                "Use the criteria and subagent findings to give a short recommendation. "
                "Preserve relevant limitations and disagreements.",
                f"Question: {question}\n\nCriteria:\n{criteria}\n\nFindings:\n"
                + "\n\n".join(results),
            )
            print(f"\nFinal answer:\n{final_answer}")
        finally:
            # If a request fails, clean up pending tasks before closing the client.
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
