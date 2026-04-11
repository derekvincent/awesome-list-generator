import logging
import os
from collections import OrderedDict
from typing import Tuple

import yaml

from awesome_list import (
    awesome_items,
    default_config,
    html_writer,
    logger,
    markdown_writer,
    utils,
)

log = logging.getLogger(__name__)


def yaml_parser(
        awesome_items_path: str,
) -> Tuple[dict, OrderedDict, list, list]:
    parsed_yaml = {}

    if not os.path.exists(awesome_items_path):
        raise Exception(
            "Awesome Items yaml file does not exist: " + os.path.abspath(awesome_items_path)
        )
    with open(awesome_items_path, "r") as stream:
        parsed_yaml = yaml.safe_load(stream)

    items = parsed_yaml["items"]
    
    config = default_config.initialize_configuration(
        parsed_yaml["config"] if "config" in parsed_yaml else {}
    )
    
    categories = default_config.initialize_categories(
        config, parsed_yaml["categories"] if "categories" in parsed_yaml else [])
    
    tags = parsed_yaml["labels"] if "labels" in parsed_yaml else []



    return config, categories, items, tags

def generate_markdown(list_object, labels, config) -> None:

    try: 

        markdown = markdown_writer.MarkdownWriter()        
        markdown.write_output(list_object, labels, config)

    except Exception as ex:
        log.application("Failed to generate markdown.", exc_info=ex)
        log.error("Failed to generate markdown.", exc_info=ex)

def generate_webpage(list_object, labels, config) -> None:

    log.info("Generating HTML webpage.")
    html = html_writer.MarkdownWriter()
    html.write_output(list_object, labels, config, theme=config.get("html_theme", "default"))

def generate(items_yaml_path: str, debug: bool) -> None:    
        try: 
            config, categories, items, labels = yaml_parser(awesome_items_path=items_yaml_path)
            if debug:
                config["debug"] = True

            logger.initialize_logging(file_path=config["log_folder"], disable_log=config["disable_logging"], debug=config["debug"])
            
            if items:
                list_object = awesome_items.process_awesome_items(
                    items=items, 
                    categories=categories, 
                    config=config)
                
                #generate_markdown(list_object, labels, config)
                if config.get("html_enable", True):
                    generate_webpage(list_object, labels, config)

            else:
                log.application("No items found in the awesome list. Generating Default README.")
                generate_markdown(dict(), labels, config)

        except Exception as ex:
            log.application("Failed to generate markdown.", exc_info=ex)
            log.error("Failed to generate markdown.", exc_info=ex)
            utils.exit_process(1)