import os
import logging

from collections import OrderedDict

log = logging.getLogger(__name__)

def generate_item_md(item: dict, labels: list, config: dict) -> str:
    item_markdown = ""

    item_label_md = ""
    if "labels" in item: 
        for label_id in item["labels"]:
            for label in labels:
                if label.get("label") == label_id: 
                    if "image" in label:
                        item_label_md += '<code><img src="{image}" alt="{name}" style="display:inline;" width="16" height="16"></code>'.format(
                        image=label["image"], name=label["name"])
                    if "image" not in label and "name" in label:
                        item_label_md += '<code>{name}</code>'.format(
                        name=label["name"])

    item_markdown = '- <b><a href="{homepage}">{name}</a></b> {labels} - {description}'.format(
      homepage = item["link_id"],
      name = item["name"],
      labels = item_label_md,
      description = item["description"]
    )

    return item_markdown

def generate_category_md(category: dict, labels: list, config: dict, heading_level: int = 2) -> str:
    category_markdown = ""

    category_markdown += "#" * heading_level + " " + category["label"] + "\n\n"

    back_to_top_anchor = "#contents"

    category_markdown += f'<a href="{back_to_top_anchor}"><img align="right" width="15" height="15" src="https://git.io/JtehR" alt="Back to top"></a>\n\n'

    if "description" in category:
        category_markdown += "_" + category["description"].strip() + "_\n\n"

    if "items" in category:
        for item in category["items"]:
            item_markdown = generate_item_md(item, labels, config)
            category_markdown += item_markdown + "\n"

    if "subcategories" in category:
        for subcategory in category["subcategories"]:
            category_markdown += generate_category_md(subcategory, labels, config, 3)

    return category_markdown

def generate_legend_md(labels: list, config: dict) -> str: 
    legend_md = ""

    legend_md = "## Legend\n"
    for label in labels:
        #label = labels[label_key]
        if "image" in label and "name" in label:
            legend_md += '- <img src="{image}" style="display:inline;" width="13" height="13">&nbsp; <b>{name}</b> {description}\n'.format(
                image=label["image"], 
                name=label["name"],
                description=" - " + label["description"] if "description" in label else ""
            )

    return legend_md


def category_toc_md(category: dict, items_len: int, subcategory: bool = False) -> str:
        
        category_toc_markdown = ""
        url = "#" + category["name"]
        items_count = 0
        if "items" in category:
            items_count += len(category["items"])
        
        category_toc_markdown += "{bullet} [{title}]({url}) _{items_count} items_\n".format(
            bullet="    -" if subcategory else "-",
            title=category["label"], 
            url=url, 
            items_count=items_count
        )

        return category_toc_markdown


def generate_toc_md(categories: OrderedDict, config: dict) -> str:
     
    toc_markdown = ""

    for category_key in categories:
        category = categories[category_key]
        items_count = 0
        if "items" in category:
            items_count += len(category["items"])
        toc_markdown += category_toc_md(category, items_count)

        if "subcategories" in category:
            for subcategory in category["subcategories"]:
                items_count = 0 
                if "items" in subcategory:
                    items_count += len(subcategory["items"])
                toc_markdown += category_toc_md(subcategory, items_count, True)

    return toc_markdown + "\n"

def generate_title_md(config: dict) -> str:
    title_markdown = ""

    title_markdown = "# " + config["list_title"]

    return title_markdown + "\n"


def generate_md(categories: OrderedDict, labels: list, config: dict) -> str:
     
    markdown = ""

    markdown += generate_title_md(config=config)
    # TODO: Markdown Header 

    if "markdown_header_file" in config:
        if os.path.exists(config["markdown_header_file"]):
            with open(config["markdown_header_file"], "r") as f:
                markdown += (str(f.read()) + "\n")            
    # TOC 
    markdown += generate_toc_md(categories=categories, config=config)

    # Legend
    if len(labels) > 0:
        markdown += generate_legend_md(labels=labels, config=config)

    # Body 
    for category_key in categories:
        category = categories[category_key]
        markdown += generate_category_md(category=category, labels=labels, config=config)
    
    # TODO: Markdown Footer  

    if "markdown_footer_file" in config:
        if os.path.exists(config["markdown_footer_file"]):
            with open(config["markdown_footer_file"], "r") as f:
                markdown += (str(f.read())+ "\n")     

    return markdown

class MarkdownWriter:

    def __init__(self):
            pass

    def write_output(self, categorized_items: OrderedDict, labels: list, config: dict,) -> None:
          
        '''
        Write the 
        '''
        #for label in labels:
        #    log.info(f'Label: {label.get("label")}')
        #label_sap = [label for label in labels if label.get("label") == "sap"][0]
        #log.info(f'SAP Icon: {label_sap.get("image")}')
        markdown = generate_md(categories=categorized_items, labels=labels, config=config)
        
        with open(config["output_file"], "w") as f:
            f.write(markdown)
        return markdown

