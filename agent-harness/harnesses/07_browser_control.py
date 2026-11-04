import json

from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright


load_dotenv()

client = OpenAI()
model = "gpt-6-astra"


def browser_tool(name, description, properties):
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
    browser_tool(
        "open_url",
        "Open a URL.",
        {"url": {"type": "string"}},
    ),
    browser_tool(
        "read_page",
        "Read the visible page text.",
        {},
    ),
    browser_tool(
        "click_text",
        "Click an element containing this text.",
        {"text": {"type": "string"}},
    ),
    browser_tool(
        "fill",
        "Fill an input using a CSS selector.",
        {
            "selector": {"type": "string"},
            "value": {"type": "string"},
        },
    ),
]


def execute_tool(call, page):
    arguments = json.loads(call.arguments)

    if call.name == "open_url":
        page.goto(arguments["url"])
        return f"Opened {page.url}"

    if call.name == "read_page":
        return page.locator("body").inner_text()

    if call.name == "click_text":
        page.get_by_text(arguments["text"]).first.click()
        return f"Clicked {arguments['text']}"

    if call.name == "fill":
        page.locator(arguments["selector"]).fill(arguments["value"])
        return f"Filled {arguments['selector']}"


def control_browser(task):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        response = client.responses.create(
            model=model,
            tools=tools,
            input=task,
        )

        while True:
            calls = [
                item
                for item in response.output
                if item.type == "function_call"
            ]

            if not calls:
                browser.close()
                return response.output_text

            outputs = []

            for call in calls:
                result = execute_tool(call, page)

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
                previous_response_id=response.id,
                input=outputs,
            )


result = control_browser(
    "Open https://example.com, read the page, and tell me its heading."
)

print(result)
