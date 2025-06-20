import logging
import requests

from collections import OrderedDict
# from typing import List, Tuple 

from bs4 import BeautifulSoup

from . import utils

log = logging.getLogger(__name__)

def resource_items_metadata(resource_item: dict) -> dict:

    if utils.is_url_valid(resource_item["link_id"]):
        request_headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(resource_item["link_id"], headers=request_headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_tags = soup.find_all('meta')
            metadata = {}
            for tag in meta_tags:
                if 'name' in tag.attrs:
                    name = tag.attrs['name']
                    content = tag.attrs.get('content', '')
                    metadata[name] = content
                elif 'property' in tag.attrs:
                    property = tag.attrs['property']
                    content = tag.attrs.get('content', '')
                    metadata[property] = content
            
            return metadata

    else:
        log.info("Not a Valid URL.")

    return None

def update_category(resource_item: dict, categories: OrderedDict, default_category: str) -> None:
    '''
    Takes the list of resourse items and check if a category has been assigned
    or if the assigned category is in the category config. If not then it assigns
    the category as `default_category` as set in the config. 
    '''
    # TODO: Change the default from other to set in the config. 
    if "category" not in  resource_item:
        # If Category is not set then set it to the default.
        resource_item["category"] = default_category

    if resource_item["category"] not in categories:
        log.info(
            "Resource: " + resource_item["name"] +
            " category " + resource_item["category"] +
            " was not found in the category configuration. Setting to default."
            )
        resource_item["category"] = default_category

def update_resource_item(resource_item: dict) -> None:
    '''
    Applies additional data attribute enrichment from sources such 
    as the website metadata. 
    '''
    metadata = resource_items_metadata(resource_item)

    #if resource_item['description'] := metadata['description']:
    #print(metadata)
    if 'description' in metadata:
        resource_item['description'] = metadata['description']
    elif 'og:description' in metadata:
        resource_item['description'] = metadata['og:description']
    
    if 'og:update_time' in metadata:
        resource_item['update_at'] = metadata['og:update_time']
    
    if 'article:published_time' in metadata:
        resource_item['published_at'] = metadata['article:published_time']

def categorize_items(items: list, categories: OrderedDict) -> None: 
    categorized_items = categories
    for item in items:

        if "items" not in categorized_items[item["category"]]:
            categorized_items[item["category"]]["items"] = []
        categorized_items[item["category"]]["items"].append(item)

    return categorized_items

def category_strucutre(awseome_list_obj: OrderedDict) -> None:
        subcategories = []
        for category_key in awseome_list_obj:
            category = awseome_list_obj[category_key]
            if "parent" in category:
                if "subcategories" not in awseome_list_obj[category["parent"]]:
                    awseome_list_obj[category["parent"]]["subcategories"] = []
                awseome_list_obj[category["parent"]]["subcategories"].append(category)
                subcategories.append(category_key)

        for category_key in subcategories:    
            del awseome_list_obj[category_key]
                                 

def process_resource_items(
        resource_items: list, categories: OrderedDict, config: dict
) -> list:
    processed_resource_items = []
    unique_resource_items = set()

    for item in resource_items:
        resource_item = item
        if resource_item["link_id"] in unique_resource_items:
            log.info("Resource Item " + resource_item["name"] + " : " + resource_item["link_id"] +
                    " is a duplicate.")
            continue
        unique_resource_items.add(resource_item["link_id"])

        #update_resource_item(resource_item)

        if not resource_item.get("description"):
            resource_item["description"] = ""

        update_category(resource_item, categories, config["default_category"])

        processed_resource_items.append(resource_item)

    return processed_resource_items

def process_awesome_items(
        items: list, categories: OrderedDict, config: dict
) -> OrderedDict:

    awesome_list_obj = []
    processed_items = [] 
    unique_items = set()

    """
    Process the list items 
    """
    for item in items: 
        if item["link_id"] in unique_items:
            log.info("List Item " + item["name"] + " : " + item["link_id"] +
                    " is a duplicate.")
            continue
        unique_items.add(item["link_id"])

        #update_resource_item(resource_item)
        if not item.get("description"):
            item["description"] = ""

        update_category(item, categories, config["default_category"])

        processed_items.append(item)
    
    awesome_list_obj = categorize_items(processed_items, categories)
    category_strucutre(awseome_list_obj=awesome_list_obj)

    return awesome_list_obj