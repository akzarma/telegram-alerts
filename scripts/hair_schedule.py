"""
Hair treatment schedule reminders (Dr. T. Annapurna).
Triggered by cron-job.org via GitHub repository_dispatch.
Supports: morning, lunch, evening, night slots.
Night slot is day-specific (IST).
"""
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

NIGHT_BY_DAY = {
    0: "Ketoconazole 2% (1) overnight - wash with regular shampoo next day",  # Sun
    1: "Nidcort-CS (2) overnight - shampoo next day",                         # Mon
    2: "Ketoclenz CT (3) - 5 min scalp, then regular shampoo",                # Tue
    3: "Nidcort-CS (2) overnight - shampoo next day",                         # Wed
    4: "Ketoclenz CT (3) - 5 min, then regular shampoo",                      # Thu
    5: "Nidcort-CS (2) overnight - shampoo next day",                         # Fri
    6: "Ketoclenz CT (3) - 5 min, then regular shampoo",                      # Sat
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _day_name() -> str:
    """Current IST day name."""
    now = datetime.now(IST)
    return DAYS[now.weekday()]


def _weekday() -> int:
    """Current IST weekday (0=Mon .. 6=Sun)."""
    return datetime.now(IST).weekday()


def run_morning() -> str:
    return (
        f"🌅 Hair schedule – Morning ({_day_name()})\n"
        "• Trichogain 1 cap (after breakfast)\n"
        "• AGA Pro 6 sprays"
    )


def run_lunch() -> str:
    wd = _weekday()
    base = "💊 Hair schedule – After lunch"
    if wd == 4:  # Friday
        return f"{base} ({_day_name()})\n• Meganeuron OD+\n• Uprise D3"
    return f"{base} ({_day_name()})\n• Meganeuron OD+"


def run_evening() -> str:
    return (
        f"🌇 Hair schedule – Evening ({_day_name()})\n"
        "• AGA Pro 6 sprays"
    )


def run_night() -> str:
    wd = _weekday()
    # python weekday: 0=Mon..6=Sun; NIGHT_BY_DAY keyed on JS getDay (0=Sun..6=Sat)
    js_day = (wd + 1) % 7  # convert Mon=0 → 1, ... Sun=6 → 0
    item = NIGHT_BY_DAY.get(js_day, "")
    return (
        f"🌙 Hair schedule – Night ({_day_name()})\n"
        f"• {item}"
    )
