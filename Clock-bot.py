import discord
from discord.ext import commands, tasks
import os
import glob

# === CONFIG ===
TOKEN = 'MTQ3OTUwNDQwOTQ2MDM0Mjc5NA.GMqlIU.2J9gW3KoJLuwdIxr5ApkM5eZp1oCcMtb3Hhx7Y'
CHANNEL_ID = 1234567890  # Your Discord channel ID
# Your central preview folder
PREVIEW_ROOT = r"D:\Master\Andi\File sekolah\File Project\preview"

# Enable Intents in code
intents = discord.Intents.default()
intents.message_content = True  # Matches the toggle you just turned on!

bot = commands.Bot(command_prefix="!", intents=intents)
sent_images = set()

@tasks.loop(seconds=10)
async def check_previews():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return

    # Search for any JPG/PNG inside the shot subfolders
    search_pattern = os.path.join(PREVIEW_ROOT, "**", "*.[jp][pn]g")
    files = glob.glob(search_pattern, recursive=True)
    
    if not files: return
    
    # Grab the newest file overall
    latest_file = max(files, key=os.path.getmtime)

    if latest_file not in sent_images:
        shot_name = os.path.basename(os.path.dirname(latest_file))
        await channel.send(f"🚀 **New Update for Shot:** `{shot_name}`", file=discord.File(latest_file))
        sent_images.add(latest_file)

@bot.event
async def on_ready():
    print(f"Bot is online and watching: {PREVIEW_ROOT}")
    check_previews.start()

bot.run(TOKEN)