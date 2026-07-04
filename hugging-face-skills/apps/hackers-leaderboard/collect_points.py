#!/usr/bin/env python3
"""
Collect engagement points from the hf-skills organization.

Tracks user activity across all repos (models, datasets, spaces) and counts:
- 1 point per discussion opened
- 1 point per comment made
- 1 point per PR opened
- 1 point per repo owned/created

Results are saved to a dataset for the hackers leaderboard.

Usage:
    HF_TOKEN=$HF_TOKEN python collect_points.py [--push-to-hub]
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import requests

API_BASE = "https://huggingface.co/api"
ORG_NAME = "hf-skills"
USER_AGENT = "hf-skills-leaderboard/1.0"
DISCUSSION_LIMIT = 100  # Max discussions to fetch per repo
TRENDING_LIMIT = 50  # Number of trending repos to scan for external PRs


@dataclass
class UserStats:
    """Tracks engagement stats for a single user."""

    username: str
    is_org_member: bool = True
    discussions_opened: int = 0
    comments_made: int = 0
    prs_opened: int = 0
    repos_owned: int = 0
    activities: list[dict[str, Any]] = field(default_factory=list)

    @property
    def total_points(self) -> int:
        return self.discussions_opened + self.comments_made + self.prs_opened + self.repos_owned

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "is_org_member": self.is_org_member,
            "total_points": self.total_points,
            "discussions_opened": self.discussions_opened,
            "comments_made": self.comments_made,
            "prs_opened": self.prs_opened,
            "repos_owned": self.repos_owned,
        }


class PointsCollector:
    """Collects engagement points from the hf-skills organization."""

    def __init__(self, token: str | None = None) -> None:
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.user_stats: dict[str, UserStats] = {}
        self.logs: list[str] = []

    def log(self, message: str) -> None:
        """Add a log message."""
        print(message)
        self.logs.append(message)

    def _fetch_org_members(self) -> list[str]:
        """Fetch all members of the organization."""
        try:
            from huggingface_hub import HfApi

            api = HfApi(token=self.token)
            members = list(api.list_organization_members(ORG_NAME))
            usernames = [m.username for m in members if m.username]
            self.log(f"👥 Found {len(usernames)} organization members")
            return usernames
        except Exception as e:
            self.log(f"⚠️ Failed to fetch org members: {e}")
            # Fallback: try the API directly
            try:
                url = f"{API_BASE}/organizations/{ORG_NAME}/members"
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                members = response.json()
                usernames = [m.get("user") or m.get("username") or m.get("name") for m in members]
                usernames = [u for u in usernames if u]
                self.log(f"👥 Found {len(usernames)} organization members (via API)")
                return usernames
            except Exception as e2:
                self.log(f"⚠️ Fallback also failed: {e2}")
                return []

    def collect_all(self) -> dict[str, UserStats]:
        """Collect points from all repos in the organization."""
        self.log(f"🔍 Scanning organization: {ORG_NAME}")

        # First, get all org members and initialize their stats
        members = self._fetch_org_members()
        for username in members:
            self.user_stats[username] = UserStats(username=username)

        # Collect from all repo types
        models = self._list_repos("models")
        datasets = self._list_repos("datasets")
        spaces = self._list_repos("spaces")

        all_repos = [
            *[(r, "model") for r in models],
            *[(r, "dataset") for r in datasets],
            *[(r, "space") for r in spaces],
        ]

        self.log(f"📦 Found {len(models)} models, {len(datasets)} datasets, {len(spaces)} spaces")

        for repo_info, repo_type in all_repos:
            repo_id = repo_info.get("id") or repo_info.get("modelId")
            if not repo_id:
                continue

            # Credit repo owner
            owner = repo_info.get("author") or repo_id.split("/")[0]
            if owner and owner != ORG_NAME:
                self._add_point(owner, "repos_owned", repo_id, "repo_created")

            # Scan discussions
            self._scan_discussions(repo_id, repo_type)

        return dict(self.user_stats)

    def scan_external_repos(self, repo_types: list[str] | None = None) -> None:
        """Scan trending repos across the Hub for PRs by org members.

        Args:
            repo_types: List of repo types to scan. Options: "models", "datasets", "spaces".
                       If None, scans all types.
        """
        org_members = set(self.user_stats.keys())
        if not org_members:
            self.log("⚠️ No org members loaded. Run collect_all() first.")
            return

        if repo_types is None:
            repo_types = ["models", "datasets", "spaces"]

        self.log(f"🌐 Scanning trending repos for PRs by {len(org_members)} org members...")
        self.log(f"📂 Repo types: {', '.join(repo_types)}")

        for repo_type in repo_types:
            trending = self._fetch_trending(repo_type)
            self.log(f"📈 Scanning {len(trending)} trending {repo_type}...")

            for repo_info in trending:
                repo_id = repo_info.get("id") or repo_info.get("modelId")
                if not repo_id:
                    continue

                # Skip org repos (already scanned)
                if repo_id.startswith(f"{ORG_NAME}/"):
                    continue

                # Scan for PRs/discussions by each org member using author filter
                self._scan_repo_for_members(repo_id, repo_type, org_members)

    def _fetch_trending(self, repo_type: str) -> list[dict[str, Any]]:
        """Fetch trending repos of a given type."""
        endpoint = f"{API_BASE}/{repo_type}"
        params = {"sort": "trendingScore", "limit": TRENDING_LIMIT}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log(f"⚠️ Failed to fetch trending {repo_type}: {e}")
            return []

    def _scan_repo_for_members(self, repo_id: str, repo_type: str, org_members: set[str]) -> None:
        """Scan a repo's discussions for activity by org members using author filter."""
        # Parse namespace and repo from repo_id
        parts = repo_id.split("/")
        if len(parts) != 2:
            return
        namespace, repo = parts

        for member in org_members:
            # Use author filter for efficient querying
            self._fetch_member_discussions(
                repo_type=repo_type,
                namespace=namespace,
                repo=repo,
                author=member,
                discussion_type="pull_request",
            )
            self._fetch_member_discussions(
                repo_type=repo_type,
                namespace=namespace,
                repo=repo,
                author=member,
                discussion_type="discussion",
            )

    def _fetch_member_discussions(
        self,
        repo_type: str,
        namespace: str,
        repo: str,
        author: str,
        discussion_type: str = "all",
    ) -> None:
        """Fetch discussions for a specific author on a repo.

        Uses: GET /api/{repoType}/{namespace}/{repo}/discussions?author={author}&type={type}
        """
        url = f"{API_BASE}/{repo_type}/{namespace}/{repo}/discussions"
        params = {
            "author": author,
            "type": discussion_type,
            "status": "all",
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return

        discussions = data.get("discussions", [])
        repo_id = f"{namespace}/{repo}"

        for discussion in discussions:
            is_pr = discussion.get("isPullRequest", False)
            disc_num = discussion.get("num")

            if is_pr:
                self._add_point(author, "prs_opened", repo_id, "external_pr", disc_num)
                self.log(f"🔀 Found PR by {author} on {repo_id}")
            else:
                self._add_point(author, "discussions_opened", repo_id, "external_discussion", disc_num)
                self.log(f"💬 Found discussion by {author} on {repo_id}")

            # Count comments on the discussion
            num_comments = discussion.get("numComments", 0)
            if num_comments > 0:
                self._fetch_discussion_comments(repo_type, namespace, repo, disc_num, author)

    def _fetch_discussion_comments(
        self,
        repo_type: str,
        namespace: str,
        repo: str,
        disc_num: int,
        target_author: str,
    ) -> None:
        """Fetch comments on a discussion and count those by target author."""
        url = f"{API_BASE}/{repo_type}/{namespace}/{repo}/discussions/{disc_num}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            return

        repo_id = f"{namespace}/{repo}"
        events = data.get("events", [])
        for event in events:
            if event.get("type") == "comment":
                author_info = event.get("author", {}) or {}
                author = author_info.get("name") or author_info.get("fullname")
                if author == target_author:
                    self._add_point(author, "comments_made", repo_id, "external_comment", disc_num)

    def _list_repos(self, repo_type: str) -> list[dict[str, Any]]:
        """List all repos of a given type in the organization."""
        endpoint = f"{API_BASE}/{repo_type}"
        params = {"author": ORG_NAME, "limit": 1000}

        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.log(f"⚠️ Failed to list {repo_type}: {e}")
            return []

    def _scan_discussions(self, repo_id: str, repo_type: str) -> None:
        """Scan all discussions for a repo and count engagement."""
        # Map repo type to API path
        type_map = {"model": "models", "dataset": "datasets", "space": "spaces"}
        api_type = type_map.get(repo_type, "models")

        url = f"{API_BASE}/{api_type}/{repo_id}/discussions"

        try:
            response = self.session.get(url, params={"limit": DISCUSSION_LIMIT}, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            self.log(f"⚠️ Failed to get discussions for {repo_id}: {e}")
            return

        discussions = data.get("discussions", [])
        if not discussions:
            return

        self.log(f"💬 {repo_id}: found {len(discussions)} discussions")

        for discussion in discussions:
            self._process_discussion(repo_id, api_type, discussion)

    def _process_discussion(self, repo_id: str, api_type: str, discussion: dict[str, Any]) -> None:
        """Process a single discussion and its comments."""
        author_info = discussion.get("author", {}) or {}
        author = author_info.get("name") or author_info.get("fullname")
        is_pr = discussion.get("isPullRequest", False)
        disc_num = discussion.get("num")

        if author and author != ORG_NAME:
            activity_type = "pr_opened" if is_pr else "discussion_opened"
            point_type = "prs_opened" if is_pr else "discussions_opened"
            self._add_point(author, point_type, repo_id, activity_type, disc_num)

        # Fetch discussion details to get comments
        if disc_num:
            self._fetch_comments(repo_id, api_type, disc_num)

    def _fetch_comments(self, repo_id: str, api_type: str, disc_num: int) -> None:
        """Fetch and count comments on a discussion."""
        url = f"{API_BASE}/{api_type}/{repo_id}/discussions/{disc_num}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            # Silently skip failed comment fetches
            return

        events = data.get("events", [])
        for event in events:
            event_type = event.get("type")
            # Count comments (not the initial post, status changes, etc.)
            if event_type == "comment":
                author_info = event.get("author", {}) or {}
                author = author_info.get("name") or author_info.get("fullname")
                if author and author != ORG_NAME:
                    self._add_point(author, "comments_made", repo_id, "comment", disc_num)

    def _add_point(
        self,
        username: str,
        point_type: str,
        repo_id: str,
        activity_type: str,
        disc_num: int | None = None,
    ) -> None:
        """Add a point to a user's stats."""
        if not username:
            return

        # Initialize stats for users not in the org (external contributors)
        if username not in self.user_stats:
            self.user_stats[username] = UserStats(username=username, is_org_member=False)

        stats = self.user_stats[username]
        current = getattr(stats, point_type, 0)
        setattr(stats, point_type, current + 1)

        stats.activities.append(
            {
                "type": activity_type,
                "repo_id": repo_id,
                "discussion_num": disc_num,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_leaderboard(self) -> list[dict[str, Any]]:
        """Get the leaderboard sorted by total points."""
        leaderboard = [stats.to_dict() for stats in self.user_stats.values()]
        leaderboard.sort(key=lambda x: x["total_points"], reverse=True)
        return leaderboard

    def save_json(self, filepath: str) -> None:
        """Save the leaderboard to a JSON file."""
        leaderboard = self.get_leaderboard()
        output = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "organization": ORG_NAME,
            "total_participants": len(leaderboard),
            "leaderboard": leaderboard,
        }
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2)
        self.log(f"💾 Saved leaderboard to {filepath}")

    def push_to_hub(self, repo_id: str = "hf-skills/hackers-leaderboard") -> None:
        """Push the leaderboard data to a HF dataset."""
        try:
            from huggingface_hub import HfApi
        except ImportError:
            self.log("❌ huggingface_hub not installed. Run: pip install huggingface_hub")
            return

        api = HfApi()
        leaderboard = self.get_leaderboard()

        # Create dataset as JSONL
        jsonl_content = "\n".join(json.dumps(row) for row in leaderboard)

        # Also create a metadata file
        metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "organization": ORG_NAME,
            "total_participants": len(leaderboard),
            "total_points": sum(row["total_points"] for row in leaderboard),
        }

        try:
            # Create repo if it doesn't exist
            api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
            self.log(f"📁 Ensured dataset repo exists: {repo_id}")

            # Upload leaderboard data
            api.upload_file(
                path_or_fileobj=jsonl_content.encode(),
                path_in_repo="data/leaderboard.jsonl",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Update leaderboard - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            )

            # Upload metadata
            api.upload_file(
                path_or_fileobj=json.dumps(metadata, indent=2).encode(),
                path_in_repo="data/metadata.json",
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"Update metadata - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            )

            self.log(f"🚀 Pushed leaderboard to {repo_id}")
        except Exception as e:
            self.log(f"❌ Failed to push to hub: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect engagement points from hf-skills organization")
    parser.add_argument(
        "--push-to-hub",
        action="store_true",
        help="Push results to HF dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="leaderboard.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        default="hf-skills/hackers-leaderboard",
        help="HF dataset repo ID for pushing",
    )
    parser.add_argument(
        "--scan-external",
        action="store_true",
        help="Also scan trending repos for PRs/discussions by org members",
    )
    parser.add_argument(
        "--repo-type",
        type=str,
        nargs="+",
        choices=["models", "datasets", "spaces"],
        default=None,
        help="Repo types to scan (for --scan-external). Default: all types",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("⚠️ No HF_TOKEN found. Some requests may be rate-limited.")

    collector = PointsCollector(token=token)
    collector.collect_all()

    # Optionally scan external repos for member activity
    if args.scan_external:
        collector.scan_external_repos(repo_types=args.repo_type)

    # Print leaderboard
    print("\n" + "=" * 50)
    print("🏆 HACKERS LEADERBOARD")
    print("=" * 50)

    leaderboard = collector.get_leaderboard()
    for i, entry in enumerate(leaderboard[:20], 1):
        print(
            f"{i:2}. {entry['username']:20} - {entry['total_points']:4} points "
            f"(💬{entry['discussions_opened']} 📝{entry['comments_made']} "
            f"🔀{entry['prs_opened']} 📦{entry['repos_owned']})"
        )

    if len(leaderboard) > 20:
        print(f"   ... and {len(leaderboard) - 20} more participants")

    print("=" * 50)
    print(f"Total participants: {len(leaderboard)}")
    print(f"Total points awarded: {sum(e['total_points'] for e in leaderboard)}")

    # Save locally
    collector.save_json(args.output)

    # Push to hub if requested
    if args.push_to_hub:
        collector.push_to_hub(args.repo_id)


if __name__ == "__main__":
    main()
