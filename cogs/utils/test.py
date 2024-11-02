import os
import sys
import dotenv
import logging
# import discord
import asyncio
import subprocess

from discord import app_commands, Object, Interaction, Embed, Color
from discord.ext import commands

class Test( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.url = "https://shohei.akikaki.net"

    async def translate(self, interact: Interaction):