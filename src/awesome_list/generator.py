import logging
import os 
from typing import Tuple
from collections import OrderedDict

import yaml

from . import resource_items
from . import default_config
from . import markdown_writer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG) 

def parse_resource_items_yaml(
        resource_items_path: str,
) -> Tuple[dict, list, OrderedDict, list]:
    parsed_yaml = {}

    if not os.path.exists(resource_items_path):
        raise Exception(
            "Resource Items yaml file does not exist: " + os.path.abspath(resource_items_path)
        )
    with open(resource_items_path, "r") as stream:
        parsed_yaml = yaml.safe_load(stream)

    #print(parsed_yaml["resource_items"])
    resource_items_list = parsed_yaml["resource_items"]
    
    config = default_config.initialize_configuration(
        parsed_yaml["config"] if "config" in parsed_yaml else {}
    )
    
    categories = default_config.initialize_categories(
        config, parsed_yaml["categories"] if "categories" in parsed_yaml else [])
    
    tags = parsed_yaml["tags"] if "tags" in parsed_yaml else []

    res_items = resource_items.process_resource_items(resource_items_list, categories, config)
    #log.info("Config: %s", config )
    #log.info("Categories: %s", categories)
    resource_items.categorize_items(res_items, categories)
    #log.info("Categories: %s", categories)

    markdown = markdown_writer.MarkdownWriter()
    md_out = markdown.write_output(config, res_items, categories, tags)
    log.info("Mardown Output: \n" + md_out)
    return config, res_items, categories, tags
