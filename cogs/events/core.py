import discord
from discord.ext import commands
import time
from utils.logger import setup_logger

logger = setup_logger("events.core")

class CoreEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.process_start_time = time.time()
    
    @commands.Cog.listener()
    async def on_ready(self):
        uptime = time.time() - self.process_start_time
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.bot.guilds)} servers"
        )
        await self.bot.change_presence(activity=activity)
        
        logger.info(
            f"🤖 Bot online as {self.bot.user} "
            f"(ID: {self.bot.user.id}) | "
            f"{len(self.bot.guilds)} guilds | "
            f"Uptime: {uptime:.1f}s"
        )
        self.bot.start_time = time.time()
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        logger = setup_logger("command_error")
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
            logger.warning(f"MissingPermissions: {ctx.author} in {ctx.guild}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ `{error.param.name}` argument is required!")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Command on cooldown. Try again in {error.retry_after:.1f}s")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("❌ This command cannot be used in DMs!")
        else:
            logger.error(f"Unexpected error: {error}", exc_info=True)
            await ctx.send("❌ An unexpected error occurred!")

async def setup(bot):
    await bot.add_cog(CoreEvents(bot))
