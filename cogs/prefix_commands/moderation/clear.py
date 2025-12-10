import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger("moderation.clear")

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10):
        """Delete messages. !clear 50"""
        if amount > 100:
            return await ctx.send("❌ Max 100 messages!", delete_after=5)
        
        # ✅ FIX: Defer + respond fast
        await ctx.defer()
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title="🧹 Messages Deleted",
            description=f"**{len(deleted)-1}** messages cleared.",
            color=0x00ff00
        )
        msg = await ctx.followup.send(embed=embed, ephemeral=True)
        await msg.delete(delay=3)
        
        logger.info(f"{ctx.author} cleared {len(deleted)-1} messages")

async def setup(bot):
    await bot.add_cog(Clear(bot))
