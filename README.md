# Awesome List Generator

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, Python-based CLI tool designed to automate the generation of beautiful, structured "Awesome Lists" in both Markdown and HTML formats from simple YAML data files.

Stop manually formatting your markdown links and managing table of contents. Just define your resources in a YAML file, and let the generator do the heavy lifting!

## ✨ Features

- **Dual Output Formats**: Generates both a standard GitHub-flavored `README.md` and a fully responsive, searchable, dark-mode-enabled Bootstrap 5 HTML site.
- **Auto-Enrichment**: Automatically scrapes websites for Open Graph titles and descriptions if you don't provide them.
- **GitHub Integration**: Intercepts GitHub URLs and uses the GitHub REST API to fetch real-time Stars (⭐), Forks (🍴), and License data.
- **Built-in Link Linter**: Fast, stream-based health checks to detect and report broken links (`404`s, parked domains, etc.) so your list never goes stale.
- **Smart Categorization**: Supports nested subcategories, custom visual labels, images, and emojis.
- **Change Tracking**: Automatically builds a `latest-changes.md` diff to track what was added, changed, or removed between builds.

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **uv** (Recommended for dependency management)

### Installation

Clone the repository and install the dependencies using `uv`:

```bash
git clone https://github.com/derekvincent/awesome-list-generator.git
cd awesome-list-generator
uv sync
```

## 💻 Usage

The CLI provides two main commands: `generate` and `lint`.

### Generate the List

To parse your YAML file, fetch metadata, and generate both the Markdown and HTML outputs:

```bash
uv run awesome-lists-generator generate path/to/your/projects.yaml
```

*Tip: Add `--debug` for verbose logging output.*

### Lint the List

To run a fast health check on all the URLs in your list without generating any output files. This will exit with a non-zero status code if broken links are found, making it perfect for CI/CD pipelines.

```bash
uv run awesome-lists-generator lint path/to/your/projects.yaml
```

## ⚙️ Configuration

The generator is driven by a single YAML file (e.g., `projects.yaml`). Here is a basic example of the structure:

```yaml
config: 
  output_file: output/README.md
  html_folder: output/web
  list_title: Awesome Example!
  markdown_header_file: config/header.md
  feedback_api_url: "https://your-worker.your-account.workers.dev" # Optional Feedback API

labels:
  - label: "github" 
    name: "GitHub"
    image: "https://github.githubassets.com/favicons/favicon.svg"
    
categories:
  - name: tools
    label: Development Tools
    description: Useful tools for development.

items:
 - link_id: https://github.com/derekvincent/awesome-list-generator
   name: Awesome List Generator
   category: tools
   labels: ["github"]
```

### GitHub API Rate Limits

To prevent hitting unauthenticated rate limits when querying GitHub repository metadata, you can export a `GITHUB_TOKEN` environment variable before running the generator:

```bash
export GITHUB_TOKEN="your_personal_access_token"
uv run awesome-lists-generator generate projects.yaml
```

## 🤝 Contributing

Contributions are very welcome! If you'd like to add a feature, fix a bug, or improve the documentation, please check out our Contributing Guidelines and our Code of Conduct.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.