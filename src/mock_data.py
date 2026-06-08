"""
mock_data.py — Simulates pixel events from a landing page.

In a real system, these would come from a tracking pixel (like a Meta pixel
or a custom JS snippet on your page) stored in a DB or analytics platform.

Each event captures: who visited, what they did, how long they stayed.
"""

from datetime import datetime, timedelta


def get_pixel_events():
    """
    Returns a list of pixel events and a customer registry.

    Three customers with distinct behavior patterns:
    - Sofia:  high intent  → 3 visits, CTA click, deep scroll
    - Marcus: medium intent → 1 visit, moderate engagement
    - Elena:  low intent   → bounced in 8 seconds
    """

    now = datetime.now()

    events = [
        # --- Sofia (high intent) ---
        {
            "customer_id": "cust_001",
            "name": "Sofia Andersen",
            "phone": "+45 12 34 56 78",
            "event": "pageview",
            "timestamp": (now - timedelta(days=2)).isoformat(),
            "scroll_depth_pct": 55,
            "time_on_page_seconds": 95,
            "referrer": "google_ads",
        },
        {
            "customer_id": "cust_001",
            "name": "Sofia Andersen",
            "phone": "+45 12 34 56 78",
            "event": "pageview",
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "scroll_depth_pct": 80,
            "time_on_page_seconds": 210,
            "referrer": "direct",
        },
        {
            "customer_id": "cust_001",
            "name": "Sofia Andersen",
            "phone": "+45 12 34 56 78",
            "event": "cta_click",
            "button_label": "Start Free Trial",
            "timestamp": now.isoformat(),
            "scroll_depth_pct": 92,
            "time_on_page_seconds": 310,
            "referrer": "email_campaign",
        },

        # --- Marcus (medium intent) ---
        {
            "customer_id": "cust_002",
            "name": "Marcus Veil",
            "phone": "+45 87 65 43 21",
            "event": "pageview",
            "timestamp": (now - timedelta(hours=5)).isoformat(),
            "scroll_depth_pct": 48,
            "time_on_page_seconds": 75,
            "referrer": "instagram_organic",
        },
        {
            "customer_id": "cust_002",
            "name": "Marcus Veil",
            "phone": "+45 87 65 43 21",
            "event": "section_view",
            "section": "pricing",
            "timestamp": (now - timedelta(hours=5, minutes=-2)).isoformat(),
        },

        # --- Elena (low intent / bounce) ---
        {
            "customer_id": "cust_003",
            "name": "Elena Moro",
            "phone": "+45 11 22 33 44",
            "event": "pageview",
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "scroll_depth_pct": 12,
            "time_on_page_seconds": 8,
            "referrer": "tiktok_ad",
        },
    ]

    customers = {
        "cust_001": {"name": "Sofia Andersen", "phone": "+45 12 34 56 78"},
        "cust_002": {"name": "Marcus Veil",    "phone": "+45 87 65 43 21"},
        "cust_003": {"name": "Elena Moro",     "phone": "+45 11 22 33 44"},
    }

    return events, customers
