"""
main.py — Entry point.

Run:
  cd src
  python main.py
"""

import sys
import os

# Load .env from the project root
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from pipeline import build_pipeline, PipelineState


def main():
    print("=" * 55)
    print("  Marketing Agent POC")
    print("  Pixel Data → Segmentation → WhatsApp CTAs")
    print("=" * 55)

    pipeline = build_pipeline()

    # Initial state — empty, Data Agent will populate it
    initial_state: PipelineState = {
        "raw_events": [],
        "segments":   [],
        "messages":   [],
    }

    result = pipeline.invoke(initial_state)

    # --------------------------------------------------------
    # Print the output
    # --------------------------------------------------------
    print("\n" + "=" * 55)
    print("  GENERATED WHATSAPP MESSAGES")
    print("=" * 55)

    for msg in result["messages"]:
        segment_icon = {
            "HIGH_INTENT":   "🔥",
            "MEDIUM_INTENT": "🌡️",
            "LOW_INTENT":    "❄️",
        }.get(msg["segment"], "•")

        print(f"\n{segment_icon}  {msg['name']}  ({msg['phone']})")
        print(f"   Segment : {msg['segment']}")
        print(f"   Message : {msg['message']}")

    print("\n✅ Pipeline complete.\n")


if __name__ == "__main__":
    main()
