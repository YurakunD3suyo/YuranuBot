import time
import os
import platform

from discord import app_commands, Status, CustomActivity, Embed, Color, Interaction, __version__ as discord_version
from discord.ext import commands, tasks

from modules.computer import pc_status, PCStatus


class Computer( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.rpc_mode = 1
        if os.getenv("USE_RPC") == "True":
            self.rpc_loop.start()

    if os.getenv("USE_RPC") == "True":
        @tasks.loop(seconds=10)
        async def rpc_loop(self):

            pc = PCStatus()
            activity_message = None
            status = None

            if self.rpc_mode == 1:
                guild_count = len(self.bot.guilds)
                user_count = sum(len(guild.members) for guild in self.bot.guilds)

                activity_message = f"{guild_count} Guilds | {user_count} Users"
                status = Status.online

            elif self.rpc_mode == 2:
                #Uptimeを計算するために時間を取得
                curr_time = time.time()
                #稼働時間を計算
                elapsed = curr_time - self.bot.start_time
                #時分秒に変換
                days, remainder = divmod(elapsed, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)

                activity_message = f"起動時間: {int(days)}日 {int(hours)}時間 {int(minutes)}分"
                status = Status.online
            
            elif self.rpc_mode == 3:
                pc = await pc_status()

                if pc.cpu_load >= 90 or pc.gpu_load >= 90 or pc.gpu_mem_percent >= 90 or pc.ram_percent >= 90:
                    activity_message = "⚠リソース使用率: 高"
                    status = Status.dnd
                elif pc.cpu_load >= 70 or pc.gpu_load >= 70 or pc.gpu_mem_percent >= 70 or pc.ram_percent >= 70:
                    activity_message = "リソース使用率: 中"
                    status = Status.idle
                else:
                    activity_message = "リソース使用率: 低"
                    status = Status.online
            
            elif self.rpc_mode == 4:
                activity_message = "More at bot.yuranu.net"

                self.rpc_mode = 0
            
            await self.bot.change_presence(status=status, activity=CustomActivity(name=activity_message)) 

            self.rpc_mode += 1

    @commands.command()
    async def rpc_stop(self, ctx: commands.Context):
        if ctx.author.bot:
            return

        if await self.bot.is_owner(ctx.author):
            self.rpc_loop.stop()
            await ctx.reply("✅ RPC Loop Stopped!")
            
    @commands.command()
    async def rpc_start(self, ctx: commands.Context):
        if ctx.author.bot:
            return

        if await self.bot.is_owner(ctx.author):
            self.rpc_loop.start()
            await ctx.reply("✅ RPC Loop Started!")
    
    @app_commands.command(name="status",description="Botを稼働しているPCの状態を表示するのだ")#PCの状態
    async def status(self, interact: Interaction):
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

        embed = Embed(
            title="サーバーの稼働状況なのだ！",
            color=Color.green()
        )
        embed.add_field(name="> Bot Detail",
                        value=f"・{guild_count} Guilds  |  {user_count} Users\n"+
                              f"・Ping: {(self.bot.latency*1000):.1f}ms\n"+
                              f"・Python: Version{py_version}\n"+
                              f"・Discord.py: Version{discord_version}\n",
                        inline=False)
        
        embed.add_field(name="> Server Detail",
                        value=f"・OS: {pc.os_name}\n"+
                              f"・Uptime: {uptime}",
                        inline=False)
        
        embed.add_field(name=f"> CPU ({pc.cpu_name})",
                        value=f"・Usage: {pc.cpu_load:.1f}%\n"+
                              f"・Freq: {pc.cpu_freq:.2f}GHz",
                        inline=False)
        
        embed.add_field(name=f"> GPU ({pc.gpu_name})",
                        value=f"・Core Usage: {pc.gpu_load:.1f}%\n"+
                              f"・Mem Used: {pc.gpu_mem_use:.2f}GB\n"+
                              f"・Mem Total: {pc.gpu_mem_total:.2f}GB\n"+
                              f"・Mem Usage: {pc.gpu_mem_percent:.1f}%",
                        inline=False)
        
        embed.add_field(name="> RAM",
                        value=f"・Used: {pc.ram_use:.2f}GB\n"+
                              f"・Total: {pc.ram_total:.2f}GB\n"+
                              f"・Usage: {pc.ram_percent:.1f}%",
                        inline=False)
        embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)
        
        await interact.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Computer(bot))