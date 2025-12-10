import discord
from discord.ext import commands
from utils.logger import setup_logger

logger = setup_logger("verification")

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verified_role_name = "Verified"

    async def get_or_create_verified_role(self, guild):
        """Get or create verified role."""
        role = discord.utils.get(guild.roles, name=self.verified_role_name)
        if not role:
            role = await guild.create_role(
                name=self.verified_role_name,
                color=0x00ff00,
                reason="Auto-created verification role"
            )
            # Deny access to @everyone
            for channel in guild.channels:
                overwrite = discord.PermissionOverwrite(read_messages=False)
                await channel.set_permissions(guild.default_role, overwrite=overwrite)
                await channel.set_permissions(role, read_messages=True)
        return role

    @commands.hybrid_command(name="verify")
    @commands.has_permissions(manage_guild=True)
    async def verify(self, ctx):
        """Setup verification system."""
        verified_role = await self.get_or_create_verified_role(ctx.guild)
        
        embed = discord.Embed(
            title="🔐 Verification Required",
            description="React ✅ to verify and gain access to the server!",
            color=0x0099ff
        )
        embed.set_footer(text=f"Setup by {ctx.author}")
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        
        logger.info(f"Verification setup by {ctx.author} in {ctx.guild}")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Handle verification reactions."""
        if user.bot or str(reaction.emoji) != "✅":
            return
            
        message = reaction.message
        if message.embeds and "Verification Required" in message.embeds[0].title:
            guild = message.guild
            verified_role = discord.utils.get(guild.roles, name=self.verified_role_name)
            
            if verified_role and verified_role not in user.roles:
                await user.add_roles(verified_role, reason="User verified")
                logger.info(f"{user} verified in {guild}")

async def setup(bot):
    await bot.add_cog(Verification(bot))
