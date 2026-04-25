import logging
import pprint
from collections import OrderedDict

import requests

# from typing import List, Tuple
from bs4 import BeautifulSoup

from awesome_list import utils

log = logging.getLogger(__name__)


def get_items_metadata(item: dict) -> dict:

    if utils.is_url_valid(item["link_id"]):
        try:
            request_headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "accept-language": "en-US,en;q=0.5",
                "accept-encoding": "gzip, deflate, br",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "dnt": "1",
                "upgrade-insecure-requests": "1",
                "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="137", "Chromium";v="137"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "sec-gpc": "1",
            }

            response = requests.get(
                item["link_id"], headers=request_headers, timeout=10
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                meta_tags = soup.find_all("meta")
                metadata = {}
                for tag in meta_tags:
                    if "name" in tag.attrs:
                        name = tag.attrs["name"]
                        content = tag.attrs.get("content", "")
                        metadata[name] = content
                    elif "property" in tag.attrs:
                        property = tag.attrs["property"]
                        content = tag.attrs.get("content", "")
                        metadata[property] = content

                return metadata

            else:
                log.error(
                    f"Issue with fetching metadata for {item['link_id']} "
                    f"Status Code: {response.status_code}"
                )

        except requests.exceptions.RequestException as e:
            log.error(f"Error fetching {item['link_id']}: {e}")
            return None
    else:
        log.application(f"Invalid URL: {item['link_id']}")
    return None


def update_category(item: dict, categories: OrderedDict, default_category: str) -> None:
    """
    Takes the list of resourse items and check if a category has been assigned
    or if the assigned category is in the category config. If not then it assigns
    the category as `default_category` as set in the config.
    """
    if not item.get("category"):
        # If Category is not set or is empty, set it to the default.
        item["category"] = default_category

    if item["category"] not in categories:
        log.application(
            f"Resource: {item['name']} category {item['category']} "
            "was not found in the category configuration. Setting to default."
        )
        item["category"] = default_category


def update_item(resource_item: dict) -> None:
    """
    Applies additional data attribute enrichment from sources such
    as the website metadata.
    """
    metadata = get_items_metadata(resource_item)

    if metadata:
        log.debug(
            f"Item Url: {resource_item['link_id']} \n Metadata: {pprint.pformat(metadata)}"
        )
        if title := metadata.get("og:title"):
            resource_item["name"] = title

        if description := metadata.get("description"):
            resource_item["description"] = description
        elif og_desc := metadata.get("og:description"):
            resource_item["description"] = og_desc

        if update_time := metadata.get("og:update_time"):
            resource_item["update_at"] = update_time
        else:
            resource_item["update_at"] = ""

        if published_time := metadata.get("article:published_time"):
            resource_item["published_at"] = published_time
        else:
            resource_item["published_at"] = ""

    log.info(f"Updated item {resource_item['name']} with metadata.")


def categorize_items(items: list, categories: OrderedDict) -> None:
    categorized_items = categories
    for item in items:
        if "items" not in categorized_items[item["category"]]:
            categorized_items[item["category"]]["items"] = []
        if not item["hidden"] or item.get("always_include"):
            categorized_items[item["category"]]["items"].append(item)
            log.info(f"{item['name']} was added to category {item['category']}.")
        else:
            log.application(
                f"{item['name']} was set to hidden and will not be included."
            )

    return categorized_items


def category_structure(awesome_list_obj: OrderedDict) -> None:
    subcategories = []
    for category_key in awesome_list_obj:
        category = awesome_list_obj[category_key]
        try:
            if category.get("parent"):
                if "subcategories" not in awesome_list_obj[category["parent"]]:
                    awesome_list_obj[category["parent"]]["subcategories"] = {}
                awesome_list_obj[category["parent"]]["subcategories"][category_key] = (
                    category
                )
                subcategories.append(category_key)
        except KeyError as e:
            log.application(
                f"KeyError: {e} in category {category_key}. "
                "This may be due to a missing parent category."
            )
    for category_key in subcategories:
        del awesome_list_obj[category_key]


def process_awesome_items(
    items: list, categories: OrderedDict, config: dict
) -> OrderedDict:

    processed_items = []
    unique_items = set()

    """
    Process the list items 
    """
    for item in items:
        if item["link_id"] in unique_items:
            log.application(
                f"List Item {item['name']} : {item['link_id']} is a duplicate."
            )
            continue
        unique_items.add(item["link_id"])

        if item.get("hidden") is None:
            item["hidden"] = False

        try:
            update_item(item)
        except Exception as err:
            item["hidden"] = True
            log.error(f"Item: {item['link_id']} returned error: {err}")

        if not item.get("description"):
            item["description"] = ""

        update_category(item, categories, config["default_category"])

        processed_items.append(item)

    awesome_list_obj = categorize_items(processed_items, categories)
    category_structure(awesome_list_obj=awesome_list_obj)

    return awesome_list_obj
