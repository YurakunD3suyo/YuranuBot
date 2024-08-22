import discord
from discord.ext import commands
from discord import app_commands

import sys
import logging
import random
from modules.vc_speakers import spk_choices, user_spk_choices, find_spker

from modules.messages import conn_message, zunda_conn_message
from modules.pc_status import pc_status
from modules.yomiage_main import yomiage, queue_yomiage, sound_effects
from modules.vc_events import vc_inout_process
from modules.db_settings import db_load, db_init, get_server_setting, get_user_setting, save_server_setting, save_user_setting
from modules.exception import sendException, exception_init
from modules.db_vc_dictionary import dictionary_load, delete_dictionary, save_dictionary, get_dictionary
import modules.pages as Page


class yomiage_cmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    yomi = app_commands.Group(name="yomiage", description="読み上げ関連のコマンドを実行するのだ")
        
    
    @app_commands.command(name="vc-start", description="ユーザーが接続しているボイスチャットに接続するのだ")
    async def vc_command(self, interact: discord.Interaction):
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
        
            embed = discord.Embed(
                title="接続したのだ！",
                description="ボイスチャンネルに参加しました！",
                color=discord.Color.green()
            )
            embed.add_field(
                name="読み上げるチャンネル",
                value=f"> {channel}"
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
            embed.add_field(
                name="自然係サーバーの方々によりずんだぼっとがパワーアップしました！",
                value="安定性、機能性向上にご協力いただき本当にありがとうございます！！",
                inline=False
                )
            file = discord.File(R"images\boticon_zunda.png", filename="boticon_zunda.png")
            embed.set_thumbnail(url=f"attachment://boticon_zunda.png")
            embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

            await interact.response.send_message(embed=embed, file=file)

            ##読み上げるチャンネルが存在しない場合に警告文を送信

            if (channel is None):
                embed = discord.Embed(
                    color=discord.Color.red(),
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


    @yomi.command(name="server-settings", description="サーバーの読み上げ設定を表示するのだ")
    async def check_yomi_settings(self, interact: discord.Interaction):
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

        embed = discord.Embed(
            title="サーバーの読み上げ設定を表示するのだ！",
            color=discord.Color.green()
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

    @yomi.command(name="user-settings", description="ユーザーの読み上げ設定を表示するのだ")
    async def check_user_yomi_settings(self, interact: discord.Interaction):
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
        embed = discord.Embed(
            title="ユーザーの読み上げ設定を表示するのだ！",
            color=discord.Color.green()
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

    @yomi.command(name="channel", description="読み上げるチャンネルを変更するのだ")
    async def yomiage_channel(self, interact: discord.Interaction, channel: discord.TextChannel):
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
        
    
    @yomi.command(name="announcement", description="ユーザーの入退出を読み上げするのだ")
    @app_commands.rename(activate="有効無効")
    @app_commands.choices(
        activate=[
            app_commands.Choice(name="有効(ユーザー別有効)", value=2),
            app_commands.Choice(name="有効(ユーザー別無効)",value=1),
            app_commands.Choice(name="アナウンス無効",value=0)
        ]
    )
    async def yomiage_channel(self, interact: discord.Interaction, activate: int):
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

    @yomi.command(name="dictionary-add", description="サーバー辞書に単語を追加するのだ")
    @app_commands.rename(text="単語", reading="かな")
    async def vc_dictionary(self, interact: discord.Interaction, text: str, reading: str):
        try:
            result = save_dictionary(interact.guild.id, text, reading, interact.user.id)
            if result is None:
                embed = discord.Embed(
                    title="正常に登録したのだ！",
                    description="サーバー辞書に単語を登録しました！",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="登録した単語",
                    value=text
                )
                embed.add_field(
                    name="読み仮名",
                    value=reading
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                await interact.response.send_message(embed=embed)
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)
    

    @yomi.command(name="dictionary-list", description="サーバー辞書の単語を表示するのだ")
    async def vc_dictionary(self, interact: discord.Interaction):
        try:
            result = get_dictionary(interact.guild.id)
            if result:
                embeds = []
                embed = discord.Embed(
                    title="サーバー辞書の単語を表示するのだ！",
                    description="サーバー辞書の単語を表示しています！",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                for i in range(len(result)):
                    embed.add_field(
                        name=f"単語{i+1}",
                        value=f"単語: {result[i][0]}\n読み仮名: {result[i][1]}\n登録者: <@{result[i][2]}>"
                    )

                    if (i+1) % 10 == 0:  # Create a new embed every 10 words
                        embeds.append(embed)
                        embed = discord.Embed(
                            title="サーバー辞書の単語を表示するのだ！",
                            description="サーバー辞書の単語を表示するのだ！",
                            color=discord.Color.green()
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

    @yomi.command(name="dictionary-delete", description="サーバー辞書の単語を削除するのだ")
    async def vc_dictionary(self, interact: discord.Interaction, text: str):
        try:
            result = delete_dictionary(interact.guild.id, text)
            if result is None:
                embed = discord.Embed(
                    title="正常に削除したのだ！",
                    description="サーバー辞書の単語を削除しました！",
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="削除した単語",
                    value=text
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                await interact.response.send_message(embed=embed)
                return
            
            await interact.response.send_message(f"設定に失敗したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="soundtext-list", description="サーバー辞書の単語を表示するのだ")
    async def soundboard_list(self, interact: discord.Interaction):
        try:
            result = sound_effects
            if result:
                embeds = []
                embed = discord.Embed(
                    title="これを使ってみるのだ！",
                    description="使用できるサウンドテキストの一覧です。",
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)
                
                for i in range(len(result)):
                    embed.add_field(
                        name=f"サウンドテキスト{i+1}",
                        value=f"{result[i][0]}"
                    )

                    if (i+1) % 10 == 0:  # Create a new embed every 10 words
                        embeds.append(embed)
                        embed = discord.Embed(
                            title="これを使ってみるのだ！",
                            description="使用できるサウンドテキストの一覧です。",
                            color=discord.Color.green()
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

    @yomi.command(name="soundtext-mode", description="サウンドテキスト機能を変更するのだ")
    @app_commands.rename(mode="モード")
    @app_commands.choices(
        mode=[
            app_commands.Choice(name="有効", value=2),
            app_commands.Choice(name="ゲームモード",value=1),
            app_commands.Choice(name="無効",value=0)
        ]
    )
    async def soundtext_mode(self, interact: discord.Interaction, mode: int):
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

    @yomi.command(name="server-speaker", description="サーバーの読み上げ話者を設定するのだ")
    @app_commands.rename(id="話者")
    @app_commands.choices(id=spk_choices)
    async def yomiage_server_speaker(self, interact:discord.Interaction,id:int):
        try:
            if interact.user.guild_permissions.administrator:
                read_type = "vc_speaker"
                result = save_server_setting(interact.guild.id, read_type, id)

                if result is None:
                    spker_name = find_spker(id=id)
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


    @yomi.command(name="user-speaker", description="ユーザーの読み上げ話者を設定するのだ(どのサーバーでも同期されるのだ)")
    @app_commands.rename(id="話者")
    @app_commands.choices(id=user_spk_choices)
    async def yomiage_user_speaker(self, interact:discord.Interaction,id:int):
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


    @yomi.command(name="server-speed", description="サーバーの読み上げ速度を変更するのだ")
    @app_commands.rename(speed="速度")
    @app_commands.describe(speed="0.5~2.0")
    async def yomiage_speed(self, interact: discord.Interaction, speed: float):
        try:
            if speed >= 0.5 or speed <=2.0:
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


    @yomi.command(name="user-speed", description="ユーザー読み上げ速度を変更するのだ")
    @app_commands.rename(speed="速度")
    @app_commands.describe(speed="0.5~2.0 (0: サーバー設定を使用する)")
    async def user_speed(self, interact: discord.Interaction, speed: float):
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


    @yomi.command(name="length-limit", description="読み上げ文字数を制限するのだ")
    async def yomiage_speed(self, interact: discord.Interaction, limit: int):
        try:
            read_type = "length_limit"
            result = save_server_setting(interact.guild.id, read_type, limit)

            if result is None:
                await interact.response.send_message(f"読み上げ文字数を**「{limit}文字」**に変更したのだ！")
                return
            
            await interact.response.send_message("エラーが発生したのだ...")

        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_no = exception_traceback.tb_lineno
            await sendException(e, filename, line_no)

    @yomi.command(name="join-message", description="参加時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    async def change_vc_join_message(self, interact: discord.Interaction, text: str):
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
            
    @yomi.command(name="exit-message", description="退出時の読み上げ内容を変更するのだ<<必ず最初にユーザー名が来るのだ>>")
    async def change_vc_exit_message(self, interact: discord.Interaction, text: str):
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
    

    @yomi.command(name="user-join-message", description="[ユーザー別]参加時の読み上げを設定するのだ！")
    @app_commands.describe(text="<user> : ユーザー名")
    async def change_user_join_message(self, interact: discord.Interaction, text: str):
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

    @yomi.command(name="user-exit-message", description="[ユーザー別]退席時の読み上げを設定するのだ！")
    @app_commands.describe(text="<user>: ユーザー名")
    async def change_user_exit_message(self, interact: discord.Interaction, text: str):
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


    @yomi.command(name="connect-message", description="読み上げ接続時の読み上げ内容を変更するのだ")
    async def change_vc_exit_message(self, interact: discord.Interaction, text: str):
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
    async def auto_connect(self, interact: discord.Interaction, bool: bool):
        try:
            if bool is True:
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
    async def vc_disconnect_command(self, interact: discord.Interaction):
        try:
            if ((interact.guild.voice_client is None)):
                await interact.response.send_message("私はボイスチャンネルに接続していないのだ...")
                return
            
            elif((interact.user.voice is None)):
                await interact.response.send_message("ボイスチャンネルに接続していないのだ...入ってから実行するのだ")
                return
            elif interact.user.voice.channel != interact.guild.voice_client.channel:
                await interact.response.send_message("入ってるボイスチャンネルと違うチャンネルなのだ...実行してるチャンネルでやるのだ")
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
