import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger("slowmode")

class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="slowmode")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def slowmode(self, ctx, duration: str = None, channel: discord.TextChannel = None):
        """Set slowmode. Usage: !slowmode 30s #channel or !slowmode off"""
        target = channel or ctx.channel
        
        if duration == "off" or duration is None:
            await target.edit(slowmode_delay=0)
            await ctx.send(f"✅ {target.mention} slowmode **disabled**")
        else:
            # Parse duration
            time_map = {'s': 1, 'm': 60, 'h': 3600}
            try:
                seconds = int(duration[:-1]) * time_map[duration[-1].lower()]
                if seconds > 21600:  # Max 6h
                    return await ctx.send("❌ Max 6 hours!")
                await target.edit(slowmode_delay=seconds)
                await ctx.send(f"⏳ {target.mention} slowmode: **{duration}**")
            except:
                await ctx.send("❌ Use: 30s, 1m, 5m, 1h, off")
        
        logger.info(f"{ctx.author} set slowmode {duration} on {target}")

async def setup(bot):
    await bot.add_cog(Slowmode(bot))
