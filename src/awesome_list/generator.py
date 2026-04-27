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
from awesome_list.models import AppConfig, AwesomeItem

log = logging.getLogger(__name__)


def yaml_parser(
    awesome_items_path: str,
) -> Tuple[AppConfig, OrderedDict, list, list]:

    if not os.path.exists(awesome_items_path):
        raise FileNotFoundError(
            f"Awesome Items yaml file does not exist: {os.path.abspath(awesome_items_path)}"
        )
    with open(awesome_items_path, "r") as stream:
        parsed_yaml = yaml.safe_load(stream)

    raw_items = parsed_yaml.get("items", [])
    items = [AwesomeItem.from_dict(item) for item in raw_items]

    config = default_config.initialize_configuration(parsed_yaml.get("config", {}))

    categories = default_config.initialize_categories(
        config, parsed_yaml.get("categories", [])
    )

    tags = parsed_yaml.get("labels", [])

    return config, categories, items, tags


def generate_markdown(list_object: OrderedDict, labels: list, config: dict) -> None:

    try:
        markdown = markdown_writer.MarkdownWriter()
        markdown.write_output(list_object, labels, config)

    except Exception as ex:
        log.application("Failed to generate markdown.", exc_info=ex)
        log.error("Failed to generate markdown.", exc_info=ex)


def generate_webpage(list_object: OrderedDict, labels: list, config: dict) -> None:

    log.info("Generating HTML webpage.")
    html = html_writer.HtmlWriter()
    html.write_output(
        list_object, labels, config, theme=config.get("html_theme", "default")
    )


def generate(items_yaml_path: str, debug: bool) -> None:
    try:
        config, categories, items, labels = yaml_parser(
            awesome_items_path=items_yaml_path
        )
        if debug:
            config["debug"] = True

        logger.initialize_logging(
            file_path=config["log_folder"],
            disable_log=config["disable_logging"],
            debug=config["debug"],
        )

        if items:
            list_object = awesome_items.process_awesome_items(
                items=items, categories=categories, config=config
            )

            generate_markdown(list_object, labels, config)
            if config.get("html_enable", True):
                generate_webpage(list_object, labels, config)

        else:
            log.application(
                "No items found in the awesome list. Generating Default README."
            )
            generate_markdown(dict(), labels, config)

    except Exception as ex:
        log.application("Failed to generate markdown.", exc_info=ex)
        log.error("Failed to generate markdown.", exc_info=ex)
        utils.exit_process(1)


def lint(items_yaml_path: str, debug: bool) -> None:
    try:
        config, categories, items, labels = yaml_parser(
            awesome_items_path=items_yaml_path
        )
        if debug:
            config["debug"] = True

        logger.initialize_logging(
            file_path=config["log_folder"],
            disable_log=config["disable_logging"],
            debug=config["debug"],
        )

        log.info(f"Starting linter for {len(items)} items...")
        broken_links = []

        for item in items:
            is_valid, msg = awesome_items.check_link(item["link_id"])
            if not is_valid:
                broken_links.append(item)
                log.warning(f"❌ BROKEN: {item['name']} ({item['link_id']}) - {msg}")
            else:
                log.info(f"✅ OK: {item['name']} - {msg}")

        if broken_links:
            log.error(f"Linting failed! Found {len(broken_links)} broken links.")
            utils.exit_process(1)
        else:
            log.info("Linting passed! All links are perfectly valid.")
            utils.exit_process(0)

    except Exception as ex:
        log.error("Failed to execute linter.", exc_info=ex)
        utils.exit_process(1)
