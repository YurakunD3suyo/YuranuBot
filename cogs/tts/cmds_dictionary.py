from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color

import sys
from modules.exception import sendException
from modules.db_vc_dictionary import delete_dictionary, save_dictionary, get_dictionary
from modules import pages as Page

def make_new_embed(bot):
    embed = Embed(
        title="サーバー辞書の単語を表示するのだ！",
        description="サーバー辞書の単語を表示するのだ！",
        color=Color.green()
    )
    embed.set_footer(text=f"{bot.user.display_name} | Made by yurq.", icon_url=bot.user.avatar.url)

    return embed

class Dictionary(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    dict_cmd = app_commands.Group(name="dictionary", description="辞書系のコマンドなのだ")

    @dict_cmd.command(name="add", description="サーバー辞書に単語を追加するのだ")
    @app_commands.rename(text="単語", reading="かな")
    async def vc_dictionary(self, interact: Interaction, text: str, reading: str):
        try:
            result = save_dictionary(interact.guild.id, text, reading, interact.user.id)
            if result is None:
                embed = Embed(
                    title="正常に登録したのだ！",
                    description="サーバー辞書に単語を登録しました！",
                    color=Color.green()
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

    @dict_cmd.command(name="delete", description="サーバー辞書の単語を削除するのだ")
    @app_commands.rename(text="単語")
    async def vc_dictionary(self, interact: Interaction, text: str):
        try:
            result = delete_dictionary(interact.guild.id, text)
            if result is None:
                embed = Embed(
                    title="正常に削除したのだ！",
                    description="サーバー辞書の単語を削除しました！",
                    color=Color.green()
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

    @dict_cmd.command(name="list", description="サーバー辞書の単語を表示するのだ")
    async def vc_dictionary(self, interact: Interaction):
        try:
            result = get_dictionary(interact.guild.id)
            if result:
                embeds = []
                embed = make_new_embed(self.bot)

                for i in range(len(result)):
                    embed.add_field(
                        name=f"単語{i+1}",
                        value=f"単語: {result[i][0]}\n読み仮名: {result[i][1]}\n登録者: <@{result[i][2]}>"
                    )

                    if (i+1) % 10 == 0:  # Create a new embed every 10 words
                        embeds.append(embed)
                        embed = make_new_embed(self.bot)

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

    @dict_cmd.command(name="find", description="入力された単語から辞書内を検索します")
    @app_commands.rename(fword="単語")
    async def vc_dictionary_find(self, interact: Interaction, fword: str):
        result = get_dictionary(interact.guild.id)
    
        embed = Embed(
            title="見つからなかったのだ...",
            description="単語はありませんでした。新しく作ってみてもいいかも。",
            color=Color.orange()
        )

        for word, kana, user in result:
            if word == fword:
                embed = Embed(
                    title="発見したのだ！",
                    description="単語を発見しました。",
                    color=Color.green()
                )
                embed.add_field(
                    name="単語名",
                    value=word
                )
                embed.add_field(
                    name="読みカナ",
                    value=kana
                )
                embed.add_field(
                    name="登録ユーザー",
                    value=f"<@{user}>"
                )

        await interact.response.send_message(embed=embed)
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Dictionary(bot))