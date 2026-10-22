import os
import unittest
from unittest.mock import patch

import requests
from crewai.tools import BaseTool
from pydantic import ValidationError

from src.agentic_rag.tools.custom_tool import FireCrawlWebSearchTool


class FireCrawlWebSearchToolTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"FIRECRAWL_API_KEY": "test-api-key"})
        self.env.start()
        self.addCleanup(self.env.stop)
        post = patch("src.agentic_rag.tools.custom_tool.requests.post")
        self.post = post.start()
        self.addCleanup(post.stop)
        self.tool = FireCrawlWebSearchTool()

    def test_query_schema_and_no_argument_constructor(self):
        self.assertIsInstance(self.tool, BaseTool)
        self.assertEqual(set(self.tool.args_schema.model_fields), {"query"})
        self.assertEqual(self.tool.args_schema(query="CrewAI").query, "CrewAI")
        with self.assertRaises(ValidationError):
            self.tool.args_schema()
        with self.assertRaises(ValidationError):
            self.tool.args_schema(query=123)
        self.post.assert_not_called()

    def test_search_through_crewai_returns_markdown(self):
        response = self.post.return_value
        response.json.return_value = {
            "success": True,
            "data": [{"markdown": "# First result"}, {"markdown": "Second result"}],
        }

        result = self.tool.to_structured_tool().invoke({"query": "CrewAI"})

        self.assertEqual(result, "# First result\n___\nSecond result")
        self.post.assert_called_once_with(
            "https://api.firecrawl.dev/v1/search",
            headers={
                "Authorization": "Bearer test-api-key",
                "Content-Type": "application/json",
            },
            json={
                "query": "CrewAI",
                "limit": 5,
                "lang": "en",
                "country": "us",
                "scrapeOptions": {"formats": ["markdown"]},
            },
            timeout=60,
        )
        response.raise_for_status.assert_called_once_with()

    def test_blank_query_is_rejected_without_request(self):
        for query in ("", "   ", "\t\n"):
            with self.subTest(query=query):
                with self.assertRaises(ValidationError):
                    self.tool.args_schema(query=query)
                with self.assertRaises(ValueError):
                    self.tool.to_structured_tool().invoke({"query": query})
        self.post.assert_not_called()

    def test_query_whitespace_is_stripped(self):
        self.post.return_value.json.return_value = {"success": True, "data": []}

        self.assertEqual(self.tool.args_schema(query="  CrewAI \t").query, "CrewAI")
        self.tool.to_structured_tool().invoke({"query": "  CrewAI \t"})

        self.assertEqual(self.post.call_args.kwargs["json"]["query"], "CrewAI")

    def test_empty_search_results(self):
        self.post.return_value.json.return_value = {"success": True, "data": []}

        self.assertEqual(self.tool._run("unknown topic"), "")

    def test_missing_search_data(self):
        self.post.return_value.json.return_value = {"success": True}

        self.assertEqual(self.tool._run("CrewAI"), "")

    def test_non_list_search_data(self):
        for data in (None, {}, {"markdown": "Result"}, "unexpected", 42, False):
            with self.subTest(data=data):
                self.post.return_value.json.return_value = {"success": True, "data": data}

                self.assertEqual(
                    self.tool._run("CrewAI"), "Failed to fetch web search results."
                )

    def test_non_object_search_result(self):
        for data in ([None], [1], ["unexpected"], [[]], [{"markdown": "Result"}, None]):
            with self.subTest(data=data):
                self.post.return_value.json.return_value = {"success": True, "data": data}

                self.assertEqual(
                    self.tool._run("CrewAI"), "Failed to fetch web search results."
                )

    def test_non_string_markdown(self):
        for markdown in (42, 0, 1.5, True, False, [], ["unexpected"], {}, {"text": "unexpected"}):
            with self.subTest(markdown=markdown):
                self.post.return_value.json.return_value = {
                    "success": True,
                    "data": [
                        {"markdown": "First result"},
                        {"markdown": markdown},
                        {"markdown": "Last result"},
                    ],
                }

                self.assertEqual(
                    self.tool._run("CrewAI"), "Failed to fetch web search results."
                )

    def test_result_without_markdown_is_skipped(self):
        self.post.return_value.json.return_value = {
            "success": True,
            "data": [
                {"url": "https://example.com"},
                {"markdown": None},
                {"markdown": ""},
                {"markdown": "Result"},
            ],
        }

        self.assertEqual(self.tool._run("CrewAI"), "Result")

    def test_missing_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "FIRECRAWL_API_KEY"):
                FireCrawlWebSearchTool()
        self.post.assert_not_called()

    def test_empty_api_key(self):
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": ""}):
            with self.assertRaisesRegex(ValueError, "FIRECRAWL_API_KEY"):
                FireCrawlWebSearchTool()
        self.post.assert_not_called()

    def test_api_key_is_not_serialized(self):
        self.assertNotIn("test-api-key", repr(self.tool))
        self.assertNotIn("test-api-key", str(self.tool.model_dump()))

    def test_api_failure(self):
        self.post.return_value.json.return_value = {"success": False, "error": "Failed"}

        self.assertEqual(self.tool._run("CrewAI"), "Failed to fetch web search results.")

    def test_non_object_response(self):
        for payload in (None, [], "unexpected", 42):
            with self.subTest(payload=payload):
                self.post.return_value.json.return_value = payload

                self.assertEqual(
                    self.tool._run("CrewAI"), "Failed to fetch web search results."
                )

    def test_http_failure(self):
        response = self.post.return_value
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("503")

        self.assertEqual(self.tool._run("CrewAI"), "Failed to fetch web search results: 503")
        response.json.assert_not_called()

    def test_request_timeout(self):
        self.post.side_effect = requests.exceptions.Timeout("Request timed out")

        self.assertEqual(
            self.tool._run("CrewAI"),
            "Failed to fetch web search results: Request timed out",
        )

    def test_invalid_json(self):
        self.post.return_value.json.side_effect = requests.exceptions.JSONDecodeError(
            "Invalid JSON", "not json", 0
        )

        self.assertIn("Failed to fetch web search results:", self.tool._run("CrewAI"))


if __name__ == "__main__":
    unittest.main()
