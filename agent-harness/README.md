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

## Browser control: three ways to run the same loop

| Example | What the model sees | What executes its actions |
| --- | --- | --- |
| `07_browser_control.py` | Visible page text | Playwright text locators and CSS selectors |
| `09_visual_browser_control.py` | Screenshots and the current URL | Playwright mouse coordinates and keyboard input |
| `10_agent_browser_control.py` | Accessibility snapshots with refs such as `@e1` | Vercel's agent-browser CLI over CDP |

The new examples are independent scripts. Read `tools`, then `execute_tool`, then
`control_browser`: the model selects a tool, Python executes it, and the updated
page goes back as a `function_call_output`. `previous_response_id` keeps the
conversation connected. A screenshot is image input, not a text description of
an image. Both scripts execute one model-selected action at a time, limit the run
to 20 model turns, and close their browser in `finally`.

From the repository root, install just the browser examples' Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install openai playwright python-dotenv
python -m playwright install chromium
```

The CLI example also needs Node.js/npm and its browser download. The Python script
uses `npx` with a pinned version, so no global npm install is needed:

```bash
npx --yes agent-browser@0.42.0 install
```

Set `OPENAI_API_KEY` in the root `.env`. Both new examples default to the existing
examples' `gpt-6-astra` model; set `OPENAI_MODEL` in `.env` to override it. Visual
control requires a model with image input and function calling. These runs call
the OpenAI API and use API credits.

```bash
python agent-harness/harnesses/09_visual_browser_control.py
python agent-harness/harnesses/10_agent_browser_control.py
```

Both open a visible browser, visit example.com, click **Learn more**, then report
the destination's heading and URL. Tool names print as the agent works. Pass a
different task as a quoted argument; add `--headless` to hide the browser:

```bash
python agent-harness/harnesses/10_agent_browser_control.py \
  "Open https://example.com and tell me its heading." --headless
```

For a local app, include its `http://localhost:...` URL in the task. The visual
example also supports typing, keyboard shortcuts, and scrolling. The CLI example
exposes navigation, snapshots, clicking, and filling inputs; add more typed tools
as you need them. The model never receives an arbitrary shell-execution tool.

These are learning examples: the model can interact with sites reachable by the
fresh browser, and page observations are sent to the API. Use a demo app when
experimenting. The code does not implement a website allowlist or approval UI.

References: [OpenAI function calling](https://developers.openai.com/api/docs/guides/function-calling),
[computer use](https://developers.openai.com/api/docs/guides/tools-computer-use),
and [agent-browser commands](https://agent-browser.dev/commands).

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

