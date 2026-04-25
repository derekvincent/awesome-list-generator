import difflib
import logging
import os
import re
from collections import OrderedDict
from datetime import datetime

log = logging.getLogger(__name__)


def select_markdown_section(markdown_text: str) -> str:
    section_dict = dict()

    matches = re.findall(
        r"^\[(\w+)\]:\s*#"
        r"\s*([\s\S]*?)"
        r"(?=\n\[\w+\]:\s*#|\Z)",
        markdown_text,
        flags=re.UNICODE | re.DOTALL | re.MULTILINE,
    )

    for section, subtext in matches:
        subtext = subtext.rstrip()
        section_dict[section] = subtext

    return section_dict


def clean_diffed_markdown(diffed_markdown: list) -> list:
    """
    Used to remove some unsavory markdown formatting items that we do not
    want to worry about in the changelog output.
    """
    cleaned_diffed_list = []
    for line in diffed_markdown:
        if len(line) < 2:
            continue
        elif line[1:] == "---":
            continue
        else:
            cleaned_diffed_list.append(line)
    return cleaned_diffed_list


def generate_changes_md(
    last_readme_md: str, current_readme_md: str, build_date: datetime.date
) -> str:
    change_log_md = ""

    last_readme_sections = select_markdown_section(last_readme_md)
    current_readme_sections = select_markdown_section(current_readme_md)

    section_added = False
    change_log_md += f"# Latest Changes - {build_date}\n"

    for section_key in last_readme_sections:
        change_log = None
        change_log = difflib.unified_diff(
            last_readme_sections[section_key].splitlines(keepends=False),
            current_readme_sections[section_key].splitlines(keepends=False),
            fromfile="original.md",
            tofile="newfile.md",
            lineterm="",
            n=0,
        )

        lines = list(clean_diffed_markdown(change_log))[2:]
        if len(lines) > 1:
            section_added = True
            change_log_md += f"## Section: {section_key.capitalize()}\n"
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.startswith("-"):
                    if i + 1 < len(lines) and lines[i + 1].startswith("+"):
                        old_line = line[1:]
                        new_line = lines[i + 1][1:]
                        change_log_md += ">### Changed:\n"
                        change_log_md += ">**Previous**\n"
                        change_log_md += f"> {old_line.lstrip()}\n"
                        change_log_md += ">\n>**New**\n"
                        change_log_md += f"> {new_line.lstrip()}\n"
                        change_log_md += "\n"
                        i += 2
                        continue
                    elif line.startswith("-") and len(line) > 2:
                        change_log_md += f">### Removed:\n> {line[1:].lstrip()}\n\n"
                elif line.startswith("+") and len(line) > 2:
                    change_log_md += f">### Added:\n> {line[1:].lstrip()}\n\n"
                i += 1
    if not section_added:
        change_log_md += "**No changes detected in this build.**"
    return change_log_md


def generate_item_md(item: dict, labels: list, config: dict) -> str:

    item_label_md = ""
    if "labels" in item:
        for label_id in item["labels"]:
            for label in labels:
                if label.get("label") == label_id:
                    if "image" in label:
                        item_label_md += '<code><img src="{image}" alt="{name}" style="display:inline;" width="16" height="16"></code>'.format(
                            image=label["image"], name=label["name"]
                        )
                    elif "emoji" in label:
                        item_label_md += "<code>{emoji}</code>".format(
                            emoji=label["emoji"]
                        )
                    elif "name" in label:
                        item_label_md += "<code>{name}</code>".format(
                            name=label["name"]
                        )

    item_markdown = f"- **[{item['name']}]({item['link_id']})** {item_label_md} - {item['description']}"
    return item_markdown


def generate_category_md(
    category: dict, labels: list, config: dict, heading_level: int = 2
) -> str:
    category_markdown = ""

    category_markdown += "\n"

    category_markdown += (
        "#" * heading_level
        + " <a id='"
        + category["name"]
        + "'></a>"
        + category["label"]
        + "\n\n"
    )

    back_to_top_anchor = "#contents"

    category_markdown += f'<a href="{back_to_top_anchor}"><img align="right" width="16" height="16" src="{config.get("up_arrow_image")}" alt="Back to top"></a>\n\n'

    if category.get("description"):
        category_markdown += "_" + category["description"].strip() + "_\n\n"

    if "items" in category:
        for item in category["items"]:
            item_markdown = generate_item_md(item, labels, config)
            category_markdown += item_markdown + "\n"

    if "subcategories" in category:
        for subcategory_key in category["subcategories"]:
            category_markdown += generate_category_md(
                category["subcategories"][subcategory_key],
                labels,
                config,
                heading_level + 1,
            )

    return category_markdown


def generate_legend_md(labels: list, config: dict) -> str:
    legend_md = "## Legend\n"
    
    for label in labels:
        image = ""
        if "image" in label and "name" in label:
            image = '<img src="{image}" style="display:inline;" width="13" height="13">'.format(
                image=label["image"]
            )
        elif "emoji" in label and "name" in label:
            image = label["emoji"]
            
        description = " - " + label["description"] if "description" in label else ""
        legend_md += f"- {image}&nbsp; <b>{label['name']}</b> {description}\n"

    return legend_md


def category_toc_md(category: dict, items_len: int, level: int = 1) -> str:

    category_toc_markdown = ""
    url = "#" + category["name"]
    items_count = 0
    if "items" in category:
        items_count += len(category["items"])

        category_toc_markdown += (
            "{bullet} [{title}]({url}) _{items_count} items_\n".format(
                bullet=" " * (level * 2) + "-" if level > 1 else "-",
                title=category["label"],
                url=url,
                items_count=items_count,
            )
        )
    else:
        category_toc_markdown += "{bullet} [{title}]({url}) \n".format(
            bullet=" " * (level * 2) + "-" if level > 1 else "-",
            title=category["label"],
            url=url,
        )
    return category_toc_markdown


def generate_toc_md(categories: OrderedDict, config: dict, level: int = 1) -> str:

    toc_markdown = ""
    for category_key in categories:
        category = categories[category_key]
        items_count = 0
        if "items" in category:
            items_count += len(category["items"])
        toc_markdown += category_toc_md(category, items_count, level)

        if "subcategories" in category:
            toc_markdown += generate_toc_md(
                category["subcategories"], config, level + 1
            )

    return toc_markdown + "\n"


def generate_title_md(config: dict) -> str:
    return f"# {config['list_title']}\n"


def generate_md(categories: OrderedDict, labels: list, config: dict) -> str:

    markdown = ""

    markdown += "\n[header]: #\n"
    # TODO: Markdown Header
    if "markdown_header_file" in config:
        if os.path.exists(config["markdown_header_file"]):
            with open(config["markdown_header_file"], "r") as f:
                header_content = f.read()
                header_content = header_content.replace("{awesome_title}", config.get("list_title", ""))
                header_content = header_content.replace("{awesome_subtitle}", config.get("list_subtitle", ""))
                header_content = header_content.replace("{awesome_description}", config.get("list_description", ""))
                markdown += header_content + "\n"
        else:
            log.warning(
                f"Markdown header file not found: {config['markdown_header_file']}. Using default header."
            )
            markdown += generate_title_md(config=config) + "\n"
    # TOC
    markdown += "\n[categories]: #\n"
    markdown += "## Contents\n\n"
    markdown += generate_toc_md(categories=categories, config=config)

    # Legend
    markdown += "\n[legend]: #\n"
    if len(labels) > 0:
        markdown += generate_legend_md(labels=labels, config=config)

    # Body
    markdown += "\n[contents]: #\n"
    for category_key in categories:
        category = categories[category_key]
        markdown += generate_category_md(
            category=category, labels=labels, config=config
        )
        markdown += "\n---\n"

    # TODO: Markdown Footer
    markdown += "\n[footer]: #\n"
    if "markdown_footer_file" in config:
        if os.path.exists(config["markdown_footer_file"]):
            with open(config["markdown_footer_file"], "r") as f:
                markdown += str(f.read()) + "\n"
        else:
            log.warning(
                f"Markdown footer file not found: {config['markdown_footer_file']}. Using default footer."
            )
            markdown += "\n---\n"
            markdown += "Generated by [Awesome List Generator](https://github.com/derekvincent/awesome-list-generator)\n"

    return markdown


def generate_default_md(config: dict) -> str:
    """
    Generates a default markdown file when no items are found.
    """
    markdown = ""
    markdown += generate_title_md(config=config)
    markdown += "\n**Welcome to your fresh Awesome List!**\n"
    markdown += "\nNow add categories and items to your new `awesome-list.yaml` file to get started.\n"

    return markdown


class MarkdownWriter:
    def __init__(self):
        pass

    def write_output(
        self,
        categorized_items: OrderedDict,
        labels: list,
        config: dict,
    ) -> None:
        """
        Write the
        """

        """
        Read the last generated file 
        """
        last_readme_md = ""
        try:
            with open(config["output_file"], "r") as f:
                last_readme_md = f.read()
        except FileNotFoundError as err:
            log.info(f"File Not Found: {config['output_file']} - {err}")

        # Generate the markdown content
        if categorized_items:
            markdown = generate_md(
                categories=categorized_items, labels=labels, config=config
            )
        else:
            log.application("Generating Default README.")
            markdown = generate_default_md(config=config)

        current_build_time = datetime.today().strftime("%Y-%m-%d")
        base_dir = os.path.dirname(config["output_file"])
        
        # Generate the changes markdown
        changes_md = generate_changes_md(last_readme_md, markdown, current_build_time)

        if config["awesome_history_folder"]:
            changes_md_file_name = current_build_time + "_changes.md"

            ## Create the history folder if it does not exist
            history_dir = os.path.join(base_dir, config["awesome_history_folder"])
            os.makedirs(history_dir, exist_ok=True)

            # If the file already exists, append the current time to the file name
            history_file_path = os.path.join(history_dir, changes_md_file_name)
            if os.path.exists(history_file_path):
                changes_md_file_name = f"{current_build_time}-{datetime.now().strftime('%H-%M')}_changes.md"
                history_file_path = os.path.join(history_dir, changes_md_file_name)

            # Write the changes markdown to the history folder
            with open(history_file_path, "w") as f:
                f.write(changes_md)

        # Write the latest changes to the latest_changes.md file
        latest_changes_path = os.path.join(base_dir, config["latest_changes_file"])
        log.info(f"Writing latest changes to {latest_changes_path}")
        with open(latest_changes_path, "w") as f:
            f.write(changes_md)

        # Write the final markdown to the output file
        log.info(f"Writing Awsesome list markdown to {config['output_file']}")
        with open(config["output_file"], "w") as f:
            f.write(markdown)
        return markdown
