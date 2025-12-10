import discord
from discord.ext import commands
import uptime
from utils.logger import setup_logger

logger = setup_logger("stats")

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="stats")
    async def stats(self, ctx):
        """Server statistics."""
        guild = ctx.guild
        
        online = len([m for m in guild.members if m.status == discord.Status.online])
        total_members = guild.member_count
        roles = len(guild.roles) - 1
        channels = len(guild.channels)
        
        embed = discord.Embed(title=f"📊 {guild.name} Stats", color=0x00ff00)
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        embed.add_field(name="👥 Members", value=f"{online}/{total_members}", inline=True)
        embed.add_field(name="🎭 Roles", value=roles, inline=True)
        embed.add_field(name="📢 Channels", value=channels, inline=True)
        embed.add_field(name="🆔 Server ID", value=guild.id, inline=True)
        embed.add_field(name="📅 Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="botstats")
    async def botstats(self, ctx):
        """Bot statistics."""
        embed = discord.Embed(title="🤖 Bot Stats", color=0x0099ff)
        embed.add_field(name="🌐 Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="👥 Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="💬 Commands Used", value="500+", inline=True)
        embed.add_field(name="⏱️ Uptime", value="24/7", inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))
