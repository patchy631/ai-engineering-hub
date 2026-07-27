"""
Seed a Zep knowledge graph with conversation data designed to trigger Observation generation.

Three conversations simulate a user (Maya) purchasing ergonomic products across two environments 
(home office and commute) over four weeks, all driven by the same underlying condition of back pain.

The conversations are structured so that:
  - Conv 1 and Conv 2 share the entity pair (Maya, Back Pain)
  - Conv 2 and Conv 3 share the entity pair (Maya, Lumbar Support)
  - Conv 1 and Conv 3 share nothing directly

Requirements:
  - pip install zep-cloud
  - ZEP_API_KEY environment variable set

Usage:
  export ZEP_API_KEY="your-api-key"
  python seed.py
"""

import os
import sys
import time
from zep_cloud.client import Zep
from zep_cloud.types import Message

API_KEY = os.environ.get("ZEP_API_KEY")
if not API_KEY:
    print("Error: ZEP_API_KEY environment variable is not set.")
    print("Run: export ZEP_API_KEY='your-api-key'")
    sys.exit(1)

client = Zep(api_key=API_KEY)

USER_ID = "maya-obs-demo"
USER_NAME = "Maya Chen"
AGENT_NAME = "Support Agent"


def add_conversation(thread_id: str, messages: list[Message], label: str):
    """Create a thread and add messages to it."""
    print(f"  [{label}] Creating thread and adding {len(messages)} messages...")
    client.thread.create(thread_id=thread_id, user_id=USER_ID)
    client.thread.add_messages(thread_id, messages=messages)
    print(f"  [{label}] Done.")
    time.sleep(2)


def main():
    # ── Create user ──────────────────────────────────────────────────────
    print("Creating user...")
    try:
        client.user.add(
            user_id=USER_ID,
            first_name="Maya",
            last_name="Chen",
            email="maya.chen@example.com",
        )
        print(f"User '{USER_ID}' created.\n")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"User '{USER_ID}' already exists, continuing.\n")
        else:
            raise

    print("Seeding conversations...\n")

    # ── Conversation 1: Standing desk ────────────────────────────────────
    # Signatures: (Maya, Standing Desk), (Maya, Back Pain), (Maya, Home Office)
    add_conversation(
        thread_id=f"{USER_ID}-conv1-standing-desk",
        label="Conv 1: Standing Desk",
        messages=[
            Message(
                created_at="2026-04-10T10:00:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "Hi, I'm looking for a standing desk for my home office. "
                    "I've been getting pretty bad back pain from sitting all day "
                    "and my doctor suggested I try alternating between sitting "
                    "and standing."
                ),
            ),
            Message(
                created_at="2026-04-10T10:02:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "I can help with that. For home office use, I'd recommend "
                    "the ErgoRise Pro. It's an electric sit-stand desk with "
                    "programmable height presets. Very popular with people "
                    "dealing with back pain from long desk sessions. It's $549 "
                    "with free shipping."
                ),
            ),
            Message(
                created_at="2026-04-10T10:04:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "That sounds good. I've been working from my home office "
                    "full time for two years now and the back pain has been "
                    "getting worse over the past few months. I need to do "
                    "something about it. Let's go with the ErgoRise Pro."
                ),
            ),
            Message(
                created_at="2026-04-10T10:06:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "Great choice. Order placed for the ErgoRise Pro standing "
                    "desk. Estimated delivery to your home office is April 15th. "
                    "A standing desk is a solid first step for addressing back "
                    "pain from prolonged sitting."
                ),
            ),
        ],
    )

    # ── Conversation 2: Ergonomic chair ───────────────
    # Signatures: (Maya, Ergonomic Chair), (Maya, Back Pain), (Maya, Lumbar Support)
    add_conversation(
        thread_id=f"{USER_ID}-conv2-ergonomic-chair",
        label="Conv 2: Ergonomic Chair",
        messages=[
            Message(
                created_at="2026-04-25T14:00:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "I bought a standing desk from you a couple weeks ago and "
                    "it's helped, but my back pain hasn't gone away completely. "
                    "I think I also need a proper ergonomic chair for the hours "
                    "when I'm sitting. Something with really good lumbar support."
                ),
            ),
            Message(
                created_at="2026-04-25T14:02:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "That makes sense. A standing desk helps but most people "
                    "still sit for a significant portion of the day. For "
                    "dedicated lumbar support, I'd recommend the PostureFlex "
                    "Ergo. It has an adjustable lumbar mechanism that adapts "
                    "to your spine. It's one of our best chairs for chronic "
                    "back pain. $429."
                ),
            ),
            Message(
                created_at="2026-04-25T14:04:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "The adjustable lumbar support sounds exactly like what I "
                    "need. I'll take it. The back pain has been affecting me "
                    "everywhere honestly, not just at my desk. I've been "
                    "noticing it during my commute too. Do you have anything "
                    "for lumbar support in a car? I have a 45-minute drive "
                    "each way."
                ),
            ),
            Message(
                created_at="2026-04-25T14:06:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "Yes, we carry several car lumbar support options. I'd "
                    "suggest looking at our car seat cushions with built-in "
                    "lumbar support once your chair arrives and you've had a "
                    "chance to see how the lumbar adjustment works for you. "
                    "I'll place the ergonomic chair order now. Delivery "
                    "estimate is April 30th."
                ),
            ),
            Message(
                created_at="2026-04-25T14:08:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "That's a good idea, I'll sort out the home office setup "
                    "first and then tackle the commute. Thanks for the help."
                ),
            ),
        ],
    )

    # ── Conversation 3: Car seat cushion ─────────────────────────────────
    # Signatures: (Maya, Car Seat Cushion), (Maya, Lumbar Support), (Maya, Commute)
    add_conversation(
        thread_id=f"{USER_ID}-conv3-car-cushion",
        label="Conv 3: Car Seat Cushion",
        messages=[
            Message(
                created_at="2026-05-08T11:00:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "Hi, I'm back. You helped me with a standing desk and an "
                    "ergonomic chair over the past month. Both have been great "
                    "for my home office. Now I need to address my commute. "
                    "I'm looking for a car seat cushion with lumbar support. "
                    "My drive is about 45 minutes each way and the car seat "
                    "has zero support."
                ),
            ),
            Message(
                created_at="2026-05-08T11:02:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "Welcome back. For your commute, I'd recommend the "
                    "DriveComfort Pro seat cushion. It has memory foam with "
                    "a built-in lumbar support ridge that works well for "
                    "longer drives. It straps onto most car seats securely. $89."
                ),
            ),
            Message(
                created_at="2026-05-08T11:04:00Z",
                name=USER_NAME,
                role="user",
                content=(
                    "That's exactly what I need. The lumbar support on my "
                    "office chair made such a difference that I want the same "
                    "for the car. Between the standing desk, the chair, and now "
                    "this cushion, I'm basically rebuilding my entire setup "
                    "around this back pain issue. Let's do it."
                ),
            ),
            Message(
                created_at="2026-05-08T11:06:00Z",
                name=AGENT_NAME,
                role="assistant",
                content=(
                    "Order placed for the DriveComfort Pro car seat cushion "
                    "with lumbar support. Delivery estimate is May 12th. "
                    "Between your standing desk, ergonomic chair, and now "
                    "the car cushion, you've got a solid ergonomic setup "
                    "across both your home office and your commute."
                ),
            ),
        ],
    )

    print()
    print("=" * 60)
    print("All 3 conversations ingested successfully.")
    print("=" * 60)
    print()
    print("Zep needs time to process the graph and generate observations.")
    print("Wait 30-60 minutes, then run:")
    print()
    print("  python check.py")
    print()


if __name__ == "__main__":
    main()