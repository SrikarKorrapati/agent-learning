"""Open a folder in Cursor using a screenshot and one model action at a time."""

import argparse
import time
from functools import partial
from pathlib import Path

import pyautogui
from desktop_model import ask_model
from dotenv import load_dotenv
from openai import AuthenticationError, OpenAI
from pynput.keyboard import Controller


def run_agent(goal, ask_model):
    for _ in range(20):
        # On Retina displays, match screenshot pixels to mouse coordinates.
        screen = pyautogui.screenshot().resize(pyautogui.size())
        action = ask_model(goal, screen)

        if action["type"] == "done":
            return action["message"]
        elif action["type"] == "click":
            pyautogui.click(action["x"], action["y"])
        elif action["type"] == "press":
            pyautogui.hotkey(*action["keys"])
        elif action["type"] == "type":
            Controller().type(action["text"])  # Also types Unicode folder names.
        elif action["type"] != "wait":
            raise ValueError(f"Unknown action: {action}")

        time.sleep(0.5)  # Let the UI update before looking again.

    raise RuntimeError("Agent reached the 20-step limit")


def open_in_cursor(directory):
    folder = Path(directory).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Expected a directory: {folder}")

    load_dotenv()
    goal = f"Open Cursor on this Mac and open the folder {folder} as its workspace."
    with OpenAI(timeout=60, max_retries=0) as client:
        return run_agent(goal, partial(ask_model, client))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default=".", help="Folder to open")
    try:
        print(open_in_cursor(parser.parse_args().directory))
    except (ValueError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    except AuthenticationError:
        parser.exit(1, "OpenAI rejected the API key. Check OPENAI_API_KEY.\n")
