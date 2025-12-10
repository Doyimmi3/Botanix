import discord
from discord.ext import commands
import asyncio
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("moderation.kick")

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a member from the server."""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ You cannot kick someone with equal or higher role!")
        
        await member.kick(reason=reason)
        
        embed = discord.Embed(
            title="👢 Member Kicked",
            color=0xffa500,
            description=f"{member.mention} was kicked from the server.",
            fields=[("👤 Target", member.display_name, True), ("👮 Moderator", ctx.author.display_name, True), ("📝 Reason", reason, False)]
        )
        await ctx.send(embed=embed)
        
        if self.bot.db_ready:
            await Database.log_moderation(ctx.guild.id, "kick", member.id, ctx.author.id, reason)
        
        logger.info(f"{ctx.author} kicked {member} ({reason})")

async def setup(bot):
    await bot.add_cog(Kick(bot))
