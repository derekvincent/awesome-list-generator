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

def update_category(resource_item: dict, categories: OrderedDict) -> None:
    '''
    Takes the list of resourse items and check if a category has been assigned
    or if the assigned category is in the category config. If not then it assigns
    the category as 'other'. 
    '''
    # TODO: Change the default from other to set in the config. 
    if "category" not in  resource_item:
        # If Category is not set then set it to the default.
        resource_item["category"] = "other"

    if not any(category["name"] == resource_item["category"] for category in categories):
        log.info(
            "Resource: " + resource_item["name"] +
            " category " + resource_item["category"] +
            " was not found in the category configuration. Setting to default."
            )
        resource_item["category"] = "other"

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

        update_category(resource_item, categories)

        #log.info("Resource Items: %s ", resource_item)
        processed_resource_items.append(resource_item)


    return process_resource_items