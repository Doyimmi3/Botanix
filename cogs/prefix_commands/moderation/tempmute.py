import discord
from discord.ext import commands
import asyncio
import re
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("moderation.tempmute")

class TempMute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tempmutes = {}  # Cache: guild_id -> {user_id: expire_time}

    def parse_duration(self, duration: str) -> tuple[int, str]:
        """Parse '1h', '30m', '2d' -> (seconds, unit)"""
        pattern = r'(\d+)([smhd])'
        match = re.match(pattern, duration.lower())
        if not match:
            raise commands.BadArgument("Use: 1s, 5m, 1h, 2d")
        
        amount, unit = match.groups()
        amount = int(amount)
        if unit == 's': return amount, 'seconds'
        if unit == 'm': return amount * 60, 'minutes'
        if unit == 'h': return amount * 3600, 'hours'
        if unit == 'd': return amount * 86400, 'days'

    async def create_mute_role(self, guild: discord.Guild) -> discord.Role:
        """Create or get mute role."""
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await guild.create_role(
                name="Muted",
                reason="Auto-created for temporary mutes",
                permissions=discord.Permissions(send_messages=False)
            )
            for channel in guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)
        return mute_role

    @commands.hybrid_command(name="tempmute")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def tempmute(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        """Temporarily mute a user. Usage: !tempmute @user 1h Spam"""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Cannot mute higher role!")

        seconds, unit = self.parse_duration(duration)
        mute_role = await self.create_mute_role(ctx.guild)
        
        await member.add_roles(mute_role, reason=reason)
        self.tempmutes.setdefault(ctx.guild.id, {})[member.id] = asyncio.get_event_loop().time() + seconds
        
        embed = discord.Embed(
            title="🔇 Temporarily Muted",
            color=0xffa500,
            description=f"{member.mention} muted for **{duration}** ({unit}).",
            fields=[
                ("👤 Target", member.display_name, True),
                ("👮 Moderator", ctx.author.display_name, True),
                ("📝 Reason", reason, False)
            ]
        )
        await ctx.send(embed=embed)
        
        # Remove mute after duration
        asyncio.create_task(self.remove_mute_after(ctx.guild.id, member.id, seconds))
        
        if self.bot.db_ready:
            await Database.log_moderation(ctx.guild.id, "tempmute", member.id, ctx.author.id, f"{duration} - {reason}")
        logger.info(f"{ctx.author} tempmuted {member} for {duration}")

    async def remove_mute_after(self, guild_id: int, user_id: int, seconds: int):
        await asyncio.sleep(seconds)
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return
            
        member = guild.get_member(user_id)
        if not member:
            return
            
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role, reason="Temporary mute expired")
            logger.info(f"Auto-unmuted {member}")

async def setup(bot):
    await bot.add_cog(TempMute(bot))
