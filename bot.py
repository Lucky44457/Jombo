import os
import re
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH

# ================= BASIC SETUP =================

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

app = Client(
    "ulp_combo_500mb",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# ================= HEURISTIC LOGIC =================

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def is_url(token: str) -> bool:
    t = token.lower()
    return t.startswith("http") or t.startswith("www.") or "/" in t

def extract_pair(line: str):
    # split by colon
    parts = [p.strip() for p in line.split(":")]

    # remove empty tokens
    parts = [p for p in parts if p]
    if not parts:
        return None

    # remove obvious URL / context parts
    parts = [p for p in parts if not is_url(p)]
    if not parts:
        return None

    # 1️⃣ email-first strategy
    email_index = None
    for i, p in enumerate(parts):
        if EMAIL_RE.match(p):
            email_index = i
            break

    if email_index is not None:
        # password = next meaningful token after email
        for j in range(email_index + 1, len(parts)):
            pwd = parts[j]
            if len(pwd) >= 3:
                return f"{parts[email_index]}:{pwd}"
        return None

    # 2️⃣ fallback: username + last token
    if len(parts) >= 2:
        user = parts[0]
        pwd = parts[-1]
        if len(pwd) >= 3:
            return f"{user}:{pwd}"

    return None

# ================= BOT COMMANDS =================

@app.on_message(filters.private & filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "✅ **Bot is ONLINE**\n\n"
        "ULP → Combo Converter (≈90% heuristic)\n\n"
        "📂 Send ONE `.txt` ULP file\n"
        "📏 Max size: 500 MB\n"
        "🔄 Supports mixed RAW logs (colon based)\n"
        "📤 Output: email/username:password\n\n"
        "⚠️ Send only one file at a time"
    )

@app.on_message(filters.private & filters.document)
async def handle_ulp(_, message):
    doc = message.document

    if not doc.file_name.endswith(".txt"):
        await message.reply_text("❌ Only .txt files allowed")
        return

    if doc.file_size > MAX_FILE_SIZE:
        await message.reply_text("❌ File size exceeds 500 MB limit")
        return

    user_id = message.from_user.id
    ulp_path = f"{DOWNLOAD_DIR}/{user_id}_ulp.txt"
    combo_path = f"{DOWNLOAD_DIR}/{user_id}_combo.txt"

    await message.reply_text("⬇️ Downloading ULP file...")
    await message.download(ulp_path)

    combos = set()
    total_lines = 0

    await message.reply_text("⚙️ Processing file, please wait...")

    with open(ulp_path, "r", errors="ignore") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue

            pair = extract_pair(line)
            if pair:
                combos.add(pair)

    if not combos:
        await message.reply_text("❌ No valid combos found")
        os.remove(ulp_path)
        return

    with open(combo_path, "w") as f:
        for combo in combos:
            f.write(combo + "\n")

    await message.reply_document(
        combo_path,
        caption=(
            "✅ **Conversion Completed**\n\n"
            f"📄 Total Lines: {total_lines}\n"
            f"🎯 Extracted Combos: {len(combos)}"
        )
    )

    os.remove(ulp_path)
    os.remove(combo_path)

print("ULP Combo Bot (500MB | Heuristic Mode) is running...")
app.run()
