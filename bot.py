import os
import asyncio
import discord

from discord.ext import commands
from modules.helpers import *

# Bot setup
bot = commands.Bot(
    command_prefix=PREFIX,
    owner_ids=OWNER_IDS,
    intents=discord.Intents.all()
)

bot.remove_command('help')

async def load_extensions():
    for filename in os.listdir(COG_FOLDER):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

# Call the function to load extensions
asyncio.run(load_extensions())

# Starting cash and level for new players
STARTING_CASH = 1000
STARTING_LEVEL = 0
WORK_REWARD = 100
WORK_COOLDOWN = 12  

# Placeholder for user profiles and cooldowns
user_profiles = {}
work_cooldowns = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command(name="profile")
async def profile(ctx):
    """Show the user's profile."""
    user_id = ctx.author.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"cash": STARTING_CASH, "level": STARTING_LEVEL}
    profile = user_profiles[user_id]
    await ctx.send(f"Profile for {ctx.author.name}:\nCash: {profile['cash']}\nLevel: {profile['level']}")

@bot.command(name="work")
async def work(ctx):
    """Earn cash every 10 minutes."""
    user_id = ctx.author.id
    if user_id not in user_profiles:
        user_profiles[user_id] = {"cash": STARTING_CASH, "level": STARTING_LEVEL}
    if user_id in work_cooldowns and work_cooldowns[user_id] > asyncio.get_event_loop().time():
        remaining = int(work_cooldowns[user_id] - asyncio.get_event_loop().time())
        await ctx.send(f"You need to wait {remaining} seconds before working again.")
        return
    user_profiles[user_id]["cash"] += WORK_REWARD
    work_cooldowns[user_id] = asyncio.get_event_loop().time() + WORK_COOLDOWN
    await ctx.send(f"You worked and earned ${WORK_REWARD}! Your new balance is ${user_profiles[user_id]['cash']}.")

# Run the bot
if __name__ == "__main__":
    bot.run(TOKEN)
