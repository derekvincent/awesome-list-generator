import os
from unittest.mock import patch

import requests
import responses

from awesome_list.awesome_items import get_github_metadata


@responses.activate
def test_get_github_metadata_success():
    """
    Tests successful fetching and parsing of GitHub repo metadata.
    """
    # Arrange
    api_url = "https://api.github.com/repos/derekvincent/awesome-list-generator"
    mock_response = {
        "name": "awesome-list-generator",
        "description": "A tool to generate awesome lists.",
        "stargazers_count": 123,
        "forks_count": 45,
        "license": {"name": "MIT License"},
        "created_at": "2024-01-01T00:00:00Z",
        "pushed_at": "2024-05-15T10:00:00Z",
    }
    responses.add(responses.GET, api_url, json=mock_response, status=200)

    # Act
    metadata = get_github_metadata("https://github.com/derekvincent/awesome-list-generator")

    # Assert
    assert metadata is not None
    assert metadata["og:title"] == "awesome-list-generator"
    assert metadata["description"] == "A tool to generate awesome lists."
    assert metadata["stars"] == 123
    assert metadata["forks"] == 45
    assert metadata["license"] == "MIT License"
    assert metadata["article:published_time"] == "2024-01-01T00:00:00Z"
    assert metadata["og:update_time"] == "2024-05-15T10:00:00Z"


@responses.activate
@patch.dict(os.environ, {"GITHUB_TOKEN": "test_token_123"})
def test_get_github_metadata_with_auth_token():
    """
    Tests that the Authorization header is correctly added when GITHUB_TOKEN is set.
    """
    # Arrange
    api_url = "https://api.github.com/repos/user/repo"
    responses.add(
        responses.GET,
        api_url,
        json={"name": "repo"},
        status=200,
        match=[responses.matchers.header_matcher({"Authorization": "Bearer test_token_123"})],
    )

    # Act
    metadata = get_github_metadata("https://github.com/user/repo")

    # Assert
    assert metadata is not None
    assert len(responses.calls) == 1
    assert responses.calls[0].request.headers["Authorization"] == "Bearer test_token_123"


def test_get_github_metadata_non_github_url():
    """
    Tests that non-GitHub URLs are ignored and return None immediately.
    """
    metadata = get_github_metadata("https://example.com/user/repo")
    assert metadata is None


@responses.activate
def test_get_github_metadata_repo_not_found():
    """
    Tests graceful failure when the GitHub API returns a 404.
    """
    # Arrange
    api_url = "https://api.github.com/repos/user/nonexistent-repo"
    responses.add(responses.GET, api_url, json={"message": "Not Found"}, status=404)

    # Act
    metadata = get_github_metadata("https://github.com/user/nonexistent-repo")

    # Assert
    assert metadata is None


@patch("awesome_list.awesome_items.log")
@patch("awesome_list.awesome_items.requests.get", side_effect=requests.exceptions.Timeout)
def test_get_github_metadata_request_exception(mock_requests_get, mock_log):
    """
    Tests that request exceptions are caught and logged.
    """
    # Act
    metadata = get_github_metadata("https://github.com/user/repo")

    # Assert
    assert metadata is None
    mock_log.error.assert_called_once()
    assert "Error fetching GitHub API" in mock_log.error.call_args[0][0]