"""
Hair treatment schedule reminders (Dr. T. Annapurna).
Triggered by cron-job.org via GitHub repository_dispatch.
Supports: morning, bath (10 AM), lunch, evening, night slots.
Night slot is day-specific (IST).
Ketoclenz CT (wash) is at 10 AM on Tue/Thu/Sat.
Overnight items (Nidcort-CS, Ketoconazole 2%) stay at 9 PM.
"""
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

# Night slot: only overnight items (no washing/bathing)
# Python weekday: 0=Mon..6=Sun
NIGHT_BY_DAY = {
    0: "Nidcort-CS (2) overnight → shampoo next day",       # Mon
    2: "Nidcort-CS (2) overnight → shampoo next day",       # Wed
    4: "Nidcort-CS (2) overnight → shampoo next day",       # Fri
    6: "Ketoconazole 2% (1) overnight → wash next day",     # Sun
}

# Bath slot (10 AM): Ketoclenz CT on Tue/Thu/Sat
BATH_DAYS = {1, 3, 5}  # Tue, Thu, Sat

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
        f"🌅 Hair schedule – Morning 8 AM ({_day_name()})\n"
        "• Trichogain 1 cap (after breakfast)\n"
        "• AGA Pro 6 sprays"
    )


def run_bath() -> str:
    """10 AM – Ketoclenz CT wash on Tue/Thu/Sat only."""
    wd = _weekday()
    if wd in BATH_DAYS:
        return (
            f"🚿 Hair schedule – Bath 10 AM ({_day_name()})\n"
            "• Ketoclenz CT (3) – 5 min on scalp\n"
            "• Then wash with regular shampoo"
        )
    return ""  # No bath reminder on other days


def run_lunch() -> str:
    wd = _weekday()
    base = "💊 Hair schedule – After lunch 2 PM"
    if wd == 4:  # Friday
        return f"{base} ({_day_name()})\n• Meganeuron OD+\n• Uprise D3"
    return f"{base} ({_day_name()})\n• Meganeuron OD+"


def run_evening() -> str:
    """7 PM – AGA Pro, but skip on nights with overnight treatment (Mon/Wed/Fri/Sun)."""
    wd = _weekday()
    if wd in NIGHT_BY_DAY:
        return (
            f"🌇 Hair schedule – Evening 7 PM ({_day_name()})\n"
            "• Skip AGA Pro tonight (overnight treatment later)"
        )
    return (
        f"🌇 Hair schedule – Evening 7 PM ({_day_name()})\n"
        "• AGA Pro 6 sprays"
    )


def run_night() -> str:
    """9 PM – Overnight items only (Mon/Wed/Fri: Nidcort-CS, Sun: Ketoconazole 2%)."""
    wd = _weekday()
    item = NIGHT_BY_DAY.get(wd, "")
    if not item:
        return ""  # No night reminder on Tue/Thu/Sat
    return (
        f"🌙 Hair schedule – Night 9 PM ({_day_name()})\n"
        f"• {item}"
    )
