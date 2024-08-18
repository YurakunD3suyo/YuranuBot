import subprocess
import discord
import time
import sys
import os
import platform

from discord.ext import commands
from discord import app_commands
from modules.pc_status_cmd import pc_status
from modules.db_settings import save_server_setting
from modules.exception import sendException
from modules.delete import delete_file_latency

class utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sbc",description="Shizen Black Companyの説明資料なのだ")#Shizen Black Companyの宣伝
    async def sbc_command(self, interact:discord.Interaction):
        await interact.response.send_message('**～ドライバーの腕が生かせる最高職場～　Shizen Black Company** https://black.shizen.lol')

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
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)

            uptime = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

        embed = discord.Embed(
            title="サーバーの稼働状況なのだ！",
            color=discord.Color.green()
        )
        embed.add_field(name="Server Detail",
                        value=f"・OS: {pc.os_name}\n"+
                              f"・Uptime: {uptime}")
        
        embed.add_field(name=f"> CPU ({pc.cpu_name})",
                        value=f"・Usage: {pc.cpu_load}%\n"+
                              f"・Freq: {pc.cpu_freq}GHz",
                        inline=False)
        
        embed.add_field(name=f"> GPU ({pc.gpu_name})",
                        value=f"・Usage: {pc.gpu_load}%\n"+
                              f"・Mem: {pc.gpu_mem_use}MB",
                        inline=False)
        
        embed.add_field(name="> RAM",
                        value=f"・Usage: {pc.ram_use}GB\n"+
                              f"・Total: {pc.ram_total}GB\n"+
                              f"({pc.ram_percent}%)",
                        inline=False)
        
        await interact.response.send_message(embed=embed)

    @app_commands.command(name="serv-join-message", description="サーバー参加者へメッセージを送信するチャンネルを設定するのだ！")
    @app_commands.rename(activate="メッセージ送信のオンオフ")
    @app_commands.describe(activate="メッセージを送信する？(コマンドを実行した場所が送信場所になるのだ)")
    @app_commands.choices(
        activate=[
            discord.app_commands.Choice(name="送信する",value=1),
            discord.app_commands.Choice(name="送信しない",value=0)
        ])
    async def serv_join_message(self, interact: discord.Interaction, activate: int):
        try:
            ##管理者のみ実行可能
            if interact.user.guild_permissions.administrator:
                channel = interact.channel
                read_type = "welcome_server"

                if activate == 1:
                    result = save_server_setting(interact.guild.id, read_type, channel.id)
                    if result is None:
                        await interact.response.send_message(f"**<#{channel.id}>に参加メッセージを設定したのだ！**")
                        return
                    
                elif activate == 0:
                    result = save_server_setting(interact.guild.id, read_type, 0)
                    if result is None:
                        await interact.response.send_message(f"**参加メッセージ機能を使わないのだ！**")
                        return
                
                await interact.response.send_message("エラーが発生したのだ...")
                return
            
            await interact.response.send_message("このコマンドは管理者のみ実行できるのだ！")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(utils(bot))