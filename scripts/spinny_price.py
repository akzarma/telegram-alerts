"""
Spinny Car Price Tracker.
Fetches car price from Spinny API and returns formatted message.
"""

import requests
from datetime import datetime


# Car listing ID to track
CAR_ID = "25264538"
API_URL = f"https://api.spinny.com/v3/api/pdp/price-breakdown/{CAR_ID}/v2/"

# Headers to mimic browser request
HEADERS = {
    "accept": "*/*",
    "accept-language": "en-US,en-IN;q=0.9,en;q=0.8,hi;q=0.7",
    "content-type": "application/json",
    "origin": "https://www.spinny.com",
    "platform": "web",
    "referer": "https://www.spinny.com/",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
}


def format_price(amount: int) -> str:
    """Format price in Indian Lakh format."""
    if amount >= 100000:
        lakhs = amount / 100000
        return f"₹{lakhs:.2f} Lakh"
    return f"₹{amount:,}"


def run() -> str | None:
    """
    Fetch car price from Spinny API and return formatted message.
    
    Returns:
        Formatted message string or None if request fails
    """
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract price information
        result = data.get("result", {})
        
        # Get car details
        car_name = result.get("car_name", "Unknown Car")
        
        # Get price breakdown
        price_breakup = result.get("price_breakup", [])
        
        # Build message
        lines = [
            "<b>🚗 Spinny Car Price Update</b>",
            "",
            f"<b>Car:</b> {car_name}",
            "",
            "<b>Price Breakdown:</b>",
        ]
        
        total_price = 0
        for item in price_breakup:
            label = item.get("label", "")
            value = item.get("value", 0)
            is_total = item.get("is_total", False)
            
            if is_total:
                total_price = value
                lines.append("")
                lines.append(f"<b>💰 {label}: {format_price(value)}</b>")
            else:
                lines.append(f"• {label}: {format_price(value)}")
        
        # Add link to listing
        listing_url = f"https://www.spinny.com/buy-used-cars/-d{CAR_ID}"
        lines.append("")
        lines.append(f"<a href='{listing_url}'>View on Spinny</a>")
        
        # Add timestamp
        now = datetime.now().strftime("%d %b %Y, %I:%M %p")
        lines.append("")
        lines.append(f"<i>Last checked: {now}</i>")
        
        return "\n".join(lines)
        
    except requests.RequestException as e:
        print(f"Failed to fetch Spinny price: {e}")
        return None
    except (KeyError, TypeError) as e:
        print(f"Failed to parse Spinny response: {e}")
        return None


if __name__ == "__main__":
    # Test the script
    message = run()
    if message:
        print(message)
    else:
        print("Failed to get price data")
