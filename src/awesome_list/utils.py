import re
import logging


log = logging.getLogger(__name__)


url_validator = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE)

def is_url_valid(url: str) -> bool:
    return re.match(url_validator, url) is not None