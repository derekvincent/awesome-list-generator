
from collections import OrderedDict
from datetime import datetime
from typing import List, Tuple

def generate_item_md(item: dict, config: dict) -> str:
    item_markdown = ""

    item_markdown = '- <b><a href="{homepage}">{name}</a></b> - {description}'.format(
      homepage = item["link_id"],
      name = item["name"],
      description = item["description"]
    )

    return item_markdown

def generate_category_md(category: dict, config: dict, heading_level: int = 2) -> str:
    category_markdown = ""

    category_markdown += "#" * heading_level + " " + category["label"] + "\n\n"

    back_to_top_anchor = "#contents"

    category_markdown += f'<a href="{back_to_top_anchor}"><img align="right" width="15" height="15" src="https://git.io/JtehR" alt="Back to top"></a>\n\n'

    if "description" in category:
        category_markdown += "_" + category["description"].strip() + "_\n\n"

    if "items" in category:
        for item in category["items"]:
            item_markdown = generate_item_md(item, config)
            category_markdown += item_markdown + "\n"

    if "subcategories" in category:
        for subcategory in category["subcategories"]:
            category_markdown += generate_category_md(subcategory, config, 3)

    return category_markdown

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

    title_markdown = "#" + config["list_title"]

    return title_markdown + "\n"


def generate_md(categories: OrderedDict, config: dict) -> str:
     
    markdown = ""

    markdown += generate_title_md(config)
    # TODO: Markdown Header 

    # TOC 
    markdown += generate_toc_md(categories, config)

    # Body 
    for category_key in categories:
        category = categories[category_key]
        markdown += generate_category_md(category, config)
    
    # TODO: Markdown Footer  

    

    return markdown

class MarkdownWriter:

    def __init__(self):
            pass

    def write_output(self, categorized_items: OrderedDict, config: dict,) -> None:
          
        '''
        Write the 
        '''

        markdown = generate_md(categorized_items, config)
        
        with open(config["output_file"], "w") as f:
            f.write(markdown)

        return markdown

