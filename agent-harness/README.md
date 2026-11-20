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

## Asynchronous subagents

Read [11_async_subagents.py](harnesses/11_async_subagents.py) for a small example
using `asyncio` and `AsyncOpenAI`. Each subagent is an independent model call with
its own instructions and input. They share an API client, not conversation history.

From the repository root, after the setup above:

```bash
python agent-harness/harnesses/11_async_subagents.py
```

The script reads the root `.env` and makes four model calls on a successful run:
two subagent evaluations, one main-agent criteria request, and one final synthesis.
It uses API credits. It defaults to `gpt-6-astra`, matching the other examples;
set `OPENAI_MODEL` in `.env` to use another available Responses API model.

Follow the logic in this order:

1. `call_agent()` awaits one API response and returns the agent name and answer.
2. `asyncio.create_task()` schedules the SQLite and PostgreSQL subagents together.
3. The main agent prepares comparison criteria while those requests are running.
4. `asyncio.as_completed()` collects the subagent results as they become available,
   after the criteria request. Completion order can vary.
5. The main agent receives the criteria and both results explicitly, then answers.

`await` suspends the current coroutine so other tasks can run during network waits.
The `finally` block cancels and awaits leftover tasks if a request fails, then the
client closes. This example focuses on orchestration: the assignments are fixed in
Python, each worker makes one model call, and there is no tool loop or shared memory.

Compare this with `04_agent_communication_handoff.py`: that example must wait for
the first agent's result before calling the second. Here, the two assignments are
independent, so their API requests can overlap.

References: [OpenAI async client](https://github.com/openai/openai-python#async-usage)
and [Python tasks](https://docs.python.org/3/library/asyncio-task.html).

