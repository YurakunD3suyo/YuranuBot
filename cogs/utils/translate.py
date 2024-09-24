import deepl
import os

from discord.ext import commands
from discord import app_commands, Interaction, Embed, Color, File
from discord.app_commands import Choice

class Translate( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="translate", description="翻訳コマンドなのだ")
    @app_commands.choices(target_lang=[
        Choice(name="英語(アメリカ)", value="EN-US"),
        Choice(name="英語(イギリス)", value="EN-GB"),
        Choice(name="中国語(簡体)", value="ZN-HANS"),
        Choice(name="中国語(繁体)", value="ZN-HANT"),
        Choice(name="韓国語", value="KO"),
        Choice(name="日本語", value="JA")
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
            value=sentence,
            inline=False
        )
        embed.add_field(
            name="翻訳後",
            value=result,
            inline=False
        )
        embed.set_thumbnail(url=f"attachment://boticon_zunda.png")
        embed.set_footer(text=f"DeepL Translate", icon_url="https://cdn.freelogovectors.net/wp-content/uploads/2022/01/deepl-logo-freelogovectors.net_.png")

        await interact.response.send_message(embed=embed)

        translator.close()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Translate(bot))

