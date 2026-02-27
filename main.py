#!/usr/bin/env python3
"""
Telegram Alerts - Main Entry Point.
Runs all alert scripts and sends notifications via Telegram.
"""

import sys
from scripts import spinny_price, tiguan_search
from utils.telegram import send_message


def main():
    """Run all alert scripts and send combined notification."""
    print("Starting Telegram Alerts...")
    
    messages = []
    
    # Run Spinny price tracker
    print("Running Spinny price tracker...")
    spinny_msg = spinny_price.run()
    if spinny_msg:
        messages.append(spinny_msg)
    else:
        messages.append("⚠️ Failed to fetch Spinny car price")
    
    # Run Tiguan city search
    print("Running Tiguan city search...")
    tiguan_msg = tiguan_search.run()
    if tiguan_msg:
        messages.append(tiguan_msg)
    else:
        messages.append("⚠️ Failed to search Tiguan availability")
    
    # Send all messages
    if messages:
        # Join with separator if multiple messages
        full_message = "\n\n─────────────────\n\n".join(messages)
        
        success = send_message(full_message)
        if success:
            print("All notifications sent successfully!")
            return 0
        else:
            print("Failed to send notifications")
            return 1
    else:
        print("No messages to send")
        return 0


if __name__ == "__main__":
    sys.exit(main())
