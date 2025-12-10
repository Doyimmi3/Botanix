import discord
from discord.ext import commands
from utils.prefixes import PrefixManager
from utils.logger import setup_logger

logger = setup_logger("prefix")

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="prefix")
    async def prefix(self, ctx):
        """Show current prefix."""
        current_prefix = await PrefixManager.get_prefix(ctx.guild.id)
        embed = discord.Embed(
            title="⚙️ Current Prefix",
            description=f"`{current_prefix}`\n\n**Use:** `{current_prefix}setprefix <new>`",
            color=0x0099ff
        )
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="setprefix")
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, *, new_prefix: str = "!"):
        """Change bot prefix. !setprefix ."""
        if len(new_prefix) > 5:
            return await ctx.send("❌ Max 5 characters!")
        
        success = await PrefixManager.set_prefix(ctx.guild.id, new_prefix)
        if success:
            embed = discord.Embed(
                title="✅ Prefix Updated",
                description=f"**New prefix:** `{new_prefix}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"{ctx.author} set prefix to '{new_prefix}' in {ctx.guild}")
        else:
            await ctx.send("❌ Database error!")

    @commands.hybrid_command(name="resetprefix")
    @commands.has_permissions(manage_guild=True)
    async def resetprefix(self, ctx):
        """Reset to default prefix (!)."""
        success = await PrefixManager.reset_prefix(ctx.guild.id)
        if success:
            embed = discord.Embed(
                title="✅ Prefix Reset",
                description="**Default prefix restored:** `!`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Database error!")

async def setup(bot):
    await bot.add_cog(Prefix(bot))
