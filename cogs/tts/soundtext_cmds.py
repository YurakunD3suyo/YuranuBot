from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color, Attachment

import sys
import os

from modules.yomiage_main import yomiage, queue_yomiage, sound_effects
# from modules.vc_events import vc_inout_process
from modules.db_settings import db_load, db_init, get_server_setting, get_user_setting, save_server_setting, save_user_setting
from modules.exception import sendException, exception_init
from modules.db_vc_dictionary import dictionary_load, delete_dictionary, save_dictionary, get_dictionary
from modules import pages as Page

class SoundTextCommands( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    st = app_commands.Group(name="soundtext", description="サウンドテキスト関連の設定なのだ")

    @st.command(name="add", description="サウンドテキストを追加するのだ")
    async def soundtext_add(self, interact: Interaction, file: Attachment):
        # サーバーID別でフォルダを管理
        save_dir = f"./sounds/{interact.guild.id}"

        # フォルダが存在しない場合は作成
        if (not os.path.isdir(save_dir)):
            os.mkdir(save_dir)

        # test
        print(file)

        await interact.response.send_message("ファイルを保存しました")

    @st.command(name="list", description="サーバー辞書の単語を表示するのだ")
    async def soundboard_list(self, interact: Interaction):
        try:
            result = sound_effects
            if result:
                embeds = []
                embed = Embed(
                    title="これを使ってみるのだ！",
                    description="使用できるサウンドテキストの一覧です。",
                    color=Color.green()
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)
                
                for i in range(len(result)):
                    embed.add_field(
                        name=f"サウンドテキスト{i+1}",
                        value=f"{result[i][0]}"
                    )

                    if (i+1) % 10 == 0:  # Create a new embed every 10 words
                        embeds.append(embed)
                        embed = Embed(
                            title="これを使ってみるのだ！",
                            description="使用できるサウンドテキストの一覧です。",
                            color=Color.green()
                        )
                        embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                if len(embed.fields) > 0:  # Add the last embed if there are remaining fields
                    embeds.append(embed)

                await Page.Simple().start(interact, pages=embeds)
                return
            else:
                await interact.response.send_message("登録されている単語はないのだ...")
                return

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @st.command(name="mode", description="サウンドテキスト機能を変更するのだ")
    @app_commands.rename(mode="モード")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="有効", value=2),
            app_commands.Choice(name="ゲームモード",value=1),
            app_commands.Choice(name="無効",value=0)
        ]
    )
    async def soundtext_mode(self, interact: Interaction, mode: int):
        try:
            result = save_server_setting(interact.guild_id, "soundtext_mode", mode)
            if result is None:
                mode_str: str = None

                if mode == 2:
                    mode_str = "有効"
                elif mode == 1:
                    mode_str = "ゲームモード"
                else:
                    mode_str = "無効"
                    
                await interact.response.send_message(f"サウンドテキスト機能を**「{mode_str}」**にしたのだ！")
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SoundTextCommands(bot))