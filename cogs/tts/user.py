import sys
from modules.db_settings import get_user_setting
from modules.vc_speakers import find_spker
from discord import Embed, Color, Interaction, app_commands
from discord.ext import commands
from discord.app_commands import Group
from modules.vc_speakers import user_spk_choices
from modules.db_settings import save_user_setting
from modules.exception import sendException

class User(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    user = Group(name="user", description="ユーザー関連の設定なのだ")

    @user.command(name="speaker", description="ユーザーの読み上げ話者を設定するのだ(どのサーバーでも同期されるのだ)")
    @app_commands.rename(id="話者")
    @app_commands.choices(id=user_spk_choices)
    async def yomiage_user_speaker(self, interact:Interaction,id:int):
        try:
            read_type = "vc_speaker"
            result = save_user_setting(interact.user.id, read_type, id)

            if result is None:
                if id == 1:
                    await interact.response.send_message(f"ユーザー話者を**サーバー設定を使用**に変更したのだ！")
                else:
                    spker_name = find_spker(id=id)
                    await interact.response.send_message(f"ユーザー話者を**{spker_name[0]}**に変更したのだ！")
                    return
                
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @user.command(name="settings", description="ユーザーの読み上げ設定を表示するのだ")
    async def check_user_yomi_settings(self, interact: Interaction):
        # ユーザー設定の取得
        spk_id = get_user_setting(interact.user.id, "vc_speaker")
        #話者IDから名前を取得
        spk_info = find_spker(id=spk_id)
        #Noneの場合はエラー表示に
        if spk_id == -1:
            spk_name="サーバー設定を使用"
        elif spk_info is None:
            spk_name = "**話者検索時にエラーが発生**"
        else:
            spk_name = spk_info[0]
        
        user_speed = get_user_setting(interact.user.id, "speak_speed")
        if user_speed == 0: user_speed = "サーバー設定を使用"
        connect_msg = get_user_setting(interact.user.id, "conn_msg")
        if connect_msg == "nan": connect_msg = "デフォルト設定"
        disconnect_msg = get_user_setting(interact.user.id, "disconn_msg")
        if disconnect_msg == "nan": disconnect_msg = "デフォルト設定"
        
        # Embedに設定内容を表示
        embed = Embed(
            title="ユーザーの読み上げ設定を表示するのだ！",
            color=Color.green()
        )
        embed.add_field(
            name="読み上げ話者",
            value=f"> {spk_name}",
            inline=False
        )
        embed.add_field(
            name="読み上げ速度",
            value=f"> {user_speed}"
        )
        embed.add_field(
            name="接続メッセージ",
            value=f"> {connect_msg}",
            inline=False
        )
        embed.add_field(
            name="切断メッセージ",
            value=f"> {disconnect_msg}",
            inline=False
        )
        embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

        await interact.response.send_message(embed=embed)

    @user.command(name="speed", description="ユーザー読み上げ速度を変更するのだ")
    @app_commands.rename(speed="速度")
    @app_commands.describe(speed="0.5~2.0 (0: サーバー設定を使用する)")
    async def user_speed(self, interact: Interaction, speed: float):
        try:
            if speed >= 0.5 or speed <=2.0 or speed == 0:
                read_type = "speak_speed"
                result = save_user_setting(interact.user.id, read_type, speed)
            else:
                interact.response.send_message(f"0.5~2.0の間で設定するのだ！")
                return

            if result is None:
                if speed == 0:
                    await interact.response.send_message(f"ユーザー読み上げ速度を**サーバー読み上げ速度**に変更したのだ！")
                else:
                    await interact.response.send_message(f"ユーザー読み上げ速度を**「{speed}」**に変更したのだ！")

                return 
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @user.command(name="join-message", description="[ユーザー別]参加時の読み上げを設定するのだ！")
    @app_commands.rename(text="文章")
    @app_commands.describe(text="<user> : ユーザー名")
    async def change_user_join_message(self, interact: Interaction, text: str):
        try:
            res = save_user_setting(interact.user.id, "conn_msg", text)
            if res is None:
                await interact.response.send_message("**ユーザー別 参加時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @user.command(name="exit-message", description="[ユーザー別]退席時の読み上げを設定するのだ！")
    @app_commands.rename(text="文章")
    @app_commands.describe(text="<user>: ユーザー名")
    async def change_user_exit_message(self, interact: Interaction, text: str):
        try:
            res = save_user_setting(interact.user.id, "disconn_msg", text)
            if res is None:
                await interact.response.send_message("**ユーザー別 退出時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(User(bot))