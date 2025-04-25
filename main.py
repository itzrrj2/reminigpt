from pyrogram import Client
from handlers.commands import command_handlers
from handlers.image import image_handlers
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("image_processor", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

command_handlers(app)
image_handlers(app)

print("Bot is running...")
app.run()
