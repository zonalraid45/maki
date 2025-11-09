import os
import discord
from discord.ext import commands

# ---- Settings ----
TOKEN = os.getenv("DISCORD_TOKEN")
AD_CHANNEL_NAME = "advertisement"  # your ad channel name

# ---- Discord Intents ----
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---- Advertisement Keywords ----
AD_KEYWORDS = [
    "discord.gg",
    "invite.gg",
    "youtube.com",
    "twitch.tv",
    "kick.com",
    "chess.com",
    "telegram.me",
    "instagram.com",
    "join my server",
    "join my",
    "follow me on",
    "lichess.org/team",
    "lichess.org/swiss",
    "lichess.org/tournament",
    "lichess.org/blog"
]

# ---- Only Admins are exempt ----
EXEMPT_ROLES = ["Admin"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # --- Skip the advertisement channel ---
    if message.channel.name.lower() == AD_CHANNEL_NAME.lower():
        return

    # --- Skip Admins ---
    if any(role.name in EXEMPT_ROLES for role in message.author.roles):
        return

    msg_lower = message.content.lower()

    # --- Detect any blog links or ad keywords ---
    contains_ad = any(keyword in msg_lower for keyword in AD_KEYWORDS)
    contains_lichess_blog = "lichess.org/@/" in msg_lower and "/blog/" in msg_lower

    if contains_ad or contains_lichess_blog:
        try:
            await message.delete()
            warning = (
                f"{message.author.mention}, Advertising is only allowed in "
                f"#{AD_CHANNEL_NAME}!\n"
                " It will be **timeout next time** if I see you again advertising here."
            )
            await message.channel.send(warning)  # warning stays visible
            print(f"🗑 Deleted ad from {message.author} in #{message.channel}")
        except Exception as e:
            print(f"⚠️ Error deleting message: {e}")

    await bot.process_commands(message)

bot.run(TOKEN)
