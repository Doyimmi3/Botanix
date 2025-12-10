import discord
from discord.ext import commands
import time
import psutil
import os
from utils.logger import setup_logger

logger = setup_logger("status")

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_uptime(self):
        delta = time.time() - self.bot.process_start_time
        hours, remainder = divmod(int(delta), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    def get_memory_usage(self):
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            return f"{memory_mb:.1f} MB"
        except:
            return "N/A"

    @commands.hybrid_command(name="status")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def status(self, ctx):
        uptime = self.get_uptime()
        latency = round(self.bot.latency * 1000)
        memory = self.get_memory_usage()
        db_status = "🟢 Connected" if self.bot.db_ready else "🔴 Disabled"
        cmd_count = getattr(self.bot, 'command_count', 0)
        
        embed = discord.Embed(title="📊 Bot Status", color=0x00ff00)
        embed.add_field(name="🕐 Uptime", value=uptime, inline=True)
        embed.add_field(name="🏓 Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="📡 DB", value=db_status, inline=True)
        embed.add_field(name="👥 Guilds", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="📱 Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="⚙️ Commands", value=cmd_count, inline=True)
        embed.add_field(name="💾 Memory", value=memory, inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        logger.info(f"Status by {ctx.author.id}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Status(bot))
