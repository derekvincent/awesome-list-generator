
from awesome_list.utils import is_url_valid


def test_is_url_valid_with_valid_urls():
    assert is_url_valid("https://kemikal.io") is True
    assert is_url_valid("http://github.com/derekvincent") is True
    assert is_url_valid("https://example.com/path/to/resource?query=1&lang=en") is True
    assert is_url_valid("http://localhost:8080") is True

def test_is_url_valid_with_invalid_urls():
    assert is_url_valid("not_a_url") is False
    assert is_url_valid("ftp://unsupported.protocol.com") is False
    assert is_url_valid("") is False
    assert is_url_valid(None) is False
    assert is_url_valid("http://") is False