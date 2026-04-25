from collections import OrderedDict

from awesome_list.models import AppConfig, Category

UP_ARROW_IMAGE = "https://git.io/JtehR"


def initialize_configuration(cfg: dict) -> AppConfig:
    # AppConfig handles all default assignments natively
    return AppConfig.from_dict(cfg)


def initialize_categories(config: AppConfig, categories: list) -> OrderedDict:

    return_categories = OrderedDict()

    if categories:
        for category in categories:
            if "label" not in category:
                category["label"] = category["name"]
            return_categories[category["name"]] = Category.from_dict(category)

    if config.default_category not in return_categories:
        # Add others category at the last position
        return_categories[config.default_category] = Category(
            name=config.default_category, label="Others"
        )

    return return_categories
