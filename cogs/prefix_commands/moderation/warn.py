import discord
from discord.ext import commands
from utils.logger import setup_logger
from utils.db import Database
from typing import Dict

logger = setup_logger("moderation.warn")

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Warn a member."""
        warning = await Database.safe_add_warning(ctx.guild.id, member.id, reason, ctx.author.id)
        
        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=0xffff00,
            description=f"{member.mention} has been warned.",
            fields=[
                ("📝 Reason", reason, False),
                ("🆔 Warning ID", warning["warning_id"], True),
                ("📊 Total Warnings", str(len(await Database.safe_get_warnings(ctx.guild.id, member.id))), True)
            ]
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} warned {member} (ID: {warning['warning_id']})")

    @commands.hybrid_command(name="warnings")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member = None):
        """Show member's warnings."""
        target = member or ctx.author
        warns = await Database.safe_get_warnings(ctx.guild.id, target.id)
        
        embed = discord.Embed(
            title=f"📋 {target.display_name}'s Warnings",
            color=0x0099ff
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        if warns:
            warn_count = len(warns)
            embed.description = f"**Total: {warn_count} warnings**"
            for warn in warns[-5:]:  # Last 5 warnings
                embed.add_field(
                    name=f"🆔 {warn.get('warning_id', 'N/A')}",
                    value=f"**Reason:** {warn.get('reason', 'N/A')[:50]}...\n**By:** <@{warn.get('moderator_id', 0)}>\n**Date:** {warn.get('timestamp', 'N/A')}",
                    inline=False
                )
        else:
            embed.description = "✅ No warnings found."
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Warn(bot))
