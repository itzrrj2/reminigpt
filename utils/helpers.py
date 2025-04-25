import aiohttp
from config import CHANNEL_ID, AR_HOSTING_API, REQUIRED_CHANNELS

async def check_user_in_channel(client, user_id):
    try:
        member = await client.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

async def check_subscription(client, user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await client.get_chat_member(f"@{channel}", user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

async def get_file_size(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            return int(resp.headers.get("Content-Length", 0))

async def fetch_file_blob(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.read()

async def upload_to_ar(file_bytes, filename):
    data = aiohttp.FormData()
    data.add_field('file', file_bytes, filename=filename, content_type='application/octet-stream')
    async with aiohttp.ClientSession() as session:
        async with session.post(AR_HOSTING_API, data=data) as resp:
            res = await resp.json()
            return res.get("data")

async def process_image(image_url, tool):
    tools = {
        'upscale': 'upscale',
        'restore': 'restore',
        'enhance': 'enhance',
        'removebg': 'removebg',
        'colorize': 'colorize'
    }
    url = f"https://reminisrbot.shresthstakeyt.workers.dev/?url={image_url}&tool={tools[tool]}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data.get("result", {}).get("resultImageUrl")
