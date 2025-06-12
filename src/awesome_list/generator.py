import logging
import os 
from typing import Tuple
from collections import OrderedDict

import yaml

from . import resource_items

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

    print(parsed_yaml["resource_items"])
    resource_items_list = parsed_yaml["resource_items"]
    config = {}
    categories = parsed_yaml["categories"]
    tags = []
    res_items = resource_items.process_resource_items(resource_items_list, categories, config)
    #print(res_items)
    return config, res_items, categories, tags
