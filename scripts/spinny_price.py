"""
Spinny Car Price Tracker.
Fetches car prices from Spinny API and returns formatted message.
"""

import requests
from datetime import datetime


# Cars to track - add more IDs here
CARS = [
    {"id": "25264538", "label": "VW Tiguan"},      # 2018 Volkswagen Tiguan Highline TDI
    {"id": "24138859", "label": "Skoda Superb"},   # 2021 Skoda Superb L&K AT
]

API_BASE = "https://api.spinny.com/v3/api/pdp/price-breakdown/{}/v2/"

# Headers to mimic browser request
HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://www.spinny.com",
    "platform": "web",
    "referer": "https://www.spinny.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


def get_status(data: dict) -> tuple[str, str]:
    """Get availability status emoji and text."""
    if data.get("sold"):
        return "🔴", "SOLD"
    elif data.get("booked"):
        return "🟡", "BOOKED"
    elif data.get("on_hold"):
        return "🟠", "ON HOLD"
    elif data.get("soft_unpublish") or data.get("listing_status") == "unpublished":
        return "🔵", "UNAVAILABLE"
    elif data.get("upcoming"):
        return "⚪", "UPCOMING"
    return "🟢", "AVAILABLE"


def fetch_car(car_id: str) -> dict | None:
    """Fetch car data from Spinny API."""
    try:
        url = API_BASE.format(car_id)
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        resp_data = response.json()
        
        if not resp_data.get("is_success"):
            return None
        
        return resp_data.get("data", {})
    except Exception as e:
        print(f"Failed to fetch car {car_id}: {e}")
        return None


def format_car_summary(data: dict, car_id: str) -> str:
    """Format a concise summary for one car."""
    # Car details
    make = data.get("make", "")
    model = data.get("model", "")
    variant_data = data.get("variant", {})
    variant = variant_data.get("display_name", "") if isinstance(variant_data, dict) else ""
    year = data.get("make_year", "")
    mileage = data.get("mileage", "N/A")
    fuel = data.get("fuel_type", "").capitalize()
    transmission = data.get("transmission", "").capitalize()
    
    # Status
    status_emoji, status_text = get_status(data)
    
    # Price
    pricing = data.get("pricing", {})
    price = pricing.get("listing_price", {}).get("price", "N/A")
    market_price = pricing.get("market_price", {}).get("price", "N/A")
    
    # Build car name
    car_name = f"{year} {make} {model}"
    if variant:
        car_name += f" {variant}"
    
    # Listing URL - use permanent_url from API, fallback to basic format
    permanent_url = data.get("permanent_url", "")
    if permanent_url:
        url = f"https://www.spinny.com{permanent_url}"
    else:
        url = f"https://www.spinny.com/buy-used-cars/-d{car_id}"
    
    # Compact format
    lines = [
        f"<b>{car_name}</b>",
        f"{fuel} | {transmission} | {mileage} km",
        f"{status_emoji} {status_text} | <b>₹{price}</b> (Market: ₹{market_price})",
        f"<a href='{url}'>View →</a>",
    ]
    
    return "\n".join(lines)


def run() -> str | None:
    """
    Fetch car prices from Spinny API and return formatted message.
    
    Returns:
        Formatted message string or None if all requests fail
    """
    car_summaries = []
    
    for car in CARS:
        car_id = car["id"]
        print(f"Fetching {car['label']} ({car_id})...")
        
        data = fetch_car(car_id)
        if data:
            summary = format_car_summary(data, car_id)
            car_summaries.append(summary)
        else:
            car_summaries.append(f"⚠️ Failed to fetch {car['label']}")
    
    if not car_summaries:
        return None
    
    # Build final message
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    
    lines = [
        "<b>🚗 Spinny Price Update</b>",
        "",
    ]
    
    # Add each car separated by a line
    lines.append(car_summaries[0])
    for summary in car_summaries[1:]:
        lines.append("")
        lines.append("─────────────")
        lines.append("")
        lines.append(summary)
    
    lines.append("")
    lines.append(f"<i>Updated: {now}</i>")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Test the script
    message = run()
    if message:
        print(message)
    else:
        print("Failed to get price data")
