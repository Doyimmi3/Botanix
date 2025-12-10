import discord
from discord.ext import commands
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("moderation.ban")

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a member from the server."""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ You cannot ban someone with equal or higher role!")
        
        await member.ban(reason=reason)
        
        embed = discord.Embed(
            title="🔨 Member Banned",
            color=0xff0000,
            description=f"{member.mention} was banned from the server.",
            fields=[("👤 Target", member.display_name, True), ("👮 Moderator", ctx.author.display_name, True), ("📝 Reason", reason, False)]
        )
        await ctx.send(embed=embed)
        
        if self.bot.db_ready:
            await Database.log_moderation(ctx.guild.id, "ban", member.id, ctx.author.id, reason)
        
        logger.info(f"{ctx.author} banned {member} ({reason})")

    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason="No reason provided"):
        """Unban a user by ID."""
        user = discord.Object(id=user_id)
        try:
            await ctx.guild.unban(user, reason=reason)
            await ctx.send(f"✅ {user_id} was unbanned!")
            logger.info(f"{ctx.author} unbanned {user_id}")
        except discord.NotFound:
            await ctx.send("❌ User not found in ban list!")

async def setup(bot):
    await bot.add_cog(Ban(bot))
