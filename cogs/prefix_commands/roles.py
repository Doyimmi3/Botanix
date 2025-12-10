import discord
from discord.ext import commands
from utils.logger import setup_logger
from utils.db import Database

logger = setup_logger("roles")

class RolePanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="rolepanel")
    @commands.has_permissions(manage_roles=True)
    async def rolepanel(self, ctx, *, role_list: str):
        """Create role panel. !rolepanel 1:Designer 2:Developer 3:Gamer"""
        # Parse role list
        parts = role_list.split()
        if len(parts) > 20:
            return await ctx.send("❌ Max 20 roles!")
        
        embed = discord.Embed(
            title="🎭 Role Selection",
            description="**React with numbers to get roles:**\n" + 
                       "\n".join([f"{i+1}: {part}" for i, part in enumerate(parts)]),
            color=0x0099ff
        )
        msg = await ctx.send(embed=embed)
        
        # Add numbered Unicode emojis ONLY
        for i in range(min(len(parts), 20)):
            emoji = str(i + 1) + "️⃣"  # 1️⃣ 2️⃣ 3️⃣
            await msg.add_reaction(emoji)
        
        # ✅ FIXED: SAFE Database - NO truth testing
        collection = Database.collection("role_panels")
        if collection is not None:  # ✅ EXPLICIT None check
            try:
                await collection.insert_one({
                    "guild_id": ctx.guild.id,
                    "message_id": msg.id,
                    "roles": dict(zip([str(i+1)+"️⃣" for i in range(len(parts))], parts))
                })
            except Exception as e:
                logger.error(f"Role panel DB save error: {e}")
        
        await ctx.send(f"✅ Role panel created! {len(parts)} roles added.")
        logger.info(f"Role panel by {ctx.author}: {len(parts)} roles")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
            
        # ✅ FIXED: SAFE Database check
        collection = Database.collection("role_panels")
        if collection is None:  # ✅ EXPLICIT None check
            return
            
        try:
            panel = await collection.find_one({"message_id": reaction.message.id})
            if not panel:
                return
                
            guild = reaction.message.guild
            emoji = str(reaction.emoji)
            
            if emoji in panel["roles"]:
                role_name = panel["roles"][emoji]
                role = discord.utils.get(guild.roles, name=role_name)
                
                if role:
                    if role not in user.roles:
                        await user.add_roles(role, reason="Role panel")
                        action = "got"
                    else:
                        await user.remove_roles(role, reason="Role panel")
                        action = "removed"
                        
                    try:
                        await reaction.message.channel.send(
                            f"{user.mention} {action} **{role_name}** role!",
                            delete_after=5
                        )
                    except:
                        pass
        except Exception as e:
            logger.error(f"Reaction role error: {e}")

async def setup(bot):
    await bot.add_cog(RolePanel(bot))
