import asyncio
import json
import os
import time
import discord
import logging
from discord.ext import commands
from utils.db import Database
from utils.prefixes import PrefixManager

# Logging simples
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger("bot")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class ProductionBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        self.process_start_time = time.time()
        self.config = {}
        
    async def get_prefix(self, bot, message):
        if not message.guild:
            return commands.when_mentioned_or("!")(bot, message)
        prefix = await PrefixManager.get_prefix(message.guild.id)
        return commands.when_mentioned_or(prefix)(bot, message)
    
    async def load_config(self):
        with open("config.json", "r") as f:
            self.config = json.load(f)
        mongodb_uri = self.config.get("mongodb_uri", "").strip()
        if mongodb_uri:
            await Database.init(mongodb_uri)
        logger.info("⚙️ Config loaded")
    
    async def load_cogs(self):
        """🔥 CORRIGIDO: Carrega TODOS cogs dinamicamente"""
        # Lista MANUAL de TODOS os seus cogs
        cog_paths = [
            "cogs.prefix_commands.ping",
            "cogs.prefix_commands.status",
            "cogs.prefix_commands.moderation.kick",
            "cogs.prefix_commands.moderation.ban",
            "cogs.prefix_commands.moderation.warn",
            "cogs.prefix_commands.moderation.clear",
            "cogs.prefix_commands.moderation.tempmute",
            "cogs.prefix_commands.moderation.tempban",
            "cogs.prefix_commands.moderation.lock",
            "cogs.prefix_commands.moderation.timeout",
            "cogs.prefix_commands.utilities",
            "cogs.prefix_commands.verification",
            "cogs.prefix_commands.slowmode",
            "cogs.prefix_commands.roles",
            "cogs.prefix_commands.stats",
            "cogs.events.core",
            "cogs.events.automod"
        ]
        
        loaded = 0
        for cog_path in cog_paths:
            try:
                await self.load_extension(cog_path)
                logger.info(f"✅ {cog_path}")
                loaded += 1
            except Exception as e:
                logger.warning(f"⚠️ Skip {cog_path}: {str(e)[:50]}...")
        
        logger.info(f"📦 {loaded}/{len(cog_paths)} cogs carregados!")
    
    async def setup_hook(self):
        await self.tree.sync()
        logger.info("🔄 Slash commands synced")

async def main():
    bot = ProductionBot()
    await bot.load_config()
    await bot.load_cogs()
    try:
        await bot.start(bot.config["token"])
    finally:
        await Database.close()
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
