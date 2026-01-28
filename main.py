#!/usr/bin/env python3
"""
Telegram Alerts - Main Entry Point.
Runs all alert scripts and sends notifications via Telegram.
"""

import sys
from scripts import spinny_price
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
    
    # Add more scripts here in the future:
    # from scripts import another_tracker
    # msg = another_tracker.run()
    # if msg:
    #     messages.append(msg)
    
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
