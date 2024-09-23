from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color, File, TextChannel
from discord.app_commands import Choice

import sys
import logging
import random
from modules.vc_speakers import spk_choices, user_spk_choices, find_spker

from modules.vc_messages import conn_message, zunda_conn_message
from modules.yomiage_main import yomiage
from modules.db_settings import get_server_setting, get_user_setting, save_server_setting, save_user_setting
from modules.exception import sendException
from modules.db_vc_dictionary import delete_dictionary, save_dictionary, get_dictionary
from modules import pages as Page


class yomiage_cmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    yomi = app_commands.Group(name="yomiage", description="読み上げ関連のコマンドを実行するのだ")
        
    
    @app_commands.command(name="vc-start", description="ユーザーが接続しているボイスチャットに接続するのだ")
    async def vc_command(self, interact: Interaction):
        try:
            if (interact.user.voice is None):
                await interact.response.send_message("ボイスチャンネルに接続していないのだ...")
                return
            if (interact.guild.voice_client is not None):
                await interact.response.send_message("すでにほかのボイスチャンネルにつながっているのだ...")
                return
            
            await interact.user.voice.channel.connect()

            ##接続を知らせるメッセージを送信
            channel = get_server_setting(interact.guild_id, "speak_channel")
            if channel is None: channel = "**チャンネルが未設定です**"
            else: channel = f"<#{channel}>"
            length_limit = get_server_setting(interact.guild_id, "length_limit")
            yomiage_speed = get_server_setting(interact.guild_id, "speak_speed")

            if length_limit == 0:
                length_limit = f"!!文字数制限なし!!"
            else:
                length_limit = f"{length_limit}文字"
        
            embed = Embed(
                title="接続したのだ！",
                description="ボイスチャンネルに参加しました！",
                color=Color.green()
            )
            embed.add_field(
                name="読み上げるチャンネル",
                value=f"> {channel}",
                inline=False
            )
            embed.add_field(
                name="読み上げ文字数の制限",
                value=f"> {length_limit}",
                inline=False
            )
            embed.add_field(
                name="読み上げスピード",
                value=f"> {yomiage_speed}",
                inline=False
            )
            embed.add_field(
                name="**VOICEVOXを使用しています!**",
                value="**[VOICEVOX、音声キャラクターの利用規約](<https://voicevox.hiroshiba.jp/>)を閲覧のうえ、正しく使うのだ！**",
                inline=False
            )
            file = File(R"images\boticon_zunda.png", filename="boticon_zunda.png")
            embed.set_thumbnail(url=f"attachment://boticon_zunda.png")
            embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

            await interact.response.send_message(embed=embed, file=file)

            ##読み上げるチャンネルが存在しない場合に警告文を送信

            if (channel is None):
                embed = Embed(
                    color=Color.red(),
                    title="読み上げるチャンネルがわからないのだ...",
                    description="読み上げを開始するには読み上げるチャンネルを設定してください！"
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                await interact.channel.send(embed=embed)

            ##参加時の読み上げ
            spkID = get_server_setting(interact.guild.id, "vc_speaker")
            # もしずんだもんならずんだもん専用の接続メッセージを使用
            if spkID == 3:
                mess = random.choice(zunda_conn_message)
            else:
                mess = random.choice(conn_message)
            await yomiage(mess, interact.guild)

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="channel", description="読み上げるチャンネルを変更するのだ")
    @app_commands.rename(channel="読み上げるチャンネル")
    async def yomiage_channel(self, interact: Interaction, channel: TextChannel):
        try:
            result = save_server_setting(interact.guild_id, "speak_channel", channel.id)
            if result is None:
                await interact.response.send_message(f"☑**「<#{channel.id}>」**を読み上げるのだ！")
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
        
    
    @yomi.command(name="user-announce", description="ユーザーの入退出を読み上げするのだ")
    @app_commands.rename(activate="有効無効")
    @app_commands.choices(
        activate=[
            Choice(name="有効(ユーザー別有効)", value=2),
            Choice(name="有効(ユーザー別無効)",value=1),
            Choice(name="アナウンス無効",value=0)
        ]
    )
    async def yomiage_channel(self, interact: Interaction, activate: int):
        try:
            result = save_server_setting(interact.guild_id, "vc_user_announce", activate)

            if result is None:
                if activate == 0:
                    await interact.response.send_message(f"ユーザーの入退出読み上げを**「無効」**にしたのだ！")
                elif activate == 1:
                    await interact.response.send_message(f"ユーザーの入退出読み上げを**「有効(ユーザー別無効)」**にしたのだ！")
                elif activate == 2:
                    await interact.response.send_message(f"ユーザーの入退出読み上げを**「有効(ユーザー別有効)」**にしたのだ！")
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)



    @yomi.command(name="connect-message", description="読み上げ接続時の読み上げ内容を変更するのだ")
    @app_commands.rename(text="文章")
    async def change_vc_exit_message(self, interact: Interaction, text: str):
        try:
            read_type = "vc_connect_message"
            res = save_server_setting(interact.guild.id, read_type, text)
            if res is None:
                await interact.response.send_message("**読み上げ接続時の読み上げ内容を変更したのだ！**")
                return
            
            await interact.response.send_message("設定に失敗したのだ...")  
            logging.warning(res)  

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)


    @yomi.command(name="auto-channel", description="設定したVCに自動接続するのだ(現在入っているVCが対象なのだ)")
    @app_commands.rename(bool="有効無効")
    @app_commands.choices(bool=[
        Choice(name="有効", value=1),
        Choice(name="無効", value=0)
    ])
    async def auto_connect(self, interact: Interaction, bool: int):
        try:
            if bool == 1:
                vc_id = interact.user.voice.channel.id
                if interact.user.voice is not None: ##設定するユーザーがチャンネルに入っていることを確認するのだ
                    res = save_server_setting(interact.guild_id, "auto_connect", vc_id)
                
                else: ##ユーザーがボイスチャットに入っていない場合
                    await interact.response.send_message("自動接続したいチャンネルに入ってから実行するのだ！")
                    return
            else:
                save_server_setting(interact.guild_id, "auto_connect", 0)
                await interact.response.send_message("自動接続を無効化したのだ！")
                return

            await interact.response.send_message(f"「<#{vc_id}>」に自動接続を設定したのだ！")
            
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    
    @app_commands.command(name="vc-stop", description="ボイスチャンネルから退出するのだ")
    async def vc_disconnect_command(self, interact: Interaction):
        try:
            if ((interact.guild.voice_client is None)):
                await interact.response.send_message("私はボイスチャンネルに接続していないのだ...")
                return
            
            elif((interact.user.voice is None)):
                await interact.response.send_message("ボイスチャンネルに接続していないのだ...入ってから実行するのだ")
                return
            elif interact.user.voice.channel != interact.guild.voice_client.channel:
                await interact.response.send_message("入っているボイスチャンネルと違うチャンネルなのだ...実行しているチャンネルでやるのだ")
                return
            
            await interact.guild.voice_client.disconnect()
            await interact.response.send_message("切断したのだ")
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(yomiage_cmds(bot))
