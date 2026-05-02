import unittest
from collections import OrderedDict
from unittest.mock import MagicMock, patch

import requests
import responses

from awesome_list.awesome_items import (
    _parse_podcast_rss,
    get_items_metadata,
    sort_categories_dict,
    update_item,
)


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


@responses.activate
def test_get_items_metadata_missing_tags():
    url = "https://example.com/no-tags"
    mock_html = "<html><head><title>No Meta Tags Here</title></head></html>"
    
    responses.add(
        responses.GET,
        url,
        body=mock_html,
        status=200,
        content_type="text/html"
    )
    
    item = {"link_id": url}
    metadata = get_items_metadata(item)
    
    assert metadata is not None
    assert metadata.get("description") is None
    assert metadata.get("og:title") is None

@patch("awesome_list.awesome_items.log")
def test_get_items_metadata_invalid_url(mock_log):
    item = {"link_id": "invalid-url"}
    metadata = get_items_metadata(item)
    assert metadata is None


class TestAwesomeItems(unittest.TestCase):

    # --- Tests for _parse_podcast_rss ---

    @patch('requests.get')
    def test_parse_podcast_rss_success(self, mock_get):
        """
        Test successful parsing of a valid RSS feed.
        """
        rss_content = """
        <rss>
          <channel>
            <item>
              <title>Latest Episode Title</title>
              <pubDate>Mon, 01 Jul 2024 10:00:00 +0000</pubDate>
            </item>
            <item>
              <title>Older Episode</title>
              <pubDate>Mon, 24 Jun 2024 10:00:00 +0000</pubDate>
            </item>
          </channel>
        </rss>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = rss_content.encode('utf-8')
        mock_get.return_value = mock_response

        result = _parse_podcast_rss("https://example.com/feed.xml")

        self.assertIsNotNone(result)
        self.assertEqual(result['media_type'], 'podcast')
        self.assertEqual(result['latest_episode_title'], 'Latest Episode Title')
        self.assertEqual(result['latest_episode_date'], '2024-07-01T10:00:00+00:00')

    @patch('requests.get')
    def test_parse_podcast_rss_http_error(self, mock_get):
        """
        Test handling of a non-200 HTTP status code.
        """
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = _parse_podcast_rss("https://example.com/feed.xml")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_parse_podcast_rss_request_exception(self, mock_get):
        """
        Test handling of a network request exception.
        """
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        result = _parse_podcast_rss("https://example.com/feed.xml")
        self.assertIsNone(result)

    @patch('requests.get')
    def test_parse_podcast_rss_no_items(self, mock_get):
        """
        Test RSS feed with no <item> tags.
        """
        rss_content = "<rss><channel></channel></rss>"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = rss_content.encode('utf-8')
        mock_get.return_value = mock_response

        result = _parse_podcast_rss("https://example.com/feed.xml")
        self.assertIsNone(result)

    # --- Tests for update_item ---

    @patch('awesome_list.awesome_items.get_items_metadata')
    def test_update_item_with_youtube_metadata(self, mock_get_metadata):
        """
        Test that a resource item is correctly updated with YouTube metadata.
        """
        mock_get_metadata.return_value = {
            "og:title": "My YouTube Video",
            "description": "A great video.",
            "og:image": "https://i.ytimg.com/vi/123/hqdefault.jpg",
            "media_type": "video.youtube",
            "article:published_time": "2024-07-01T12:00:00Z"
        }
        
        resource_item = {"link_id": "https://www.youtube.com/watch?v=123"}
        update_item(resource_item)

        self.assertEqual(resource_item.get("name"), "My YouTube Video")
        self.assertEqual(resource_item.get("thumbnail_url"), "https://i.ytimg.com/vi/123/hqdefault.jpg")
        self.assertEqual(resource_item.get("media_type"), "video.youtube")
        self.assertEqual(resource_item.get("published_at"), "2024-07-01T12:00:00Z")
        self.assertIsNone(resource_item.get("latest_episode_title")) # Ensure podcast fields are not set

    @patch('awesome_list.awesome_items.get_items_metadata')
    def test_update_item_with_podcast_metadata(self, mock_get_metadata):
        """
        Test that a resource item is correctly updated with Podcast metadata.
        """
        mock_get_metadata.return_value = {
            "og:title": "My Awesome Podcast",
            "og:image": "https://example.com/podcast.jpg",
            "media_type": "podcast",
            "latest_episode_title": "Episode 101",
            "latest_episode_date": "2024-07-07T10:00:00+00:00"
        }

        resource_item = {"link_id": "https://example.com/podcast"}
        update_item(resource_item)

        self.assertEqual(resource_item.get("name"), "My Awesome Podcast")
        self.assertEqual(resource_item.get("thumbnail_url"), "https://example.com/podcast.jpg")
        self.assertEqual(resource_item.get("media_type"), "podcast")
        self.assertEqual(resource_item.get("latest_episode_title"), "Episode 101")
        self.assertEqual(resource_item.get("latest_episode_date"), "2024-07-07T10:00:00+00:00")

    @patch('awesome_list.awesome_items.get_items_metadata')
    def test_update_item_with_no_media_metadata(self, mock_get_metadata):
        """
        Test that a standard item is not populated with media fields.
        """
        mock_get_metadata.return_value = {
            "og:title": "A Regular Blog Post",
            "description": "Just a normal article."
        }

        resource_item = {"link_id": "https://example.com/blog/post"}
        update_item(resource_item)

        self.assertEqual(resource_item.get("name"), "A Regular Blog Post")
        self.assertIsNone(resource_item.get("thumbnail_url"))
        self.assertIsNone(resource_item.get("media_type"))
        self.assertIsNone(resource_item.get("latest_episode_date"))

    # --- Tests for sort_categories_dict ---

    def _get_unsorted_categories(self):
        return OrderedDict([
            ("cat_c", {"label": "Charlie", "subcategories": OrderedDict([
                ("sub_z", {"label": "Zulu"}),
                ("sub_a", {"label": "Alpha"})
            ])}),
            ("cat_a", {"label": "Alpha"}),
            ("cat_b", {"name": "Bravo"}), # Missing label, should fallback to name
        ])

    def test_sort_categories_dict_asc(self):
        cats = self._get_unsorted_categories()
        sorted_cats = sort_categories_dict(cats, "asc")
        
        keys = list(sorted_cats.keys())
        self.assertEqual(keys, ["cat_a", "cat_b", "cat_c"])
        
        # Verify recursive subcategory sort
        sub_keys = list(sorted_cats["cat_c"]["subcategories"].keys())
        self.assertEqual(sub_keys, ["sub_a", "sub_z"])

    def test_sort_categories_dict_desc(self):
        cats = self._get_unsorted_categories()
        sorted_cats = sort_categories_dict(cats, "desc")
        
        keys = list(sorted_cats.keys())
        self.assertEqual(keys, ["cat_c", "cat_b", "cat_a"])
        
    def test_sort_categories_dict_set(self):
        # "set" should leave the order as initially parsed
        cats = self._get_unsorted_categories()
        sorted_cats = sort_categories_dict(cats, "set")
        
        keys = list(sorted_cats.keys())
        self.assertEqual(keys, ["cat_c", "cat_a", "cat_b"])