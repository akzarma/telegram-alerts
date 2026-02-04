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

interface TelegramMessage {
  message?: {
    chat: { id: number };
    text?: string;
    from?: { first_name?: string };
  };
}

async function sendTelegramMessage(chatId: number, text: string): Promise<void> {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text: text,
      parse_mode: "HTML",
    }),
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
      await sendTelegramMessage(
        chatId,
        "<b>🚗 Spinny Price Bot</b>\n\n" +
        "Commands:\n" +
        "• /update - Get latest car prices\n" +
        "• /price - Get latest car prices\n" +
        "• /help - Show this help\n\n" +
        "You can also say:\n" +
        "• \"car price update\"\n" +
        "• \"check price\""
      );
    }

    return new Response("OK", { status: 200 });
  } catch (error) {
    console.error("Error processing webhook:", error);
    return new Response("OK", { status: 200 });
  }
});
