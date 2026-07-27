"""
Check what Zep generated from the seeded conversations.

Prints observations, facts, and entities for the demo user.

Usage:
  export ZEP_API_KEY="your-api-key"
  python check.py
"""

import os
import sys
from zep_cloud.client import Zep

API_KEY = os.environ.get("ZEP_API_KEY")
if not API_KEY:
    print("Error: ZEP_API_KEY environment variable is not set.")
    print("Run: export ZEP_API_KEY='your-api-key'")
    sys.exit(1)

client = Zep(api_key=API_KEY)
USER_ID = "maya-obs-demo"


def main():
    # ── Observations ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("OBSERVATIONS")
    print("=" * 60)

    observations = client.graph.observation.get_by_user_id(user_id=USER_ID)

    if observations:
        for obs in observations:
            print(f"\nName: {obs.name}")
            print(f"Summary: {obs.summary}")
    else:
        print("\nNo observations generated yet.")
        print("  - Observations require Flex Plus or Enterprise tier.")
        print("  - The graph needs 30+ minutes of idle time after ingestion.")
        print("  - Try running this script again in 30 minutes.")

    # ── Facts ────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FACTS (first 20)")
    print("=" * 60)

    edges = client.graph.edge.get_by_user_id(user_id=USER_ID, limit=20)

    if edges:
        for edge in edges:
            print(f"  [{edge.name}] {edge.fact}")
    else:
        print("\n  No facts found. Graph may still be processing.")

    # ── Entities ─────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("ENTITIES")
    print("=" * 60)

    nodes = client.graph.node.get_by_user_id(user_id=USER_ID)

    if nodes:
        for node in nodes:
            print(f"  {node.name}")
    else:
        print("\n  No entities found. Graph may still be processing.")

    print()


if __name__ == "__main__":
    main()