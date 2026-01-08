import os
from pyrogram import Client, filters
from config import BOT_TOKEN, API_ID, API_HASH

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB limit

app = Client(
    "ulp_combo_500mb",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

@app.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text(
        "✅ **Bot is ONLINE**\n\n"
        "ULP → Combo Converter (500 MB)\n\n"
        "📂 Send ONE `.txt` ULP file\n"
        "📏 Max size: 500 MB\n"
        "🔄 Format: email|password|extra\n"
        "📤 Output: email:password\n\n"
        "⚠️ Send only one file at a time"
    )

@app.on_message(filters.document)
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

            if "|" not in line:
                continue

            parts = line.split("|", 2)
            if len(parts) < 2:
                continue

            email = parts[0].strip()
            password = parts[1].strip()

            if email and password:
                combos.add(f"{email}:{password}")

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
            f"🎯 Unique Combos: {len(combos)}"
        )
    )

    os.remove(ulp_path)
    os.remove(combo_path)

print("ULP Combo Bot (500MB) is running...")
app.run()
