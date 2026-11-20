"""Open a folder in the Cursor editor on macOS."""

import argparse
import subprocess
from pathlib import Path


def open_in_cursor(directory):
    folder = Path(directory).expanduser().resolve()
    if not folder.is_dir():
        raise ValueError(f"Expected a directory: {folder}")

    subprocess.run(["open", "-a", "Cursor", str(folder)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "directory", nargs="?", default=".", help="Folder to open (default: current directory)"
    )
    args = parser.parse_args()
    try:
        open_in_cursor(args.directory)
    except ValueError as error:
        parser.error(str(error))
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode)
