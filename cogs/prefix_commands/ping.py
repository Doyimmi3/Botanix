import discord
from discord.ext import commands
import time
from utils.logger import setup_logger

logger = setup_logger("ping")

class PingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", with_app_command=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
        """Shows bot latency and uptime."""
        start_time = time.time()
        
        if ctx.interaction:
            await ctx.interaction.response.defer()
        
        end_time = time.time()
        latency = round((end_time - start_time) * 1000)
        ws_latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(title="🏓 Pong!", color=0x00ff00)
        embed.add_field(name="🌐 Websocket", value=f"{ws_latency}ms", inline=True)
        embed.add_field(name="📡 API", value=f"{latency}ms", inline=True)
        embed.add_field(name="💓 Uptime", value=self.format_uptime(), inline=True)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        logger.info(f"Ping by {ctx.author.id}: WS={ws_latency}ms, API={latency}ms")
        
        if ctx.interaction:
            await ctx.interaction.followup.send(embed=embed)
        else:
            await ctx.send(embed=embed)

    def format_uptime(self):
        delta = time.time() - self.bot.start_time
        hours, remainder = divmod(int(delta), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

async def setup(bot):
    await bot.add_cog(PingCog(bot))
