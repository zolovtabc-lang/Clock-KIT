import discord
from discord.ext import commands, tasks
import os
import glob
from flask import Flask
from threading import Thread

# === KEEP ALIVE SERVER ===
# This part makes Render happy so it doesn't shut down the bot.
app = Flask('')

@app.route('/')
def home():
    return "Clock-in Bot is Online!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# === CONFIG ===
TOKEN = 'INSERT TOKEN DISINI'
CHANNEL_ID = 1234567890  # Your Discord channel ID
# NOTE: On Render, this path won't exist. You'll need to sync 
# your school files to the cloud (like Google Drive) for Render to see them!
PREVIEW_ROOT = r"D:\Master\Andi\File sekolah\File Project\preview"

# Enable Intents
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)
sent_images = set()

@tasks.loop(seconds=10)
async def check_previews():
    channel = bot.get_channel(CHANNEL_ID)
    if not channel: return

    if not os.path.exists(PREVIEW_ROOT):
        return

    search_pattern = os.path.join(PREVIEW_ROOT, "**", "*.[jp][pn]g")
    files = glob.glob(search_pattern, recursive=True)
    
    if not files: return
    
    latest_file = max(files, key=os.path.getmtime)

    if latest_file not in sent_images:
        shot_name = os.path.basename(os.path.dirname(latest_file))
        await channel.send(f"🚀 **New Update for Shot:** `{shot_name}`", file=discord.File(latest_file))
        sent_images.add(latest_file)

@bot.event
async def on_ready():
    print(f"Bot is online and watching: {PREVIEW_ROOT}")
    if not check_previews.is_running():
        check_previews.start()

# Start the web server and then the bot
keep_alive()
bot.run(TOKEN)
