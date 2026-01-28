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


def format_price_inr(amount: float) -> str:
    """Format price in Indian format with commas."""
    amount = int(amount)
    if amount >= 100000:
        # Format in lakhs: 15,74,658
        s = str(amount)
        # Last 3 digits
        result = s[-3:]
        s = s[:-3]
        # Then groups of 2
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        return f"₹{result}"
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
        resp_data = response.json()
        
        if not resp_data.get("is_success"):
            print("API returned unsuccessful response")
            return None
        
        data = resp_data.get("data", {})
        
        # Extract car details
        make = data.get("make", "Unknown")
        model = data.get("model", "Unknown")
        variant_data = data.get("variant", {})
        variant = variant_data.get("display_name", "") if isinstance(variant_data, dict) else ""
        year = data.get("make_year", "")
        mileage = data.get("mileage", "N/A")
        fuel = data.get("fuel_type", "").capitalize()
        transmission = data.get("transmission", "").capitalize()
        
        # Extract availability status
        is_booked = data.get("booked", False)
        is_sold = data.get("sold", False)
        is_on_hold = data.get("on_hold", False)
        listing_status = data.get("listing_status", "unknown")
        
        car_name = f"{year} {make} {model}"
        if variant:
            car_name += f" {variant}"
        
        # Extract pricing
        pricing = data.get("pricing", {})
        listing_price_str = pricing.get("listing_price", {}).get("price", "N/A")
        market_price_str = pricing.get("market_price", {}).get("price", "N/A")
        savings_msg = pricing.get("market_price", {}).get("message", "")
        
        # Extract price breakdown
        pb = data.get("price_breakdown_v2", {})
        listing_price = pb.get("listing_price", 0)
        base_price = pb.get("base_listing_price", 0)
        tax_data = pb.get("tax_data", {})
        tax_amount = tax_data.get("numeric_value", 0)
        
        # Get add-ons breakdown
        base_add_ons = pb.get("base_add_on_data_list", [])
        add_on_total = 0
        add_on_items = []
        for addon in base_add_ons:
            if addon.get("name") == "base_add_on":
                add_on_total = addon.get("value", 0)
                on_click = addon.get("on_click", [])
                if on_click:
                    for item in on_click:
                        add_on_items.append({
                            "name": item.get("display_name", ""),
                            "value": item.get("value", 0)
                        })
        
        # Determine availability status
        if is_sold:
            status_emoji = "🔴"
            status_text = "SOLD"
        elif is_booked:
            status_emoji = "🟡"
            status_text = "BOOKED"
        elif is_on_hold:
            status_emoji = "🟠"
            status_text = "ON HOLD"
        else:
            status_emoji = "🟢"
            status_text = "AVAILABLE"
        
        # Build message
        lines = [
            "<b>🚗 Spinny Car Price Update</b>",
            "",
            f"<b>{car_name}</b>",
            f"📍 {fuel} | {transmission} | {mileage} km",
            "",
            f"<b>Status:</b> {status_emoji} {status_text}",
            "",
            "<b>💰 Pricing:</b>",
            f"• Spinny Price: <b>₹{listing_price_str}</b>",
            f"• Market Price: ₹{market_price_str}",
        ]
        
        if savings_msg:
            # Extract savings amount
            lines.append(f"• <i>{savings_msg}</i>")
        
        lines.append("")
        lines.append("<b>📋 Price Breakdown:</b>")
        lines.append(f"• Base Price: {format_price_inr(base_price)}")
        
        if add_on_items:
            lines.append(f"• Add-ons ({format_price_inr(add_on_total)}):")
            for item in add_on_items:
                lines.append(f"   - {item['name']}: {format_price_inr(item['value'])}")
        
        if tax_amount:
            lines.append(f"• Taxes: {format_price_inr(tax_amount)}")
        
        lines.append("")
        lines.append(f"<b>Total: {format_price_inr(listing_price)}</b>")
        
        # Add link to listing
        listing_url = f"https://www.spinny.com/buy-used-cars/-d{CAR_ID}"
        lines.append("")
        lines.append(f"🔗 <a href='{listing_url}'>View on Spinny</a>")
        
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
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test the script
    message = run()
    if message:
        print(message)
    else:
        print("Failed to get price data")
