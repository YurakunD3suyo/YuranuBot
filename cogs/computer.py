import discord
import time
import sys
import os
import platform

from discord.ext import commands, tasks
from discord import app_commands
from modules.pc_status_cmd import pc_status, PCStatus
from modules.db_settings import save_server_setting
from modules.exception import sendException
from modules.delete import delete_file_latency

class Computer( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rpc_mode = 1
        if os.getenv("USE_RPC") == "True":
            self.rpc_loop.start()

    if os.getenv("USE_RPC") == "True":
        @tasks.loop(seconds=7)
        async def rpc_loop(self):

            pc = PCStatus

            if self.rpc_mode == 1:
                guild_count = len(self.bot.guilds)
                user_count = sum(len(guild.members) for guild in self.bot.guilds)

                status_message = f"{guild_count} Guilds | {user_count} Users"

            elif self.rpc_mode == 2:
                #Uptimeを計算するために時間を取得
                curr_time = time.time()
                #稼働時間を計算
                elapsed = curr_time - self.bot.start_time
                #時分秒に変換
                days, remainder = divmod(elapsed, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                status_message = f"Uptime: {int(days)}d {int(hours)}h {int(minutes)}m"

            elif self.rpc_mode == 3:
                pc = await pc_status()

                status_message = f"CPU: {pc.cpu_load}% | GPU: {pc.gpu_load}%"

            elif self.rpc_mode == 4:
                pc = await pc_status()

                status_message = f"RAM: {pc.ram_use}/{pc.ram_total}GB ({pc.ram_percent}%)"

            elif self.rpc_mode == 5:
                pc = await pc_status()

                status_message = f"GPUMem: {pc.gpu_mem_use}GB"
                self.rpc_mode = 0

            await self.bot.change_presence(activity=discord.Game(name=status_message)) 
            self.rpc_mode += 1

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        
        if message.author == self.bot.owner_id:
            prefix = await self.bot.get_prefix(message)
            if message.content == (f"{prefix}rpc stop"):
                self.rpc_loop.stop()
                await message.reply("✅ RPC Loop Stopped!")
            
            elif message.content == (f"{prefix}rpc start"):
                self.rpc_loop.start()
                await message.reply("✅ RPC Loop Started!")
    
    @app_commands.command(name="status",description="Botを稼働しているPCの状態を表示するのだ")#PCの状態
    async def status(self, interact: discord.Interaction):
        # PCの状態を取得
        pc = await pc_status()

        if self.bot.start_time is None:
            uptime = "計算時にエラー"
        else:
            #Uptimeを計算するために時間を取得
            curr_time = time.time()
            #稼働時間を計算
            elapsed = curr_time - self.bot.start_time
            #時分秒に変換
            days, remainder = divmod(elapsed, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            uptime = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

        py_version = platform.python_version()
        guild_count = len(self.bot.guilds)
        user_count = sum(len(guild.members) for guild in self.bot.guilds)

        embed = discord.Embed(
            title="サーバーの稼働状況なのだ！",
            color=discord.Color.green()
        )
        embed.add_field(name="> Bot Detail",
                        value=f"・{guild_count} Guilds  |  {user_count} Users\n"+
                              f"・Ping: {(self.bot.latency*1000):.1f}ms\n"+
                              f"・Python: Version{py_version}\n"+
                              f"・Discord.py: Version{discord.__version__}\n",
                        inline=False)
        
        embed.add_field(name="> Server Detail",
                        value=f"・OS: {pc.os_name}\n"+
                              f"・Uptime: {uptime}",
                        inline=False)
        
        embed.add_field(name=f"> CPU ({pc.cpu_name})",
                        value=f"・Usage: {pc.cpu_load}%\n"+
                              f"・Freq: {pc.cpu_freq}GHz",
                        inline=False)
        
        embed.add_field(name=f"> GPU ({pc.gpu_name})",
                        value=f"・Usage: {pc.gpu_load}%\n"+
                              f"・Mem: {pc.gpu_mem_use}GB",
                        inline=False)
        
        embed.add_field(name="> RAM",
                        value=f"・Usage: {pc.ram_use}GB\n"+
                              f"・Total: {pc.ram_total}GB\n"+
                              f"・Percent: {pc.ram_percent}%",
                        inline=False)
        embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)
        
        await interact.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Computer(bot))