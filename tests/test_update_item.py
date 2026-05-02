import responses

from awesome_list import awesome_items


@responses.activate
def test_update_item_success():
    # Arrange
    item = {
        "link_id": "https://news.sap.com",
        "name": "",
        "description": ""
    }
    
    mock_html = """
    <html>
        <head>
            <meta property="og:title" content="SAP News Center">
            <meta property="og:description" content="News & press releases from SAP">
        </head>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://news.sap.com",
        body=mock_html,
        status=200,
        content_type="text/html"
    )

    # Act
    awesome_items.update_item(item)

    # Assert
    assert item["name"] == "SAP News Center"
    assert item["description"].startswith("News & press releases from SAP")
    assert item["update_at"] == ""
    assert item["published_at"] == ""


@responses.activate
def test_update_item_non_valid_url():
    item = {
        "link_id": "https://kemikal.io/notfound",
        "name": "Kemikal IO - Not Found",
        "description": ""
    }
    
    responses.add(
        responses.GET,
        "https://kemikal.io/notfound",
        status=404
    )

    awesome_items.update_item(item)

    assert item["name"] == "Kemikal IO - Not Found"


@responses.activate
def test_update_item_server_error():
    item = {
        "link_id": "https://kemikal.io/error",
        "name": "Server Error",
        "description": ""
    }
    
    responses.add(
        responses.GET,
        "https://kemikal.io/error",
        status=500
    )

    awesome_items.update_item(item)

    assert item["name"] == "Server Error"


@responses.activate
def test_update_item_preserves_existing_data():
    # Arrange
    item = {
        "link_id": "https://example.com",
        "name": "Custom User Name",
        "description": "Custom User Description"
    }
    
    mock_html = """
    <html>
        <head>
            <meta property="og:title" content="Fetched Title">
            <meta property="og:description" content="Fetched description">
        </head>
    </html>
    """
    
    responses.add(
        responses.GET,
        "https://example.com",
        body=mock_html,
        status=200,
        content_type="text/html"
    )

    # Act
    awesome_items.update_item(item)

    # Assert - We assume the implementation prioritizes manually entered YAML data over fetched metadata
    assert item["name"] == "Custom User Name"
    assert item["description"] == "Custom User Description"
