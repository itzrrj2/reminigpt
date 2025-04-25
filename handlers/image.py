from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import *
from utils.helpers import (
    check_user_in_channel, check_subscription, get_file_size,
    fetch_file_blob, upload_to_ar, process_image
)
import aiohttp
from io import BytesIO

def image_handlers(app):
    @app.on_message(filters.photo | filters.document)
    async def handle_image(client, message: Message):
        user = message.from_user
        chat_id = message.chat.id

        # Force Join System
        if not await check_subscription(client, user.id):
            join_buttons = [
                [InlineKeyboardButton(f"Join @{channel}", url=f"https://t.me/{channel}")]
                for channel in REQUIRED_CHANNELS
            ]
            join_buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="checkjoin")])
            join_buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])
            await message.reply(
                "🚫 <b>You must join the required channels to use this bot.</b>\n\nAfter joining, tap <b>I Joined</b>.",
                reply_markup=InlineKeyboardMarkup(join_buttons),
                parse_mode="HTML"
            )
            return
        else:
            await message.reply("✅ You are verified! Send a photo or image document to begin processing.")

        # Safe file detection
        if message.photo:
            file = message.photo[-1] if isinstance(message.photo, list) else message.photo
        elif message.document:
            file = message.document
        else:
            await message.reply("❌ Only photo or image document is supported.")
            return

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
            [InlineKeyboardButton("Permanent 🖇️", callback_data=f"permanent {hosted_url}")],
            [InlineKeyboardButton("Back to Menu ⬅️", callback_data="refresh")]
        ])

        await message.reply("✅ Image uploaded! Choose what you want to do:", reply_markup=buttons)

    @app.on_callback_query()
    async def handle_callback(client, callback_query: CallbackQuery):
        data = callback_query.data
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id

        # Check join button
        if data == "checkjoin":
            if await check_subscription(client, user_id):
                await callback_query.message.reply("✅ You are verified! Send a photo to start.")
            else:
                join_buttons = [
                    [InlineKeyboardButton(f"Join @{channel}", url=f"https://t.me/{channel}")]
                    for channel in REQUIRED_CHANNELS
                ]
                join_buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="checkjoin")])
                join_buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])
                await callback_query.message.reply(
                    "❌ You still haven't joined all required channels.",
                    reply_markup=InlineKeyboardMarkup(join_buttons),
                    parse_mode="HTML"
                )
            return

        # Refresh button
        if data == "refresh":
            if await check_subscription(client, user_id):
                await callback_query.message.reply("✅ You are verified! You can use the bot now.")
            else:
                join_buttons = [
                    [InlineKeyboardButton(f"Join @{channel}", url=f"https://t.me/{channel}")]
                    for channel in REQUIRED_CHANNELS
                ]
                join_buttons.append([InlineKeyboardButton("✅ I Joined", callback_data="checkjoin")])
                join_buttons.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])
                await callback_query.message.reply(
                    "❌ You still haven't joined all required channels.",
                    reply_markup=InlineKeyboardMarkup(join_buttons),
                    parse_mode="HTML"
                )
            return

        # Handle image tools
        if any(data.startswith(tool) for tool in ['enhance', 'removebg', 'restore', 'colorize', 'upscale']):
            tool, image_url = data.split()
            processing_msg = await callback_query.message.reply(f"🔄 {tool.capitalize()}ing your image...")

            result_url = await process_image(image_url, tool)
            if not result_url:
                await processing_msg.edit_text("❌ Failed to process image.")
                return

            await processing_msg.edit_text(f"✅ {tool.capitalize()} complete!")

            async with aiohttp.ClientSession() as session:
                async with session.get(result_url) as resp:
                    image_bytes = await resp.read()

            buffer = BytesIO(image_bytes)
            buffer.name = f"{tool}_result.jpg"

            await client.send_document(chat_id, buffer, caption=f"{tool.capitalize()}d image ✅")
