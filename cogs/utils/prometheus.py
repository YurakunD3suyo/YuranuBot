import time
import os
import platform
from discord import app_commands, Status, CustomActivity, Embed, Color, Interaction, __version__ as discord_version
from discord.ext import commands, tasks

from modules import prometheus

class Prometheus( commands.Cog ):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    if self.bot.prometheus:   
        @tasks.loop(seconds=30)
        async def loops(self):
            guild_count = len(self.bot.guilds)
            user_count = sum(len(guild.members) for guild in self.bot.guilds)
            self.bot.metrics.set("tts_guilds", guild_count)
            self.bot.metrics.set("tts_users", user_count)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Prometheus(bot))
