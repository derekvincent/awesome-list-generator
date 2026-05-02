import os
import re
import sys

import markdown2

url_validator = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
    re.IGNORECASE,
)


def is_url_valid(url: str | None) -> bool:
    if not url:
        return False
    return re.match(url_validator, url) is not None


def convert_markdown_to_html(markdown_file: str) -> str:
    """Convert the markdown file to HTML using markdown2 library."""

    if not os.path.exists(markdown_file):
        raise FileNotFoundError(f"Markdown file not found: {markdown_file}")

    with open(markdown_file, "r", encoding="utf-8") as md_file:
        markdown_content = md_file.read()
        html_content = markdown2.markdown(
            markdown_content,
            extras=[
                "fenced-code-blocks",
                "tables",
                "strike",
                "cuddled-lists",
                "metadata",
            ],
        )
        return html_content


def exit_process(code: int = 0) -> None:
    """Exit the process with exit code.

    `sys.exit` seems to be a bit unreliable, process just sleeps and does not exit.
    So we are using os._exit instead and doing some manual cleanup.
    """
    import atexit
    import gc

    gc.collect()
    atexit._run_exitfuncs()
    sys.stdout.flush()
    os._exit(code)
