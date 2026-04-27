import logging
import os
import pprint
from collections import OrderedDict
from urllib.parse import urlparse

import requests

# from typing import List, Tuple
from bs4 import BeautifulSoup

from awesome_list import utils

log = logging.getLogger(__name__)


REQUEST_HEADERS = {
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

def get_github_metadata(link_id: str) -> dict | None:
    """
    Intercepts GitHub URLs and fetches extended metadata from the GitHub REST API.
    """
    parsed = urlparse(link_id)
    if parsed.netloc != "github.com":
        return None
        
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return None
        
    owner, repo = parts[0], parts[1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    
    if "GITHUB_TOKEN" in os.environ:
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "og:title": data.get("name"),
                "description": data.get("description"),
                "stars": data.get("stargazers_count"),
                "forks": data.get("forks_count"),
                "license": data.get("license", {}).get("name") if data.get("license") else None,
                "article:published_time": data.get("created_at"),
                "og:update_time": data.get("pushed_at") or data.get("updated_at"),
            }
        else:
            log.warning(f"GitHub API returned {response.status_code} for {link_id}")
    except requests.exceptions.RequestException as e:
        log.error(f"Error fetching GitHub API for {link_id}: {e}")
        
    return None


def get_items_metadata(item: dict) -> dict | None:

    if utils.is_url_valid(item["link_id"]):
        if github_data := get_github_metadata(item["link_id"]):
            return github_data

        try:
            response = requests.get(
                item["link_id"], headers=REQUEST_HEADERS, timeout=10
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



def check_link(url: str) -> tuple[bool, str]:
    """
    Fast check to see if a URL is alive without downloading the full page body.
    """
    if not utils.is_url_valid(url):
        return False, "Invalid URL format"

    try:
        # Use GET with stream=True to avoid downloading the full body for speed
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=10, stream=True)
        response.close()

        if response.status_code < 400:
            return True, f"HTTP {response.status_code}"
        elif response.status_code in [401, 403, 405, 429]:
            # Some sites block automated scripts but are technically alive and resolving
            return True, f"HTTP {response.status_code} (Protected but reachable)"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, str(e)


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
            
        if stars := metadata.get("stars"):
            resource_item["stars"] = stars
            
        if forks := metadata.get("forks"):
            resource_item["forks"] = forks
            
        if license_name := metadata.get("license"):
            resource_item["license"] = license_name

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
