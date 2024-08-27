import emoji
import sys

from discord.ext import commands, tasks
from discord import app_commands, Interaction, Message, Embed, Color
from modules.pc_status import pc_status, PCStatus
from modules.db_settings import save_server_setting
from modules.exception import sendException
from modules.delete import delete_file_latency
from modules.yomiage_main import yomiage


class utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="dashboard", description="ダッシュボードについてなのだ")
    async def dashboard(self, interact: Interaction):
        await interact.response.send_message("ZundaCordのダッシュボード「ZunDash」\nhttps://bot.yuranu.net/")

    @app_commands.command(name="serv-join-message", description="サーバー参加者へメッセージを送信するチャンネルを設定するのだ！")
    @app_commands.rename(activate="メッセージ送信のオンオフ")
    @app_commands.describe(activate="メッセージを送信する？(コマンドを実行した場所が送信場所になるのだ)")
    @app_commands.choices(
        activate=[
            app_commands.Choice(name="送信する",value=1),
            app_commands.Choice(name="送信しない",value=0)
        ])
    async def serv_join_message(self, interact: Interaction, activate: int):
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

        # コンテキストメニューの実装
        self.message_content_viewer = app_commands.ContextMenu(name="装飾前の本文確認", callback=self.show_content)
        async def show_content(interact: Interaction, message: Message):
            embed = Embed(
                color=Color.green(),
                title="メッセージは全部お見通しなのだ！",
                description=f"```{message.content}```"
            )
            await interact.response.send_message(embed=embed)
        self.bot.tree.add_command(self.message_content_viewer)


        self.message_content_viewer_demojised = app_commands.ContextMenu(name="装飾前の本文確認(絵文字変換後)", callback=self.show_content_demojised)
        
        async def show_content_demojised(interact: Interaction, message: Message):
            content = emoji.demojize(message.content)
            embed = Embed(
                color=Color.green(),
                title="メッセージは全部お見通しなのだ！",
                description=f"```{content}```"
            )
            await interact.response.send_message(embed=embed)
        self.bot.add_command(self.message_content_viewer_demojised)

    
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(utils(bot))