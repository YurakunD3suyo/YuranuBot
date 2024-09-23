import sys
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Group
from discord import Interaction, Embed, Color
from modules.vc_speakers import find_spker, spk_choices
from modules.db_settings import get_server_setting, save_server_setting
from modules.exception import sendException

class Server( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    server = Group(name="server", description="サーバー関連のコマンドなのだ")

    @server.command(name="server-speaker", description="サーバーの読み上げ話者を設定するのだ")
    @app_commands.rename(id="話者")
    @app_commands.choices(id=spk_choices)
    async def yomiage_server_speaker(self, interact:Interaction,id:int):
        try:
            if interact.user.guild_permissions.administrator:
                read_type = "vc_speaker"
                result = save_server_setting(interact.guild.id, read_type, id)

                if result is None:
                    spker_name = find_spker(id=id)

                    if spker_name is not None:
                        await interact.response.send_message(f"サーバー話者を**{spker_name[0]}**に変更したのだ！")
                        return
                    
                await interact.response.send_message("エラーが発生したのだ...")
            else:
                await interact.response.send_message("このコマンドは管理者のみ実行できるのだ")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @server.command(name="speed", description="サーバーの読み上げ速度を変更するのだ")
    @app_commands.rename(speed="速度")
    @app_commands.describe(speed="0.5~2.0")
    async def yomiage_speed(self, interact: Interaction, speed: float):
        try:
            if speed >= 0.5 or speed <= 2.0:
                read_type = "speak_speed"
                result = save_server_setting(interact.guild.id, read_type, speed)
            else:
                interact.response.send_message(f"0.5~2.0の間で設定するのだ！")
                return

            if result is None:
                await interact.response.send_message(f"読み上げ速度を**「{speed}」**に変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @server.command(name="server-settings", description="サーバーの読み上げ設定を表示するのだ")
    async def check_yomi_settings(self, interact: Interaction):
        vc_channel = get_server_setting(interact.guild.id, "speak_channel")
        if vc_channel is None: vc_channel = "チャンネルが未設定"
        else: vc_channel = f"<#{vc_channel}>"

        spker_id = get_server_setting(interact.guild.id, "vc_speaker")
        spker_name = find_spker(id=spker_id)
        spker_name = spker_name[0]

        auto_conn_channel = get_server_setting(interact.guild.id, "auto_connect")
        if auto_conn_channel == 0 or auto_conn_channel is None: auto_conn_channel = "オフ"
        else: auto_conn_channel = f"<#{auto_conn_channel}>"

        vc_speak_speed = get_server_setting(interact.guild.id, "speak_speed")
        length_limit = get_server_setting(interact.guild.id, "length_limit")

        soundtextMode_ = get_server_setting(interact.guild.id, "soundtext_mode")
        if soundtextMode_ == 2: soundtextMode = "有効"
        elif soundtextMode_ == 1: soundtextMode = "ゲームモード"
        elif soundtextMode_ == 0: soundtextMode = "無効"
        else: soundtextMode = "設定取得時にエラー発生" 

        embed = Embed(
            title="サーバーの読み上げ設定を表示するのだ！",
            color=Color.green()
        )
        embed.add_field(
            name="読み上げるサーバー",
            value=f"> {vc_channel}",
            inline=False
        )
        embed.add_field(
            name="読み上げ話者",
            value=f"> {spker_name}",
            inline=False
        )
        embed.add_field(
            name="読み上げ速度",
            value=f"> {vc_speak_speed}",
            inline=False
        )
        embed.add_field(
            name="読み上げ文字制限",
            value=f"> {length_limit}文字",
            inline=False
        )
        embed.add_field(
            name="VCへの自動接続",
            value=f"> {auto_conn_channel}",
            inline=False
        )
        embed.add_field(
            name="サウンドテキスト機能",
            value=f"> {soundtextMode}"
        )
        embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

        await interact.response.send_message(embed=embed)  

    @server.command(name="length-limit", description="読み上げ文字数を制限するのだ")
    @app_commands.rename(limit="文字数")
    @app_commands.describe(limit="0: 制限を無効化")
    async def yomiage_speed(self, interact: Interaction, limit: int):
        try:
            read_type = "length_limit"
            result = save_server_setting(interact.guild.id, read_type, limit)

            if result is None:
                if limit == 0:
                    await interact.response.send_message(f"読み上げ制限を**「無効」**に変更したのだ！")
                else:
                    await interact.response.send_message(f"読み上げ制限を**「{limit}文字」**に変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)     

    @server.command(name="join-message", description="参加時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    async def change_vc_join_message(self, interact: Interaction, text: str):
        try:
            res = save_server_setting(interact.guild_id, "vc_join_message", text)
            if res is None:
                await interact.response.send_message("**参加時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
            
    @server.command(name="exit-message", description="退出時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    @app_commands.rename(text="文章")
    async def change_vc_exit_message(self, interact: Interaction, text: str):
        try:
            res = save_server_setting(interact.guild.id, "vc_exit_message", text)
            if res is None:
                await interact.response.send_message("**退出時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no) 

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot))
    