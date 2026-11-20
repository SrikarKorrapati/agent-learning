# Agent Learning

Small Python examples for learning the OpenAI Responses API, LangGraph, structured outputs, reflection, ReAct agents, tool use, and checkpointed chatbot memory.

## Contents

```text
01-responses-api/
  multiple_tools.py
  web_and_bash.py
  web_search.py
02-structured-outputs/
  structured_outputs.py
03-reflection/
  reflection_system.py
  reflexion_agent.py
04-react-agent/
  react_agent.py
05-chatbot-memory/
  chatbot_with_memory.py
  inspect_checkpoint.py
  inspect_database.py
06-browser-automation/
  selenium_form.py
07-desktop-automation/
  open_cursor.py
  desktop_model.py
agent-harness/
  harnesses/
    01_basic_harness.py
    02_long_term_memory.py
    03_short_term_memory.py
    04_agent_communication_handoff.py
    05_agent_communication_feedback_loop.py
    06_agent_communication_threshold_loop.py
    07_browser_control.py
    08_local_file_control.py
    09_visual_browser_control.py
    10_agent_browser_control.py
    11_async_subagents.py
  harness.py
  main.py
  skills/
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API keys to `.env`, then run an example directly:

```bash
python 04-react-agent/react_agent.py
```

The real `.env` file and local SQLite databases are intentionally excluded from Git.

## Open a folder in Cursor through computer use

The Python script sends a screenshot of your Mac's main display to OpenAI and asks
the model to open the requested folder in Cursor. The model chooses mouse clicks
and keystrokes. Python executes them and sends back a fresh screenshot so the
model can check which window or dialog appeared.

Install Cursor and the dependencies from the setup above. Set `OPENAI_API_KEY`
in the root `.env`. The default model is `gpt-6.2-sol`. You can set `OPENAI_MODEL`
to another Responses API model that supports image input and JSON output. In macOS System
Settings → Privacy & Security, allow the terminal app running Python to use
Screen Recording and Accessibility. Keep Cursor on the main display and use a
desktop you are comfortable sharing with the API.

```bash
python3 07-desktop-automation/open_cursor.py agent-harness
```

Start with `run_agent()` in [open_cursor.py](07-desktop-automation/open_cursor.py).
It takes a screenshot, asks for one action, and executes it. The
[`ask_model()` helper](07-desktop-automation/desktop_model.py) sends the image
to OpenAI and reads the action. The loop stops when the model returns `done` or
reaches 20 steps.
