import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger("moderation.lock")

class LockUnlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="lock")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
        """Lock a channel. !lock #canal or !lock"""
        channel = channel or ctx.channel
        
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{channel.mention} foi bloqueado.",
            color=0xff0000,
            fields=[("📝 Reason", reason, False)]
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} locked {channel} - {reason}")

    @commands.hybrid_command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
        """Unlock a channel."""
        channel = channel or ctx.channel
        
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = None
        
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=reason)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{channel.mention} foi liberado.",
            color=0x00ff00,
            fields=[("📝 Reason", reason, False)]
        )
        await ctx.send(embed=embed)
        logger.info(f"{ctx.author} unlocked {channel}")

async def setup(bot):
    await bot.add_cog(LockUnlock(bot))
