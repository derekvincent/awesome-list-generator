from unittest.mock import patch

import responses

from awesome_list.awesome_items import get_items_metadata


@responses.activate
def test_get_items_metadata_success():
    # Arrange
    url = "https://example.com"
    mock_html = """
    <html>
        <head>
            <meta name="description" content="A test description">
            <meta property="og:title" content="Test Title">
        </head>
    </html>
    """
    
    responses.add(
        responses.GET,
        url,
        body=mock_html,
        status=200,
        content_type="text/html"
    )
    
    item = {"link_id": url}
    
    # Act
    metadata = get_items_metadata(item)
    
    # Assert
    assert metadata is not None
    assert metadata.get("description") == "A test description"
    assert metadata.get("og:title") == "Test Title"

@patch("awesome_list.awesome_items.log")
def test_get_items_metadata_invalid_url(mock_log):
    item = {"link_id": "invalid-url"}
    metadata = get_items_metadata(item)
    assert metadata is None