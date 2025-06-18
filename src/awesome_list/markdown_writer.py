
from collections import OrderedDict
from datetime import datetime
from typing import List, Tuple

def generate_item_md(item: dict, config: dict, tags: list) -> str:
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
            item_markdown = generate_item_md(item, config, {})
            category_markdown += item_markdown + "\n"

    return category_markdown

def generate_toc_md(categories: OrderedDict, config: dict) -> str:
     
    toc_markdown = ""

    for category_key in categories:
        category = categories[category_key]
        url = "#" + category["name"]
        items_count = 0
        if "items" in category:
            items_count += len(category["items"])
        
        toc_markdown += "- [{title}]({url}) _{items_count} items_\n".format(
            title=category["label"], url=url, items_count=items_count
        )

    return toc_markdown + "\n"


def generate_md(categories: OrderedDict, config: dict, tags: list) -> str:
     
    markdown = ""


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

    def write_output(self, config: dict, items: List[dict], categories: OrderedDict, tags: List) -> None:
          
        '''
        Write the 
        '''

        markdown = generate_md(categories, config, tags)
        
        with open(config["output_file"], "w") as f:
            f.write(markdown)

        return markdown

