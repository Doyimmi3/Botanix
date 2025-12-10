import discord
from discord.ext import commands
from collections import defaultdict, deque
import asyncio
from utils.logger import setup_logger

logger = setup_logger("automod")

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(lambda: deque(maxlen=10))  # Anti-spam
        self.spam_count = defaultdict(int)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Anti-spam (5+ mensagens em 10s)
        self.user_messages[message.author.id].append(message.created_at)
        recent_msgs = [m for m in self.user_messages[message.author.id] if 
                      (message.created_at - m).total_seconds() < 10]
        
        if len(recent_msgs) >= 5:
            await message.delete()
            embed = discord.Embed(
                title="🚫 Anti-Spam",
                description=f"{message.author.mention} spam detectado!",
                color=0xff0000
            )
            spam_msg = await message.channel.send(embed=embed)
            await asyncio.sleep(5)
            await spam_msg.delete()
            
            # Temp mute por spam
            mute_role = discord.utils.get(message.guild.roles, name="Muted")
            if mute_role:
                await message.author.add_roles(mute_role, reason="Auto-mute: Spam")
                logger.warning(f"Auto-muted {message.author} for spam")
        
        # Delete links/invites
        if any(word in message.content.lower() for word in ['discord.gg/', 'http']):
            await message.delete()
            logger.info(f"Deleted link from {message.author}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Anti-raid (10+ joins em 1min)
        # Implementar lógica aqui se necessário
        
        logger.info(f"New member: {member}")

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
