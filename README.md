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
