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


def create_directory(path):
    resolve_path(path).mkdir(parents=True, exist_ok=True)
    return f"Created directory: {path}"


def change_directory(path):
    global current_directory
    current_directory = resolve_path(path)
    location = current_directory.relative_to(workspace)
    return f"Current directory: {location or '.'}"


def list_directory(path):
    directory = resolve_path(path)
    items = [
        item.name + ("/" if item.is_dir() else "")
        for item in sorted(directory.iterdir())
    ]
    return "\n".join(items)


def create_file(path, content):
    resolve_path(path).write_text(content)
    return f"Created file: {path}"


def read_file(path):
    return resolve_path(path).read_text()


def modify_file(path, old_text, new_text):
    file = resolve_path(path)
    content = file.read_text()
    file.write_text(content.replace(old_text, new_text))
    return f"Modified file: {path}"


def delete_file(path):
    resolve_path(path).unlink()
    return f"Deleted file: {path}"


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
    arguments = json.loads(call.arguments)

    if call.name == "create_directory":
        return create_directory(arguments["path"])

    if call.name == "change_directory":
        return change_directory(arguments["path"])

    if call.name == "list_directory":
        return list_directory(arguments["path"])

    if call.name == "create_file":
        return create_file(
            arguments["path"],
            arguments["content"],
        )

    if call.name == "read_file":
        return read_file(arguments["path"])

    if call.name == "modify_file":
        return modify_file(
            arguments["path"],
            arguments["old_text"],
            arguments["new_text"],
        )

    if call.name == "delete_file":
        return delete_file(arguments["path"])


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
