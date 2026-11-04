import json
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"

workspace = (Path(__file__).parent.parent / "runtime" / "agent_workspace").resolve()
workspace.mkdir(exist_ok=True)
current_directory = workspace


def resolve_path(path):
    target = (current_directory / path).resolve()
    target.relative_to(workspace)
    return target


def file_tool(name, description, properties):
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": properties,
            "required": list(properties),
            "additionalProperties": False,
        },
        "strict": True,
    }


tools = [
    file_tool(
        "create_directory",
        "Create a directory relative to the current directory.",
        {"path": {"type": "string"}},
    ),
    file_tool(
        "change_directory",
        "Change the current directory. Use .. to move to the parent.",
        {"path": {"type": "string"}},
    ),
    file_tool(
        "list_directory",
        "List files and directories. Use . for the current directory.",
        {"path": {"type": "string"}},
    ),
    file_tool(
        "create_file",
        "Create a text file.",
        {
            "path": {"type": "string"},
            "content": {"type": "string"},
        },
    ),
    file_tool(
        "read_file",
        "Read a text file.",
        {"path": {"type": "string"}},
    ),
    file_tool(
        "modify_file",
        "Replace text inside a file.",
        {
            "path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"},
        },
    ),
    file_tool(
        "delete_file",
        "Delete a file.",
        {"path": {"type": "string"}},
    ),
]


def execute_tool(call):
    global current_directory

    arguments = json.loads(call.arguments)

    if call.name == "create_directory":
        path = arguments["path"]
        resolve_path(path).mkdir(parents=True, exist_ok=True)
        return f"Created directory: {path}"

    if call.name == "change_directory":
        current_directory = resolve_path(arguments["path"])
        location = current_directory.relative_to(workspace)
        return f"Current directory: {location}"

    if call.name == "list_directory":
        directory = resolve_path(arguments["path"])
        items = [
            item.name + ("/" if item.is_dir() else "")
            for item in sorted(directory.iterdir())
        ]
        return "\n".join(items)

    if call.name == "create_file":
        path = arguments["path"]
        resolve_path(path).write_text(arguments["content"])
        return f"Created file: {path}"

    if call.name == "read_file":
        return resolve_path(arguments["path"]).read_text()

    if call.name == "modify_file":
        path = arguments["path"]
        file = resolve_path(path)
        content = file.read_text()
        file.write_text(
            content.replace(
                arguments["old_text"],
                arguments["new_text"],
            )
        )
        return f"Modified file: {path}"

    if call.name == "delete_file":
        path = arguments["path"]
        resolve_path(path).unlink()
        return f"Deleted file: {path}"


def run_agent(task):
    response = client.responses.create(
        model=model,
        tools=tools,
        parallel_tool_calls=False,
        input=task,
    )

    while True:
        calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not calls:
            return response.output_text

        outputs = []

        for call in calls:
            result = execute_tool(call)

            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                }
            )

        response = client.responses.create(
            model=model,
            tools=tools,
            parallel_tool_calls=False,
            previous_response_id=response.id,
            input=outputs,
        )


print(
    run_agent(
        "Create a notes directory, enter it, create todo.txt containing "
        "'Learn agents', change it to 'Build agents', read it, delete it, "
        "and list the current directory."
    )
)
