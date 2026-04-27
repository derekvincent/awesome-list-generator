# Awesome List Generator

This project is a Python-based tool designed to generate Markdown and HTML "Awesome Lists" from YAML data files. It automates the process of organizing resources into categories, fetching metadata (like descriptions) from URLs, and formatting the output.

## Project Overview

- **Purpose:** Create structured, visually appealing awesome lists from simple YAML inputs.
- **Core Technologies:** 
  - **Python 3.12+**: The primary programming language.
  - **[uv](https://github.com/astral-sh/uv)**: Used for dependency management and project execution.
  - **Click**: For the Command Line Interface.
  - **PyYAML**: For parsing the input configuration and item files.
  - **Jinja2**: For HTML template rendering.
  - **BeautifulSoup4**: For scraping metadata from resource URLs.
  - **Markdown2**: For converting markdown content.

## Architecture

- `src/awesome_list/`:
    - `cli.py`: Entry point for the `awesome-lists-generator` command.
    - `generator.py`: Main orchestration logic; parses YAML and triggers writers.
    - `models.py`: Data structures for `AwesomeItem`, `Category`, and `AppConfig`.
    - `awesome_items.py`: Logic for processing items, including metadata retrieval.
    - `markdown_writer.py` & `html_writer.py`: Handlers for generating different output formats.
    - `web-template/`: Contains HTML, CSS, and JS for the web-based list output.
- `tests/`: Contains unit and integration tests using `pytest`.
- `DESIGN.md`: Detailed specification of configuration options, properties, and the project roadmap.

## Building and Running

### Development Setup
This project uses `uv`. To install dependencies and set up a virtual environment:
```bash
uv sync
```

### Running the Generator
To generate a list from a YAML file:
```bash
uv run awesome-lists-generator generate <path_to_yaml_file>
```

### Testing
Run tests using `pytest`:
```bash
uv run pytest
```

### Linting and Formatting
The project uses `ruff` for linting and code formatting:
```bash
uv run ruff check .
uv run ruff format .
```

## Development Conventions

- **Type Hinting**: Use static type hints for all function signatures and variable declarations.
- **Models**: Use `dataclasses` for data models (see `src/awesome_list/models.py`).
- **Error Handling**: Use the internal `logger` module for application-level logging.
- **CLI**: Use `click` for all CLI-related features.
- **Testing**:
    - Use `pytest` for all tests.
    - Use `responses` to mock external HTTP requests in tests.
    - Place tests in the `tests/` directory, mirroring the source structure where appropriate.
- **Git Flow**: Branch from `main`, keep commits atomic and descriptive, and follow the guidelines in `CONTRIBUTING.md`.
