import "jsr:@supabase/functions-js/edge-runtime.d.ts";

// Configuration - set these as Supabase Edge Function secrets
// supabase secrets set TELEGRAM_BOT_TOKEN=xxx GITHUB_TOKEN=xxx
const TELEGRAM_BOT_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN")!;
const GITHUB_TOKEN = Deno.env.get("GITHUB_TOKEN")!;
const GITHUB_REPO = "akzarma/telegram-alerts";
const ALLOWED_CHAT_ID = Number(Deno.env.get("ALLOWED_CHAT_ID")) || 676465574;

// Commands that trigger the price update
const TRIGGER_COMMANDS = [
  "/update",
  "/price",
  "car price update",
  "price update",
  "update price",
  "check price",
];

// Hair schedule – IST (UTC+5:30)
const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

// Night (9 PM): only overnight items — no washing/bathing at night
const NIGHT_BY_DAY: Record<number, string> = {
  0: "Ketoconazole 2% (1) overnight → wash next day",
  1: "Nidcort-CS (2) overnight → shampoo next day",
  3: "Nidcort-CS (2) overnight → shampoo next day",
  5: "Nidcort-CS (2) overnight → shampoo next day",
};

// Bath (10 AM): Ketoclenz CT wash on Tue/Thu/Sat only
const BATH_DAYS = new Set([2, 4, 6]); // JS getDay: Tue=2, Thu=4, Sat=6

function getIST(): { day: number; hour: number; minute: number } {
  const now = new Date();
  const utc = now.getTime() + now.getTimezoneOffset() * 60000;
  const ist = new Date(utc + 5.5 * 60 * 60 * 1000);
  return {
    day: ist.getDay(),
    hour: ist.getHours(),
    minute: ist.getMinutes(),
  };
}

function getTodaysPlan(day: number): string {
  const dayName = DAYS[day];
  const lunch = day === 5 ? "Meganeuron OD+ + Uprise D3" : "Meganeuron OD+";
  const night = NIGHT_BY_DAY[day] ?? "—";
  const hasBath = BATH_DAYS.has(day);
  const bathLine = hasBath
    ? " 10 AM  | Bath    | Ketoclenz CT (3) 5 min + regular shampoo\n"
    : "";
  const nightLine = night !== "—"
    ? " 9 PM   | Night   | " + night + "\n"
    : "";
  return (
    "<b>📋 Today's plan – " + dayName + "</b>\n\n" +
    "<pre>" +
    "Time   | Slot    | Medicine / Action\n" +
    "-------|---------|----------------------------------------\n" +
    " 8 AM  | Morning | Trichogain 1 cap (after breakfast)\n" +
    " 8 AM  | Morning | AGA Pro 6 sprays\n" +
    bathLine +
    " 2 PM  | Lunch   | " + lunch + "\n" +
    " 7 PM  | Evening | AGA Pro 6 sprays\n" +
    nightLine +
    "</pre>"
  );
}

function formatTime12hr(hour: number): string {
  if (hour === 0) return "12 AM";
  if (hour < 12) return hour + " AM";
  if (hour === 12) return "12 PM";
  return (hour - 12) + " PM";
}

function getNextSlot(day: number, hour: number, minute: number): string {
  const dayName = DAYS[day];
  const hasBath = BATH_DAYS.has(day);
  const hasNight = day in NIGHT_BY_DAY;

  const slots: { hour: number; min: number; label: string; item: string }[] = [
    { hour: 8, min: 0, label: "Morning", item: "Trichogain 1 cap (after breakfast), AGA Pro 6 sprays" },
  ];
  if (hasBath) {
    slots.push({ hour: 10, min: 0, label: "Bath", item: "Ketoclenz CT (3) – 5 min on scalp, then regular shampoo" });
  }
  slots.push(
    { hour: 14, min: 0, label: "Lunch", item: day === 5 ? "Meganeuron OD+ + Uprise D3" : "Meganeuron OD+" },
    { hour: 19, min: 0, label: "Evening", item: "AGA Pro 6 sprays" },
  );
  if (hasNight) {
    slots.push({ hour: 21, min: 0, label: "Night", item: NIGHT_BY_DAY[day] ?? "" });
  }

  const nowMins = hour * 60 + minute;
  for (const s of slots) {
    const slotMins = s.hour * 60 + s.min;
    if (slotMins > nowMins || (slotMins === nowMins)) {
      const time = formatTime12hr(s.hour);
      return (
        "<b>⏭ Next: " + dayName + " " + time + " – " + s.label + "</b>\n\n" +
        "<b>" + s.item + "</b>"
      );
    }
  }
  // All today's slots passed → show tomorrow's first slot
  const tomorrow = (day + 1) % 7;
  const nextDayName = DAYS[tomorrow];
  return (
    "<b>⏭ Next: " + nextDayName + " 8 AM – Morning</b>\n\n" +
    "<b>Trichogain 1 cap (after breakfast), AGA Pro 6 sprays</b>"
  );
}

function isHairScheduleQuery(text: string): "today" | "tomorrow" | "next" | false {
  const t = text.replace(/[?\s]+/g, " ").trim();
  if (/\b(tomorrow'?s? plan|tomorrow plan|what'?s? tomorrow'?s? plan)\b/i.test(t)) return "tomorrow";
  if (/\b(today'?s? plan|today plan|what'?s? today'?s? plan)\b/i.test(t)) return "today";
  if (/\b(hair schedule|hair plan)\b/i.test(t) && (/\b(today|plan)\b/i.test(t) || t.length < 25)) return "today";
  if (/\bwhat'?s? next\b/i.test(t) && (/\bhair\b/i.test(t) || /\bschedule\b/i.test(t))) return "next";
  if (/\bwhat'?s? next\b/i.test(t) && t.length < 30) return "next";
  return false;
}

interface TelegramMessage {
  message?: {
    chat: { id: number };
    text?: string;
    from?: { first_name?: string };
  };
}

async function sendTelegramMessage(chatId: number, text: string, replyMarkup?: unknown): Promise<void> {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  const payload: Record<string, unknown> = {
    chat_id: chatId,
    text: text,
    parse_mode: "HTML",
    disable_notification: true,
    disable_web_page_preview: true,
  };
  if (replyMarkup) payload.reply_markup = replyMarkup;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

async function triggerGitHubWorkflow(): Promise<boolean> {
  const url = `https://api.github.com/repos/${GITHUB_REPO}/dispatches`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${GITHUB_TOKEN}`,
      "Accept": "application/vnd.github.v3+json",
      "Content-Type": "application/json",
      "User-Agent": "supabase-edge-function",
    },
    body: JSON.stringify({ event_type: "daily-alert" }),
  });
  return response.status === 204;
}

Deno.serve(async (req: Request) => {
  // Only accept POST requests
  if (req.method !== "POST") {
    return new Response("OK", { status: 200 });
  }

  try {
    const body: TelegramMessage = await req.json();
    const message = body.message;

    if (!message || !message.text) {
      return new Response("OK", { status: 200 });
    }

    const chatId = message.chat.id;
    const text = message.text.toLowerCase().trim();
    const userName = message.from?.first_name || "there";

    // Security: Only respond to allowed chat
    if (chatId !== ALLOWED_CHAT_ID) {
      console.log(`Unauthorized chat ID: ${chatId}`);
      return new Response("OK", { status: 200 });
    }

    // Check if message matches any trigger command
    const isTriggered = TRIGGER_COMMANDS.some((cmd) =>
      text === cmd.toLowerCase() || text.startsWith(cmd.toLowerCase())
    );

    if (isTriggered) {
      // Send acknowledgment
      await sendTelegramMessage(chatId, `🔄 Fetching car prices, ${userName}...`);

      // Trigger GitHub workflow
      const success = await triggerGitHubWorkflow();

      if (!success) {
        await sendTelegramMessage(chatId, "❌ Failed to trigger price update. Please try again.");
      }
      // If success, the workflow will send the actual price update
    } else if (text === "/help" || text === "help") {
      const keyboard = {
        keyboard: [
          [{ text: "What's today's plan?" }, { text: "What's tomorrow's plan?" }],
          [{ text: "What's next?" }, { text: "/update" }],
        ],
        resize_keyboard: true,
        one_time_keyboard: false,
      };
      await sendTelegramMessage(
        chatId,
        "<b>🚗 Spinny Price Bot</b>\n\n" +
        "Commands:\n" +
        "• /update – Get latest car prices\n" +
        "• /help – Show this help\n\n" +
        "<b>📋 Hair schedule</b>\n" +
        "• Today's plan – full plan for today\n" +
        "• Tomorrow's plan – plan for tomorrow\n" +
        "• What's next – next upcoming item\n\n" +
        "👇 Tap the buttons below to use quickly!",
        keyboard,
      );
    } else {
      const hair = isHairScheduleQuery(text);
      if (hair) {
        const ist = getIST();
        let msg: string;
        if (hair === "today") {
          msg = getTodaysPlan(ist.day);
        } else if (hair === "tomorrow") {
          msg = getTodaysPlan((ist.day + 1) % 7).replace("Today's plan", "Tomorrow's plan");
        } else {
          msg = getNextSlot(ist.day, ist.hour, ist.minute);
        }
        await sendTelegramMessage(chatId, msg);
      }
    }

    return new Response("OK", { status: 200 });
  } catch (error) {
    console.error("Error processing webhook:", error);
    return new Response("OK", { status: 200 });
  }
});
