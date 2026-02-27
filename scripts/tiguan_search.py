"""
Spinny Tiguan Availability Tracker.
Searches for VW Tiguan / Tiguan Allspace across all Spinny cities.
"""

import requests
from datetime import datetime


MODELS = "tiguan,tiguan-allspace"

CITIES = [
    "delhi-ncr", "bangalore", "hyderabad", "mumbai", "pune",
    "delhi", "gurgaon", "noida", "ahmedabad", "chennai",
    "kolkata", "lucknow", "jaipur", "chandigarh",
    "agra", "ambala", "coimbatore", "faridabad", "ghaziabad",
    "kanpur", "karnal", "kochi", "mysuru", "sonipat", "visakhapatnam",
]

API_URL = "https://api.spinny.com/v3/api/listing/v6/"

HEADERS = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://www.spinny.com",
    "platform": "web",
    "referer": "https://www.spinny.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
}

PARAMS = {
    "model": MODELS,
    "page": 1,
    "show_max_on_assured": "true",
    "custom_budget_sort": "true",
    "prioritize_filter_listing": "true",
    "high_intent_required": "false",
    "active_banner": "true",
    "is_max_certified": 0,
    "is_pulse_exp": "false",
    "is_new_price": "false",
}


def get_status(car: dict) -> tuple[str, str]:
    """Get status emoji and text for a car."""
    if car.get("sold"):
        return "🔴", "SOLD"
    if car.get("booked"):
        return "🟡", "BOOKED"
    return "🟢", "AVAILABLE"


def format_price(price) -> str:
    """Format price in lakhs."""
    try:
        p = float(price)
        return f"₹{p / 100000:.1f}L"
    except (TypeError, ValueError):
        return "N/A"


def fetch_city(city: str) -> dict:
    """Fetch Tiguan listings for a city. Returns {count, cars}."""
    try:
        params = {**PARAMS, "city": city}
        r = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return {"count": data.get("count", 0), "results": data.get("results", [])}
    except Exception as e:
        print(f"Failed to fetch {city}: {e}")
        return {"count": -1, "results": []}


def run() -> str | None:
    """Search all cities for Tiguan and return formatted message."""
    car_details = []
    total_found = 0

    for city in CITIES:
        data = fetch_city(city)
        count = data["count"]

        if count <= 0:
            continue

        total_found += count
        city_name = city.replace("-", " ").title()

        for car in data["results"]:
            emoji, status = get_status(car)
            year = car.get("make_year", "")
            variant = car.get("variant", "")
            price = format_price(car.get("price"))
            mileage = car.get("mileage", "N/A")
            fuel = car.get("fuel_type", "").capitalize()
            perm_url = car.get("permanent_url", "")
            url = f"https://www.spinny.com{perm_url}" if perm_url else ""
            hub = car.get("hub", "") or ""

            lines = [
                f"<b>{year} {car.get('model', 'Tiguan')} {variant}</b>",
                f"📍 {city_name} | {fuel} | {mileage} km",
                f"{emoji} {status} | {price}",
            ]
            if hub:
                lines.append(f"🏢 {hub}")
            if url:
                lines.append(f"<a href='{url}'>View →</a>")
            car_details.append("\n".join(lines))

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    if total_found == 0:
        msg = [f"<b>🔍 Tiguan Search</b>", "", f"No Tiguans found across {len(CITIES)} cities."]
    else:
        msg = [f"<b>🔍 Tiguan Search ({total_found} found)</b>"]

    if car_details:
        msg.append("")
        msg.append("\n\n─────────────\n\n".join(car_details))

    msg.append("")
    msg.append(f"<i>Updated: {now}</i>")

    return "\n".join(msg)


if __name__ == "__main__":
    message = run()
    if message:
        print(message)
    else:
        print("Failed to search")
