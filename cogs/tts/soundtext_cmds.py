import requests
import sys
import os

from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color, Attachment
from modules.db_soundtext import save_soundtext, get_soundtext_list, find_soundtext, delete_soundtext
from modules.db_settings import save_server_setting
from modules.exception import sendException
from modules import pages as Page

# 拡張子の登録
SOUNDTEXT_DIR = "./sound/"
ALLOWED_EXTENSIONS = ['mp3', 'wav', 'ogg', 'flac', 'm4a']

# 拡張子を検出するメソッド
def check_file(file: Attachment):
    filename = file.filename
    return filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS

# ファイル名が同じ場合でも重複することなく登録するための変換メソッド
def get_unique_filename(directory, filename):
    base, extension = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base} ({counter}){extension}"
        counter += 1
    return unique_filename


class SoundTextCommands( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        #soundフォルダを作成
        if (not os.path.isdir(SOUNDTEXT_DIR)): 
            os.mkdir(SOUNDTEXT_DIR)

    st = app_commands.Group(name="soundtext", description="サウンドテキスト関連の設定なのだ")

    @st.command(name="add", description="サウンドテキストを追加するのだ")
    @app_commands.rename(file="流す音声ファイル")
    @app_commands.describe(file="mp3とwavのみに対応なのだ")
    async def soundtext_add(self, interact: Interaction, word: str, file: Attachment):

        # 同じ単語が存在しないか確認
        st_word = find_soundtext(interact.guild.id, word)
        if st_word:
            embed = Embed(
                title="既に登録されているのだ！",
                description="すでにその単語名は存在します。リストをご確認ください。",
                color=Color.red()
            )
            embed.add_field(name="単語名", value=word)
            await interact.response.send_message(embed=embed)
            return

        # ファイルが複数ある場合はエラー
        if type(file) != Attachment:
            embed = Embed(
                title="ファイルは１つだけ送信するのだ！",
                description="複数ファイルを１つの単語に登録することはできません。",
                color=Color.red()
            )
            await interact.response.send_message(embed=embed)
            return

        # チェックを通った場合は、ファイルを特定のパスに保存し、データベースに登録
        if check_file(file):
            
            # サーバーID別でフォルダを管理
            save_dir = SOUNDTEXT_DIR + f"{interact.guild.id}/"

            #使用できるファイル名を取得し、パスも取得
            uniquename = get_unique_filename(save_dir, file.filename)
            file_path = os.path.join(save_dir, uniquename)

            # フォルダが存在しない場合は作成
            if (not os.path.isdir(save_dir)): 
                os.mkdir(save_dir)

            # ファイルを保存
            await file.save(file_path)
            
            #データベースに登録
            result = save_soundtext(interact.guild.id, word, uniquename)

            if result == None:
                embed = Embed(
                    title="登録できたのだ！",
                    description="サウンドテキストを保存しました！",
                    color=Color.green()
                )
                embed.add_field(name="単語名", value=word)
                await interact.response.send_message(embed=embed)
            
            else:
                embed = Embed(
                    title="登録に失敗したのだ...",
                    description="登録できませんでした。管理者にお問い合わせください。",
                    color=Color.green()
                )
                embed.add_field(name="エラー文", value=result)
                await interact.response.send_message(embed=embed)

                os.remove(file_path)
            
        else:
            embed = Embed(
                title="ファイルが未対応なのだ...",
                description="mp3やwavなどに変換して再度行ってください。",
                color=Color.red()
            )
            await interact.response.send_message(embed=embed)
    
    @st.command(name="delete", description="サウンドテキストを削除するのだ")
    async def soundtext_delete(self, interact: Interaction, word: str):
        
        # 見つからない場合はエラーを送信
        del_st = find_soundtext(interact.guild.id, word)
        if del_st == None:
            embed = Embed(
                title="サウンドテキストが見つからなかったのだ...",
                description="サウンドテキストは見つかりませんでした。",
                color=Color.orange()
            )
            await interact.response.send_message(embed=embed)
            return

        # データベースから削除
        result = delete_soundtext(interact.guild.id, word)
        # 効果音を削除
        print(del_st)
        [ word, path ] = del_st
        try:
            full_path = os.path.join(SOUNDTEXT_DIR, f"{interact.guild.id}", path)
            os.remove(full_path)
        except FileNotFoundError:
            embed = Embed(
                title="削除に失敗したのだ...",
                description="削除できませんでした。管理者にお問い合わせください。",
                color=Color.green()
            )
            embed.add_field(name="エラー文", value=result)
            
            await interact.response.send_message(embed=embed)
            return

        if result == None:
            embed = Embed(
                title="サウンドテキストを削除したのだ！",
                description="正常に削除しました！",
                color=Color.green()
            )
            embed.add_field(name="単語名", value=word)
            await interact.response.send_message(embed=embed)
            return
        else:
            embed = Embed(
                title="削除に失敗したのだ...",
                description="削除できませんでした。管理者にお問い合わせください。",
                color=Color.green()
            )
            embed.add_field(name="エラー文", value=result)


    @st.command(name="list", description="サーバー辞書の単語を表示するのだ")
    async def soundboard_list(self, interact: Interaction):
        try:
            result = get_soundtext_list(interact.guild.id)
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