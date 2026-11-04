import base64
import json
import mimetypes
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
workspace = Path.cwd()

tools = [
    {"type": "web_search"},
    {
        "type": "function",
        "name": "bash",
        "description": "Run a shell command in the current workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute.",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "view_image",
        "description": "View a local image from the current workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Image path relative to the workspace.",
                }
            },
            "required": ["path"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def resolve_path(path_string):
    path = (workspace / path_string).resolve()

    try:
        path.relative_to(workspace)
    except ValueError:
        raise ValueError("Path must remain inside the workspace.")

    return path


def run_bash(command):
    print(f"\n\nCommand requested:\n{command}")

    if input("Run it? [y/N]: ").strip().lower() not in {"y", "yes"}:
        return json.dumps({"status": "rejected"})

    try:
        result = subprocess.run(
            command,
            shell=True,
            executable="/bin/zsh",
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=30,
        )

        return json.dumps(
            {
                "exit_code": result.returncode,
                "stdout": result.stdout[-50_000:],
                "stderr": result.stderr[-50_000:],
            }
        )
    except subprocess.TimeoutExpired:
        return json.dumps({"error": "Command timed out."})
    except Exception as error:
        return json.dumps({"error": str(error)})


def load_image(path_string):
    try:
        path = resolve_path(path_string)

        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")

        mime_type, _ = mimetypes.guess_type(path)

        if mime_type not in {
            "image/png",
            "image/jpeg",
            "image/webp",
            "image/gif",
        }:
            raise ValueError("Supported formats: PNG, JPEG, WEBP and GIF.")

        encoded = base64.b64encode(path.read_bytes()).decode()

        return [
            {
                "type": "input_text",
                "text": f"Loaded image: {path.name}",
            },
            {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{encoded}",
                "detail": "auto",
            },
        ]

    except Exception as error:
        return [
            {
                "type": "input_text",
                "text": json.dumps({"error": str(error)}),
            }
        ]


def execute_tool(call):
    try:
        arguments = json.loads(call.arguments)

        if call.name == "bash":
            return run_bash(arguments["command"])

        if call.name == "view_image":
            return load_image(arguments["path"])

        return json.dumps({"error": f"Unknown tool: {call.name}"})

    except Exception as error:
        return json.dumps({"error": str(error)})


def create_response(input_data, previous_response_id=None):
    request = {
        "model": "gpt-4.1",
        "instructions": (
            "You are a coding agent. Use web search when current information "
            "is needed. Use bash to inspect or modify the workspace. Use "
            "view_image to inspect local images."
        ),
        "tools": tools,
        "input": input_data,
        "stream": True,
    }

    if previous_response_id:
        request["previous_response_id"] = previous_response_id

    completed_response = None

    for event in client.responses.create(**request):
        if event.type == "response.web_search_call.searching":
            print("\n[Searching the web...]\n")

        elif event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)

        elif event.type == "response.completed":
            completed_response = event.response

    if completed_response is None:
        raise RuntimeError("The response did not complete.")

    return completed_response


def run_turn(prompt, previous_response_id=None):
    next_input = prompt

    for _ in range(10):
        response = create_response(next_input, previous_response_id)
        previous_response_id = response.id

        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            print()
            return previous_response_id

        next_input = []

        for call in function_calls:
            print(f"\n[Running tool: {call.name}]")

            next_input.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": execute_tool(call),
                }
            )

    raise RuntimeError("Too many consecutive tool calls.")


def main():
    print(f"Workspace: {workspace}")
    print("Type 'exit' to stop.")

    previous_response_id = None

    while True:
        try:
            prompt = input("\nYou: ").strip()

            if prompt.lower() in {"exit", "quit"}:
                break

            if not prompt:
                continue

            print("Assistant: ", end="", flush=True)

            previous_response_id = run_turn(
                prompt,
                previous_response_id,
            )

        except KeyboardInterrupt:
            print("\nStopped.")
            break

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()