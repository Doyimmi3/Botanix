import discord
from discord.ext import commands
import asyncio
import re
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("moderation.tempban")

class TempBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tempbans = {}

    def parse_duration(self, duration: str) -> tuple[int, str]:
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

    @commands.hybrid_command(name="tempban")
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def tempban(self, ctx, member: discord.Member, duration: str, *, reason="No reason provided"):
        """Temporarily ban a user. Usage: !tempban @user 1h Spam"""
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Cannot ban higher role!")

        seconds, unit = self.parse_duration(duration)
        
        await member.ban(reason=reason)
        self.tempbans.setdefault(ctx.guild.id, {})[member.id] = asyncio.get_event_loop().time() + seconds
        
        embed = discord.Embed(
            title="🔨 Temporary Ban",
            color=0xff0000,
            description=f"{member} temporarily banned for **{duration}** ({unit}).",
            fields=[
                ("👤 Target", member.display_name, True),
                ("👮 Moderator", ctx.author.display_name, True),
                ("📝 Reason", reason, False)
            ]
        )
        await ctx.send(embed=embed)
        
        # Unban after duration
        asyncio.create_task(self.unban_after(ctx.guild.id, member.id, seconds))
        
        if self.bot.db_ready:
            await Database.log_moderation(ctx.guild.id, "tempban", member.id, ctx.author.id, f"{duration} - {reason}")
        logger.info(f"{ctx.author} tempbanned {member} for {duration}")

    async def unban_after(self, guild_id: int, user_id: int, seconds: int):
        await asyncio.sleep(seconds)
        guild = self.bot.get_guild(guild_id)
        if guild:
            try:
                await guild.unban(discord.Object(id=user_id), reason="Temporary ban expired")
                logger.info(f"Auto-unbanned {user_id}")
            except:
                pass

async def setup(bot):
    await bot.add_cog(TempBan(bot))
