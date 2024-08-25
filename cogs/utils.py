import discord
import time
import sys
import os
import platform

from discord.ext import commands, tasks
from discord import app_commands
from modules.pc_status import pc_status, PCStatus
from modules.db_settings import save_server_setting
from modules.exception import sendException
from modules.delete import delete_file_latency
from modules.yomiage_main import yomiage


class utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dashboard", description="ダッシュボードについてなのだ")
    async def dashboard(self, interact: discord.Interaction):
        await interact.response.send_message("ZundaCordのダッシュボード「ZunDash」\nhttps://bot.yuranu.net/")

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
    
    @app_commands.command(name="tts_announce")
    async def tts_announce(self, interact: discord.Interaction, content: str, id: str):
        is_owner = await self.bot.is_owner(interact.user)
        if is_owner != False:
            embed = discord.Embed(
                title="bot管理者のみ実行可能なのだ！",
                color=discord.Color.red()
            )
            await interact.response.send_message(embed=embed)
            return
        
        guild = self.bot.get_guild(int(id))

        if guild == None:
            embed = discord.Embed(
                title="サーバーが見つからなかったのだ！",
                description="サーバーにbotがいるかーとか確認してみて！",
                color=discord.Color.red()
            )
            await interact.response.send_message(embed=embed)
            return
    
        if guild.voice_client == None:
            embed = discord.Embed(
                title="ボイスに接続されていなかったのだ...",
                description="VCにbotがいるかーとか確認してみて！",
                color=discord.Color.red()
            )
            await interact.response.send_message(embed=embed)
            return
        
        await yomiage(content, guild)
            embed = discord.Embed(
                title="読み上げしたのだ！",
                description="アナウンスに成功しました！",
                color=discord.Color.green()
            )

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(utils(bot))