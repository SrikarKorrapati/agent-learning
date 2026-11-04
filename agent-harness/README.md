# Agent Harness

Start with `harnesses/01_basic_harness.py`. It keeps every concept in one short file using
plain lists, dictionaries and functions.

```bash
python agent-harness/harnesses/01_basic_harness.py
```

`harness.py` and `main.py` are the more complete version for later.

This small educational harness demonstrates five concepts:

1. **Conversation state** — each session stores its latest OpenAI response ID.
2. **Long-term memory** — reusable key/value facts are stored in SQLite.
3. **Compaction** — the Responses API automatically compacts long contexts.
4. **Skills** — Markdown playbooks can be loaded into the agent instructions.
5. **Subagents** — independent tasks run in parallel and a root agent combines them.

## Run

From the repository root:

```bash
python agent-harness/main.py
```

The root `.env` file must contain:

```ini
OPENAI_API_KEY=your_openai_api_key
```

## Try the concepts

```text
/remember preferred_language=Python
/skills
/skill explain-code
Explain a Python decorator
/agents Research SQLite | Research PostgreSQL
```

Runtime state is stored locally in `runtime/harness.sqlite` and is excluded from Git.

