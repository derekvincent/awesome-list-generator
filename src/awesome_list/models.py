from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AwesomeItem:
    name: str = ""
    link_id: str = ""
    description: str = ""
    category: str = ""
    labels: List[str] = field(default_factory=list)
    hidden: bool = False
    always_include: bool = False
    update_at: str = ""
    published_at: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "AwesomeItem":
        """Creates a dataclass instance ignoring any unexpected kwargs."""
        field_names = set(f.name for f in cls.__dataclass_fields__.values())
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __contains__(self, item):
        return hasattr(self, item)


@dataclass
class Category:
    name: str
    label: str
    description: str = ""
    parent: Optional[str] = None
    items: List[AwesomeItem] = field(default_factory=list)
    subcategories: Dict[str, "Category"] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        field_names = set(f.name for f in cls.__dataclass_fields__.values())
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __contains__(self, item):
        return hasattr(self, item)


@dataclass
class AppConfig:
    output_file: str = "README.md"
    latest_changes_file: str = "latest-changes.md"
    awesome_history_folder: str = "history"
    default_category: str = "other"
    disable_logging: bool = False
    log_folder: str = "logs"
    debug: bool = False
    up_arrow_image: str = "https://raw.githubusercontent.com/derekvincent/awesome-list-generator/main/assets/UpperCaret-32.png"
    category_sort: str = "set"
    list_title: str = "Awesome List"
    list_subtitle: str = ""
    list_description: str = ""
    markdown_header_file: str = "config/header.md"
    markdown_footer_file: str = "config/footer.md"
    html_output_file: str = "index.html"
    html_theme: str = "light"
    html_enable: bool = False
    html_folder: str = "html"

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        field_names = set(f.name for f in cls.__dataclass_fields__.values())
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def get(self, key, default=None):
        return getattr(self, key, default)

    def __contains__(self, item):
        return hasattr(self, item)
