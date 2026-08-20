import unittest
from types import SimpleNamespace

from brand_monitoring_flow.tools.xquik_tool import search_x_mentions
from x_twitter_scraper.types.shared.search_tweet import SearchTweet


class FakeTweets:
    def __init__(self, tweets: list[object], error: Exception | None = None) -> None:
        """Create a fake tweet resource."""
        self.tweets = tweets
        self.error = error
        self.search_kwargs: dict[str, object] = {}

    def search(self, **kwargs: object) -> object:
        """Record search arguments and return the configured response."""
        self.search_kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(tweets=self.tweets)


class FakeClient:
    def __init__(self, tweets: list[object], error: Exception | None = None) -> None:
        """Create a fake Xquik client."""
        self.x = SimpleNamespace(tweets=FakeTweets(tweets, error))
        self.closed = False

    def close(self) -> None:
        """Record client cleanup."""
        self.closed = True


class FakeClientFactory:
    def __init__(self, client: FakeClient) -> None:
        """Create a factory for one fake client."""
        self.client = client
        self.timeout: float | None = None

    def __call__(self, *, timeout: float) -> FakeClient:
        """Record the timeout and return the fake client."""
        self.timeout = timeout
        return self.client


class SearchXMentionsTests(unittest.TestCase):
    def test_maps_xquik_tweets_to_crew_input(self) -> None:
        """Map a typed SDK tweet into the X Crew schema."""
        tweet = SearchTweet.model_validate(
            {
                "id": "123",
                "url": "https://x.com/acme/status/123",
                "text": "Acme shipped a useful update",
                "author": {"id": "42", "name": "Acme", "username": "acme"},
                "viewCount": 900,
                "likeCount": 70,
                "replyCount": 8,
                "retweetCount": 9,
                "quoteCount": 3,
                "bookmarkCount": 4,
                "entities": {
                    "hashtags": [{"text": "launch"}, {"tag": "launch"}],
                    "user_mentions": [
                        {"screen_name": "teammate"},
                        {"username": "teammate"},
                    ],
                },
            },
        )
        client = FakeClient([tweet])
        factory = FakeClientFactory(client)

        mentions = search_x_mentions("  Acme  ", 12, factory)

        self.assertEqual(factory.timeout, 30.0)
        self.assertEqual(
            client.x.tweets.search_kwargs,
            {"q": "Acme", "exact_phrase": "Acme", "limit": 12, "query_type": "Latest"},
        )
        self.assertEqual(
            mentions,
            [
                {
                    "url": "https://x.com/acme/status/123",
                    "views": 900,
                    "likes": 70,
                    "replies": 8,
                    "reposts": 9,
                    "hashtags": ["launch"],
                    "quotes": 3,
                    "bookmarks": 4,
                    "description": "Acme shipped a useful update",
                    "tagged_users": ["teammate"],
                    "original_poster": "acme",
                }
            ],
        )
        self.assertTrue(client.closed)

    def test_sparse_tweet_uses_safe_defaults(self) -> None:
        """Preserve valid sparse results and skip missing IDs."""
        client = FakeClient(
            [
                {"id": "456", "text": "Acme mention", "author": {"id": "42"}},
                {"text": "missing id"},
            ]
        )

        mentions = search_x_mentions("Acme", 1, FakeClientFactory(client))

        self.assertEqual(len(mentions), 1)
        self.assertEqual(
            mentions[0],
            {
                "url": "https://x.com/i/web/status/456",
                "views": 0,
                "likes": 0,
                "replies": 0,
                "reposts": 0,
                "hashtags": [],
                "quotes": 0,
                "bookmarks": 0,
                "description": "Acme mention",
                "tagged_users": [],
                "original_poster": "42",
            },
        )

    def test_rejects_invalid_inputs_before_creating_client(self) -> None:
        """Reject invalid input before constructing a client."""
        for brand_name, limit in ((" ", 1), ("Acme", 0), ("Acme", 51)):
            with self.subTest(brand_name=brand_name, limit=limit):
                with self.assertRaises(ValueError):
                    search_x_mentions(
                        brand_name, limit, lambda **_: self.fail("client created")
                    )

    def test_closes_client_when_search_fails(self) -> None:
        """Close the client when the search raises an error."""
        client = FakeClient([], RuntimeError("search failed"))

        with self.assertRaisesRegex(RuntimeError, "search failed"):
            search_x_mentions("Acme", 5, FakeClientFactory(client))

        self.assertTrue(client.closed)


if __name__ == "__main__":
    unittest.main()
