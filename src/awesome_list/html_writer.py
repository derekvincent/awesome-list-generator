import logging
import os
import pprint
import shutil

# from datetime import datetime
from collections import OrderedDict

from jinja2 import Environment, FileSystemLoader

from awesome_list import utils

log = logging.getLogger(__name__)


def categories_content_list(
    categories: OrderedDict, config: dict, depth: int = 1
) -> OrderedDict:

    cl_depth = depth
    content_list = OrderedDict()

    for category_key in categories:
        category = categories[category_key]
        items_count = 0
        if "items" in category:
            items_count += len(category["items"])
        content_list[category_key] = category
        content_list[category_key]["item_count"] = items_count
        content_list[category_key]["depth"] = cl_depth

        if "subcategories" in category:
            categories_content_list(category["subcategories"], config, cl_depth + 1)

    return content_list


def categories_to_toc(categories: OrderedDict, config: dict, depth: int = 1) -> list:

    toc_depth = depth
    toc = []

    ##Set the list title as the level 1 in the TOC
    if toc_depth == 1:
        toc_children = []
        if categories:
            toc_children = categories_to_toc(categories, config, toc_depth + 1)
        toc.append(
            {
                "name": config.get("list_title"),
                "label": config.get("list_title"),
                "depth": toc_depth,
                "item_count": 0,
                "children": toc_children,
            }
        )
    else:
        for category_key in categories:
            category = categories[category_key]
            toc_children = []
            items_count = 0
            if "items" in category:
                items_count += len(category["items"])
            if "subcategories" in category:
                toc_children = categories_to_toc(
                    category["subcategories"], config, toc_depth + 1
                )
            toc.append(
                {
                    "name": category_key,
                    "label": category.get("label", category_key),
                    "depth": toc_depth,
                    "item_count": items_count,
                    "children": toc_children,
                }
            )

    return toc


def html_header_to_html(config: dict) -> str:
    """
    Convert the markdown header files to HTML.
    """
    html_content = {}
    if "markdown_header_file" in config:
        if os.path.exists(config["markdown_header_file"]):
            header_env = Environment(
                variable_start_string="{", variable_end_string="}"
            ).from_string(
                utils.convert_markdown_to_html(config["markdown_header_file"])
            )
            # header_env.variable_start_string = "{"
            # header_env.variable_end_string = "}"
            html_content = header_env.render(
                awesome_title=config.get("list_title", ""),
                awesome_subtitle=config.get("list_subtitle", ""),
                awesome_description=config.get("list_description", ""),
            )

        else:
            log.warning(
                f"Markdown header file not found: {config['markdown_header_file']}"
            )
            html_content = ""
    else:
        html_content = ""

    return html_content


def html_footer_to_html(config: dict) -> str:
    """
    Convert the markdown footer files to HTML.
    """
    html_content = {}
    if "markdown_footer_file" in config:
        if os.path.exists(config["markdown_footer_file"]):
            html_content = utils.convert_markdown_to_html(
                config["markdown_footer_file"]
            )
        else:
            log.warning(
                f"Markdown footer file not found: {config['markdown_footer_file']}"
            )
            html_content = ""
    else:
        html_content = ""

    return html_content


def generate_web(
    categories: OrderedDict, labels: list, config: dict, theme: str
) -> str:
    """
    Generate the generate webpage content for the categorized items.
    """

    """
    This function will populate the variables to use in the theme template.
    1. TOC or Categories 
        Be able to set the depth - 0 
    2. Legend - a list of the labels 
    3. Header and Footer details - converted markdown to HTML
    4. Items list - a list of items with their details and categorization
    """

    html_context = {}

    html_context["title"] = config.get("list_title", "")
    html_context["subtitle"] = config.get("list_subtitle", "")
    html_context["description"] = config.get("list_description", "")
    html_context["header"] = html_header_to_html(config)
    html_context["footer"] = html_footer_to_html(config)
    html_context["theme"] = theme
    html_context["css_dir"] = "css"

    html_context["toc"] = categories_to_toc(categories, config, depth=1)
    log.info(f"TOC: \n{pprint.pformat(html_context['toc'], indent=2)}")
    html_context["categories"] = categories_content_list(categories, config, depth=1)
    log.info(f"Content: \n{pprint.pformat(html_context['categories'], indent=2)}")
    return html_context


def copy_file(source_path: str, destination_path: str) -> None:
    """
    Copy a file from source to destination.
    """

    try:
        shutil.copy2(source_path, destination_path)
        log.info(f"Copied {source_path} to {destination_path}")
    except Exception as e:
        log.error(f"Failed to copy {source_path} to {destination_path}: {e}")
    return


class HtmlWriter:
    def __init__(self):
        pass

    def write_output(
        self,
        categorized_items: OrderedDict,
        labels: list,
        config: dict,
        theme: str,
    ) -> None:

        # Generate the web-site content
        if categorized_items:
            awesomelist_web = generate_web(
                categories=categorized_items, labels=labels, config=config, theme=theme
            )
        else:
            log.application("Generating Default Webpage.")
            # markdown = generate_default_md(config=config)

        ## Setup the out and templates to use
        ## TODO: Allow for custom templates
        output_file = config.get("html_output_file", "index.html")
        environment = Environment(
            loader=FileSystemLoader(
                os.path.join(os.path.dirname(__file__), "web-template")
            )
        )
        output_template = environment.get_template("main.html")

        ## Create the web output folder if it does not exist
        os.makedirs(
            os.path.join(os.path.dirname(config["output_file"]), config["html_folder"]),
            exist_ok=True,
        )

        with open(
            os.path.join(
                os.path.dirname(config["output_file"]),
                config["html_folder"],
                output_file,
            ),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(output_template.render(awesomelist_web))
        log.info(f"Generated {output_file}")

        """ Copy the CSS files to the output folder """
        css_source_folder = os.path.join(
            os.path.dirname(__file__), "web-template", "css"
        )
        css_destination_folder = os.path.join(
            os.path.dirname(config["output_file"]), config["html_folder"], "css"
        )
        os.makedirs(css_destination_folder, exist_ok=True)
        for css_file in os.listdir(css_source_folder):
            if css_file.endswith(".css"):
                copy_file(
                    os.path.join(css_source_folder, css_file),
                    os.path.join(css_destination_folder, css_file),
                )
        return
