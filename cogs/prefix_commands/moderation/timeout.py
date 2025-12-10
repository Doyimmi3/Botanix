import discord
from discord.ext import commands
import re
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("moderation.timeout")

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_duration(self, duration: str):
        pattern = r'(\d+)([smhd])'
        match = re.match(pattern, duration.lower())
        if not match:
            raise commands.BadArgument("Use: 1s, 5m, 1h, 2d")
        amount, unit = match.groups()
        amount = int(amount)
        if unit == 's': return amount
        if unit == 'm': return amount * 60
        if unit == 'h': return amount * 3600
        if unit == 'd': return amount * 86400

    @commands.hybrid_command(name="timeout")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        """Timeout a member."""
        seconds = self.parse_duration(duration)
        if seconds > 2419200:  # 28 days max
            return await ctx.send("❌ Max 28 days!")
            
        await member.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=reason)
        
        embed = discord.Embed(
            title="⏰ Member Timed Out",
            color=0xffaa00,
            description=f"{member.mention} timed out for **{duration}**.",
            fields=[("📝 Reason", reason, False)]
        )
        await ctx.send(embed=embed)
        
        await Database.safe_log_moderation(ctx.guild.id, "timeout", member.id, ctx.author.id, reason)
        logger.info(f"{ctx.author} timed out {member} for {duration}")

    @commands.hybrid_command(name="untimeout")
    @commands.has_permissions(moderate_members=True)
    @commands.bot_has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        """Remove timeout from member."""
        await member.timeout(None, reason="Timeout removed")
        
        embed = discord.Embed(
            title="✅ Timeout Removed",
            description=f"{member.mention}'s timeout has been removed.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} removed timeout from {member}")

async def setup(bot):
    await bot.add_cog(Timeout(bot))
