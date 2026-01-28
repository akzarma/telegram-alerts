# Telegram Alerts

A modular system for sending daily notifications via Telegram. Easily extendable to track multiple APIs.

## Current Trackers

- **Spinny Price** - Tracks used car price from Spinny.com

## Setup

### 1. GitHub Secrets

Add these secrets in your repository settings (Settings > Secrets and variables > Actions):

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
- `TELEGRAM_CHAT_ID` - Your Telegram chat ID from @userinfobot

### 2. Trigger Configuration

The workflow is triggered via `repository_dispatch` event. Configure cron-job.org to call:

```
POST https://api.github.com/repos/YOUR_USERNAME/telegram-alerts/dispatches
```

Headers:
```
Authorization: Bearer YOUR_GITHUB_TOKEN
Accept: application/vnd.github.v3+json
Content-Type: application/json
```

Body:
```json
{"event_type": "daily-alert"}
```

### 3. Manual Testing

You can manually trigger the workflow from GitHub Actions tab using "Run workflow" button.

## Adding New Trackers

1. Create a new file in `scripts/` folder (e.g., `scripts/my_tracker.py`)
2. Implement a `run()` function that returns a message string
3. Import and call it from `main.py`

Example:
```python
# scripts/my_tracker.py
def run() -> str | None:
    # Fetch data and return formatted message
    return "My tracker update: ..."
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN=your_token
export TELEGRAM_CHAT_ID=your_chat_id

# Run
python main.py
```
