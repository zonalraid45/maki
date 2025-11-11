import os
import discord
from discord.ext import commands
from datetime import timedelta
import re

# ───────────── Settings ─────────────
TOKEN = os.getenv("DISCORD_TOKEN")  # or replace directly: TOKEN = "YOUR_TOKEN_HERE"
TIMEOUT_DURATION = timedelta(minutes=5)
EXEMPT_ROLES = {"moderator", "admin"}  # roles ignored by bot

# ───────────── Discord Setup ─────────────
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
recent_messages = {}

# ───────────── Helper Functions ─────────────
def is_gibberish(text: str) -> bool:
    if len(text) < 6:
        return False
    # No vowels and only letters → gibberish
    if not any(c in "aeiouAEIOU" for c in text) and text.isalpha():
        return True
    # Too many unique random letters (like "ndrhkwrlyutwq")
    letters = re.sub(r"[^a-zA-Z]", "", text)
    if len(letters) >= 6 and len(set(letters)) > 6:
        return True
    return False


def is_exempt(member: discord.Member) -> bool:
    """Return True if user has Moderator or Admin role."""
    return any(role.name.lower() in EXEMPT_ROLES for role in member.roles)


# ───────────── Events ─────────────
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    member = message.author
    content = message.content.strip().lower()

    # Skip exempt roles
    if is_exempt(member):
        return

    # Track last few messages by user
    history = recent_messages.get(member.id, [])
    history.append(content)
    if len(history) > 6:
        history.pop(0)
    recent_messages[member.id] = history

    # ─── Repeated message check ───
    if history.count(content) >= 4:
        try:
            await member.timeout(TIMEOUT_DURATION, reason="Spam (repeated message 4+ times)")
            await message.channel.send(
                f"🚫 {member.mention} You are timed out for 5 minutes for spamming the same message repeatedly."
            )
            return
        except discord.Forbidden:
            await message.channel.send("⚠️ Missing permission to timeout users.")
        except Exception as e:
            print("Error (spam):", e)

    # ─── Gibberish check ───
    if is_gibberish(content):
        try:
            await member.timeout(TIMEOUT_DURATION, reason="Nonsense/gibberish message")
            await message.channel.send(
                f"🚫 {member.mention} You are timed out for 5 minutes for sending nonsense messages."
            )
            return
        except discord.Forbidden:
            await message.channel.send("⚠️ Missing permission to timeout users.")
        except Exception as e:
            print("Error (gibberish):", e)

    await bot.process_commands(message)


bot.run(TOKEN)
