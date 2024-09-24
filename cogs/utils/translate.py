import deepl
import os

from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color
from discord.app_commands import Choice

class Translate( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="translate", description="翻訳コマンドなのだ")
    @app_commands.choices(target_lang=[
        Choice(name="日本語", value="JA"),
        Choice(name="英語", value="EN"),
    ])
    async def translate(self, interact: Interaction, sentence: str, target_lang: str):
        auth = os.getenv("DEEPL_AUTH_KEY")
        translator = deepl.Translator(auth)

        result = translator.translate_text(sentence, target_lang=target_lang)

        embed = Embed(
            title="翻訳したのだ！",
            description="正常に翻訳しました。結果は以下の通りです。",
            color=Color.green()
        )
        embed.add_field(
            name="翻訳前",
            value=sentence
        )
        embed.add_field(
            name="翻訳後",
            value=result
        )

        await interact.response.send_message(embed=embed)

        translator.close()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Translate(bot))

