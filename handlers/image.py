from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import *
from utils.helpers import (
    check_user_in_channel, get_file_size, fetch_file_blob, upload_to_ar
)

def image_handlers(app):
    @app.on_message(filters.photo | filters.document)
    async def handle_image(client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        if not await check_user_in_channel(client, user.id):
            await message.reply_text("❌ Please join our channel to use this bot!")
            return

        file = message.photo[-1] if message.photo else message.document
        file_info = await client.get_file(file.file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        file_size = await get_file_size(file_url)
        if file_size > MAX_DOCUMENT_SIZE:
            await message.reply("❌ File too large (max 50MB)")
            return

        uploading_msg = await message.reply("📤 Uploading to AR Hosting...")
        blob = await fetch_file_blob(file_url)
        hosted_url = await upload_to_ar(blob, "uploaded.jpg")
        await uploading_msg.delete()

        if not hosted_url:
            await message.reply("❌ Upload failed.")
            return

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Enhance 🦋", callback_data=f"enhance {hosted_url}"),
             InlineKeyboardButton("Remove BG 🧼", callback_data=f"removebg {hosted_url}")],
            [InlineKeyboardButton("Restore 🌟", callback_data=f"restore {hosted_url}"),
             InlineKeyboardButton("Colorize 🌈", callback_data=f"colorize {hosted_url}")],
            [InlineKeyboardButton("Upscale 📈", callback_data=f"upscale {hosted_url}"),
             InlineKeyboardButton("View 🔰", url=hosted_url)],
            [InlineKeyboardButton("Permanent 🖇️", callback_data=f"permanent {hosted_url}")]
        ])

        await message.reply("✅ Image uploaded! Choose what you want to do:", reply_markup=buttons)
