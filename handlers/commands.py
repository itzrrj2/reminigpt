from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def command_handlers(app):
    @app.on_message(filters.command("start"))
    async def start(client, message: Message):
        name = message.from_user.first_name
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Channel 📢", url="https://t.me/Ashlynn_Repository")],
            [InlineKeyboardButton("Check Join Status 🔍", callback_data="checkjoin")],
            [InlineKeyboardButton("Refresh 🔄", callback_data="refresh")]
        ])
        await message.reply_text(
            f"Hey {name} 👋\n\nWelcome to the Image Processing Bot! Send an image to remove background, upscale or enhance. 💛",
            reply_markup=buttons
        )