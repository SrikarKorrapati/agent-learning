import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from openai import OpenAI


class AgentHarness:
    """Small agent harness demonstrating memory, compaction, skills and subagents."""

    def __init__(self, model="gpt-6-astra"):
        self.model = model
        self.client = OpenAI()

        root = Path(__file__).parent
        self.skills_directory = root / "skills"

        runtime_directory = root / "runtime"
        runtime_directory.mkdir(exist_ok=True)

        self.database = sqlite3.connect(
            runtime_directory / "harness.sqlite",
            check_same_thread=False,
        )

        self.database.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                previous_response_id TEXT NOT NULL
            )
            """
        )

        self.database.execute(
            """
            CREATE TABLE IF NOT EXISTS memories (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        self.database.commit()

    # Long-term memory

    def remember(self, key, value):
        self.database.execute(
            """
            INSERT OR REPLACE INTO memories (key, value)
            VALUES (?, ?)
            """,
            (key, value),
        )
        self.database.commit()

    def get_memories(self):
        rows = self.database.execute(
            "SELECT key, value FROM memories ORDER BY key"
        ).fetchall()

        return {key: value for key, value in rows}

    # Conversation state

    def get_previous_response_id(self, session_id):
        row = self.database.execute(
            """
            SELECT previous_response_id
            FROM sessions
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

        return row[0] if row else None

    def save_response_id(self, session_id, response_id):
        self.database.execute(
            """
            INSERT OR REPLACE INTO sessions (
                session_id,
                previous_response_id
            ) VALUES (?, ?)
            """,
            (session_id, response_id),
        )
        self.database.commit()

    # Skills

    def available_skills(self):
        return sorted(path.stem for path in self.skills_directory.glob("*.md"))

    def load_skill(self, skill_name):
        if not skill_name:
            return ""

        return (self.skills_directory / f"{skill_name}.md").read_text()

    def build_instructions(self, skill_name=None):
        memories = self.get_memories()
        skill = self.load_skill(skill_name)

        return f"""
You are a helpful agent running inside a small educational harness.
Use web search when current information is needed.

Long-term memory:
{json.dumps(memories, indent=2)}

Active skill:
{skill or "No skill selected."}
""".strip()

    # Main agent loop

    def ask(self, prompt, session_id="default", skill_name=None):
        request = {
            "model": self.model,
            "instructions": self.build_instructions(skill_name),
            "input": prompt,
            "tools": [{"type": "web_search"}],
            "context_management": [
                {
                    "type": "compaction",
                    "compact_threshold": 100_000,
                }
            ],
        }

        previous_response_id = self.get_previous_response_id(session_id)

        if previous_response_id:
            request["previous_response_id"] = previous_response_id

        response = self.client.responses.create(**request)

        self.save_response_id(session_id, response.id)

        return response.output_text

    # Subagent orchestration and communication

    def run_subagents(self, tasks):
        def run_one(task):
            client = OpenAI()

            response = client.responses.create(
                model=self.model,
                instructions=(
                    "You are a focused subagent. Complete only the assigned "
                    "task and return a concise result for the root agent."
                ),
                input=task,
                tools=[{"type": "web_search"}],
            )

            return {
                "task": task,
                "result": response.output_text,
            }

        with ThreadPoolExecutor(max_workers=min(3, len(tasks))) as executor:
            results = list(executor.map(run_one, tasks))

        synthesis = self.client.responses.create(
            model=self.model,
            instructions=(
                "You are the root agent. Combine the subagent results into "
                "one clear answer. Preserve disagreements and uncertainty."
            ),
            input=json.dumps(results, indent=2),
        )

        return {
            "subagent_results": results,
            "final_answer": synthesis.output_text,
        }

    def close(self):
        self.database.close()

