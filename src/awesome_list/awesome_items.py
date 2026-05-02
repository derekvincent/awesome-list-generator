import logging
import os
import pprint
import xml.etree.ElementTree as ET
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urljoin, urlparse

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

def _parse_podcast_rss(rss_url: str) -> dict | None:
    """Fetches and parses an RSS feed to get the latest episode data."""
    log.info(f"Found RSS feed, attempting to parse: {rss_url}")
    try:
        response = requests.get(rss_url, headers=REQUEST_HEADERS, timeout=10)
        if response.status_code != 200:
            log.warning(f"Failed to fetch RSS feed {rss_url}, status: {response.status_code}")
            return None

        root = ET.fromstring(response.content)
        latest_item = root.find(".//item")
        if latest_item is None:
            log.warning(f"No <item> tags found in RSS feed: {rss_url}")
            return None

        podcast_meta = {"media_type": "podcast"}

        if (title_tag := latest_item.find("title")) is not None and title_tag.text:
            podcast_meta["latest_episode_title"] = title_tag.text

        if (pub_date_tag := latest_item.find("pubDate")) is not None and pub_date_tag.text:
            pub_date_str = pub_date_tag.text
            dt_object = None
            # Common RSS date formats, handle timezone name like GMT
            for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z"):
                try:
                    if " GMT" in pub_date_str:
                        pub_date_str = pub_date_str.replace(" GMT", " +0000")
                    dt_object = datetime.strptime(pub_date_str, fmt)
                    break
                except ValueError:
                    continue

            if dt_object:
                podcast_meta["latest_episode_date"] = dt_object.isoformat()
            else:
                podcast_meta["latest_episode_date"] = pub_date_str  # Fallback
        return podcast_meta
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        log.warning(f"Could not fetch or parse RSS feed at {rss_url}: {e}")
        return None
    
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
                # --- General Meta Tag Scraping ---
                meta_tags = soup.find_all("meta")
                metadata = {}
                for tag in meta_tags:
                    if "name" in tag.attrs:
                        name = tag.attrs["name"]
                        content = tag.attrs.get("content", "")
                        metadata[name] = content
                    elif "property" in tag.attrs:
                        property_val = tag.attrs["property"]
                        content = tag.attrs.get("content", "")
                        metadata[property_val] = content
                    elif "itemprop" in tag.attrs: # New: Capture itemprop attributes from meta tags
                        itemprop_name = tag.attrs["itemprop"]
                        content = tag.attrs.get("content", "")
                        metadata[f"itemprop:{itemprop_name}"] = content

                # --- Type Detection and Enrichment ---
                parsed_url = urlparse(item["link_id"])

                # 1. YouTube Detection
                if "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
                    metadata["media_type"] = "video.youtube"

                # 2. Podcast Detection (via RSS feed)
                rss_link_tag = soup.find("link", {"type": "application/rss+xml"})
                if rss_link_tag and rss_link_tag.has_attr("href"):
                    rss_url = urljoin(item["link_id"], rss_link_tag["href"])
                    if podcast_data := _parse_podcast_rss(rss_url):
                        # Merge podcast data, preferring podcast-specific keys
                        metadata.update(podcast_data)

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
        log.warning(f"Invalid URL: {item['link_id']}")
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
            if not resource_item.get("name"):
                resource_item["name"] = title

        if not resource_item.get("description"):
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

        # New: Extract media-specific metadata
        if thumbnail_url := metadata.get("og:image"):
            resource_item["thumbnail_url"] = thumbnail_url

        if video_url := metadata.get("og:video:url") or metadata.get("og:video:secure_url"):
            resource_item["video_embed_url"] = video_url

        if audio_url := metadata.get("og:audio:url") or metadata.get("og:audio:secure_url"):
            resource_item["audio_embed_url"] = audio_url

        if media_type := metadata.get("media_type") or metadata.get("og:type") or metadata.get("itemprop:type"):
            resource_item["media_type"] = media_type

        # Duration can come from itemprop or specific OG tags
        if duration := metadata.get("itemprop:duration") or metadata.get("og:video:duration") or metadata.get("og:audio:duration"):
            resource_item["duration"] = duration

        # View count is often an itemprop, but less reliably in meta tags.
        # For now, we'll only capture if it's in a meta tag with itemprop.
        if view_count := metadata.get("itemprop:interactionCount"):
            resource_item["view_count"] = view_count

        # New: Podcast-specific metadata
        if latest_episode_title := metadata.get("latest_episode_title"):
            resource_item["latest_episode_title"] = latest_episode_title
        if latest_episode_date := metadata.get("latest_episode_date"):
            resource_item["latest_episode_date"] = latest_episode_date

    log.info(f"Updated item {resource_item.get('name', resource_item['link_id'])} with metadata.")


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


def sort_categories_dict(categories: OrderedDict, sort_order: str) -> OrderedDict:
    """
    Recursively sorts the categories dictionary (and any subcategories) alphabetically.
    """
    if sort_order not in ["asc", "desc"]:
        return categories

    sorted_keys = sorted(
        categories.keys(),
        key=lambda k: str(categories[k].get("label", categories[k].get("name", k))).lower(),
        reverse=(sort_order == "desc")
    )

    sorted_cats = OrderedDict()
    for k in sorted_keys:
        cat = categories[k]
        if "subcategories" in cat and isinstance(cat["subcategories"], dict):
            cat["subcategories"] = sort_categories_dict(cat["subcategories"], sort_order)
        sorted_cats[k] = cat

    return sorted_cats


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

    sort_order = config.get("category_sort", "set")
    sorted_awesome_list_obj = sort_categories_dict(awesome_list_obj, sort_order)

    return sorted_awesome_list_obj
