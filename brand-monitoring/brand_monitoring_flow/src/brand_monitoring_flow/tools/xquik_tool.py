from collections.abc import Callable, Mapping
from typing import Any

from x_twitter_scraper import XTwitterScraper


def _read(value: object, name: str, default: object = None) -> object:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)


def _count(tweet: object, name: str) -> int:
    value = _read(tweet, name, 0)
    return value if isinstance(value, int) else 0


def _entity_values(
    entities: object, keys: tuple[str, ...], fields: tuple[str, ...]
) -> list[str]:
    if not isinstance(entities, Mapping):
        return []

    entries: object = []
    for key in keys:
        candidate = entities.get(key)
        if isinstance(candidate, list):
            entries = candidate
            break

    values: list[str] = []
    for entry in entries if isinstance(entries, list) else []:
        for field in fields:
            candidate = _read(entry, field)
            if isinstance(candidate, str) and candidate and candidate not in values:
                values.append(candidate)
                break
    return values


def _tweet_to_mention(tweet: object) -> dict[str, object]:
    tweet_id_value = _read(tweet, "id", "")
    tweet_id = str(tweet_id_value) if tweet_id_value is not None else ""
    author = _read(tweet, "author")
    username = str(_read(author, "username", "") or _read(author, "id", ""))
    url = _read(tweet, "url")
    if not isinstance(url, str) or not url:
        url = (
            f"https://x.com/{username}/status/{tweet_id}"
            if username
            else f"https://x.com/i/web/status/{tweet_id}"
        )

    entities = _read(tweet, "entities")
    text = _read(tweet, "text", "")
    return {
        "url": url,
        "views": _count(tweet, "view_count"),
        "likes": _count(tweet, "like_count"),
        "replies": _count(tweet, "reply_count"),
        "reposts": _count(tweet, "retweet_count"),
        "hashtags": _entity_values(entities, ("hashtags",), ("text", "tag")),
        "quotes": _count(tweet, "quote_count"),
        "bookmarks": _count(tweet, "bookmark_count"),
        "description": text if isinstance(text, str) else "",
        "tagged_users": _entity_values(
            entities,
            ("user_mentions", "userMentions", "mentions"),
            ("screen_name", "screenName", "username", "name"),
        ),
        "original_poster": username,
    }


def search_x_mentions(
    brand_name: str,
    limit: int,
    client_factory: Callable[..., Any] = XTwitterScraper,
) -> list[dict[str, object]]:
    query = brand_name.strip()
    if not query:
        raise ValueError("Brand name must not be empty.")
    if limit < 1 or limit > 50:
        raise ValueError("X result limit must be between 1 and 50.")

    client = client_factory(timeout=30.0)
    try:
        response = client.x.tweets.search(
            q=query,
            exact_phrase=query,
            limit=limit,
            query_type="Latest",
        )
        return [
            _tweet_to_mention(tweet) for tweet in response.tweets if _read(tweet, "id")
        ]
    finally:
        client.close()
