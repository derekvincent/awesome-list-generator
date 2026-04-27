import pytest

from awesome_list.logger import add_application_level


@pytest.fixture(scope="session", autouse=True)
def setup_custom_logger():
    """Ensure the custom APPLICATION log level is monkey-patched before any tests run."""
    add_application_level()