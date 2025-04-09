import discord
from discord.ext import commands
from PIL import Image
import random
import bisect
import os

class Slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="slots", help="Try your luck in the slots!")
    async def slots(self, ctx, bet: str):
        # Validate bet input
        if bet.lower() not in ["m", "a"] and not bet.isdigit():
            await ctx.send("Invalid bet amount. Use a number, 'm' for max, or 'a' for all in.")
            return

        # Load reel image
        path = "/images/"  # Update with the actual path to your reel image
        reel = Image.open(f'{path}.png').convert('RGBA')
        rw, rh = reel.size
        item = 180
        items = rh // item

        # Generate random spins
        s1 = random.randint(1, items - 1)
        s2 = random.randint(1, items - 1)
        s3 = random.randint(1, items - 1)

        # Adjust for win rate
        win_rate = 98 / 100
        if random.random() < win_rate:
            symbols_weights = [3.5, 7, 15, 25, 55]
            x = round(random.random() * 100, 1)
            pos = bisect.bisect(symbols_weights, x)
            s1 = pos + (random.randint(1, (items // 6) - 1) * 6)
            s2 = pos + (random.randint(1, (items // 6) - 1) * 6)
            s3 = pos + (random.randint(1, (items // 6) - 1) * 6)
            s1 = s1 - 6 if s1 == items else s1
            s2 = s2 - 6 if s2 == items else s2
            s3 = s3 - 6 if s3 == items else s3

        # Generate animation frames
        images = []
        speed = 6
        facade = Image.new('RGBA', (rw * 3, rh), (255, 255, 255))  # Placeholder facade
        for i in range(1, (item // speed) + 1):
            bg = Image.new('RGBA', facade.size, color=(255, 255, 255))
            bg.paste(reel, (25 + rw * 0, 100 - (speed * i * s1)))
            bg.paste(reel, (25 + rw * 1, 100 - (speed * i * s2)))
            bg.paste(reel, (25 + rw * 2, 100 - (speed * i * s3)))
            bg.alpha_composite(facade)
            images.append(bg)

        # Save animation as GIF
        fp = f"{ctx.author.id}.gif"
        images[0].save(
            fp,
            save_all=True,
            append_images=images[1:],
            duration=50
        )

        # Determine win/loss
        result = "lost"
        if (1 + s1) % 6 == (1 + s2) % 6 == (1 + s3) % 6:
            result = "won"

        # Create embed
        embed = discord.Embed(
            title=f"You {result}!",
            description="Better luck next time!" if result == "lost" else "Congratulations!",
            color=discord.Color.green() if result == "won" else discord.Color.red()
        )
        file = discord.File(fp, filename=fp)
        embed.set_image(url=f"attachment://{fp}")

        # Send result
        await ctx.send(file=file, embed=embed)

        # Clean up
        os.remove(fp)

async def setup(bot):
    await bot.add_cog(Slots(bot))