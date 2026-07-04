"""Ingest chunked data into Zep knowledge graph."""
import sys
import os
import json
import time
from pathlib import Path
from zep_cloud import Zep
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ZEP_API_KEY = os.getenv("ZEP_API_KEY")
if not ZEP_API_KEY:
    raise ValueError("ZEP_API_KEY environment variable is required")

USER_ID = os.getenv("ZEP_DOCS_USER_ID")


def main():
    """Main function to ingest data to user graph."""
    print("Initializing Zep client...")
    zep = Zep(api_key=ZEP_API_KEY)

    # Create or verify user exists
    print(f"Setting up user: \"{USER_ID}\"...")
    try:
        zep.user.add(
            user_id=USER_ID,
            email="docs@system.local",
            first_name="Zep",
            last_name="KG"
        )
        print(f"User \"{USER_ID}\" created successfully")
    except Exception as e:
        if "already exists" in str(e).lower() or "409" in str(e):
            print(f"User \"{USER_ID}\" already exists")
        else:
            print(f"Warning: Error creating user: {e}")
            print("Continuing with ingestion...")

    # Load chunked docs
    print("Loading chunked docs...")
    chunks_path = Path(__file__).parent.parent / "data" / "chunked-docs.json"

    if not chunks_path.exists():
        print(f"Error: {chunks_path} not found!")
        print("Please create chunked docs first.")
        return

    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks")

    episode_uuids = []

    for i, chunk in enumerate(chunks):
        print(f"Ingesting chunk {i + 1}/{len(chunks)}: \"{chunk['heading']}\"")

        MAX_CONTENT_LENGTH = 10000
        header = f"{chunk['context']}\n\n# {chunk['heading']}\n\n"
        available_space = MAX_CONTENT_LENGTH - len(header)

        content = chunk["content"]
        if len(content) > available_space:
            print(
                f"  Warning: Chunk content exceeds available space ({len(content)} chars), truncating to {available_space} chars...")
            content = content[:available_space - 20] + "\n\n[truncated...]"

        episode_content = header + content

        try:
            episode = zep.graph.add(
                user_id=USER_ID,
                type="text",
                data=episode_content,
            )

            episode_uuids.append(episode.uuid_)
            print(
                f"  Created episode: {episode.uuid_} ({len(episode_content)} chars)")
        except Exception as e:
            print(f"  Error ingesting chunk: {e}")

        # Rate limiting
        time.sleep(0.5)

    # Save episode mapping
    mapping_path = Path(__file__).parent.parent / \
        "data" / "episode-mapping.json"
    mapping_data = {
        "user_id": USER_ID,
        "total_episodes": len(episode_uuids),
        "episode_ids": episode_uuids,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping_data, f, indent=2)

    print(
        f"\nDone! Ingested {len(episode_uuids)} episodes to user graph \"{USER_ID}\"")
    print(f"Episode mapping saved to {mapping_path}")


if __name__ == "__main__":
    main()
