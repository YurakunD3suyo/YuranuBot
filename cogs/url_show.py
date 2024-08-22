import discord
import re
import logging

from modules.db_settings import save_server_setting, get_server_setting
from discord.ext import commands
from discord import app_commands

URL_REGEX = re.compile(r"https?://(ptb\.|canary\.)?discord(?:app)?\.com/channels/(\d+)/(\d+)/(\d+)")

class Discord_URL_Loader( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="discord-url-load", description="DiscordのメッセージURLからメッセージを取得するのだ")
    @app_commands.rename(use="設定")
    @app_commands.choices(use=[
        app_commands.Choice(name="使用する", value=1),
        app_commands.Choice(name="使用しない", value=0)
    ])
    async def discord_url_load(self, interact: discord.Interaction, use: int):
        # DBに保存
        result = save_server_setting(interact.guild.id, "discord_url_load", use)
        
        if result == None:
            use_str:str = None
            if use == 1:
                use_str = "使用する"
            else:
                use_str = "使用しない"
            
            await interact.response.send_message(f"Discord URL Loaderを**「{use_str}」**に設定したのだ！")
            return
        
        await interact.response.send_message("設定に失敗したのだ...")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        #サーバー設定を読み込み、この機能を使用するかを検出
        use = get_server_setting(message.guild.id, "discord_url_load")
        if use == 1:
            if message.author == self.bot.user:
                return
            
            # 正規表現でDiscordメッセージURLを検出
            search = URL_REGEX.search(message.content)

            if search:
                logging.debug(f"{__name__} -> Discord Message URLを検出")

                #URLからそれぞれを検出
                type, guild_id, channel_id, message_id = search.groups()
                
                #ギルドを取得
                guild = self.bot.get_guild(int(guild_id))

                if guild != None:
                    #チャンネルを取得
                    logging.debug(f"{__name__} -> ギルドを発見")
                    channel = guild.get_channel(int(channel_id))

                    if channel != None:
                        if channel.id == 1274365861410377749:
                            embed=discord.Embed(
                                title="ちょっと！なにしてるのだ！？",
                                description="おっと、見せられない内容なようです。",
                                color=discord.Color.purple()
                            )
                            embed.add_field(name="チャンネル", value=f"<#{channel.id}>")

                            await message.reply(embed=embed)
                            return

                        else:
                            #↑からメッセージを検索
                            logging.debug(f"{__name__} -> チャンネルを発見")
                            tar_message = await channel.fetch_message(int(message_id))

                        if tar_message != None:
                            logging.debug(f"{__name__} -> メッセージを発見")
                            #Embedでいろいーろ
                            embed=discord.Embed(
                                #メッセージの送信者
                                title=f"Message from {tar_message.author.name}",
                                #メッセージの内容
                                description=f"{tar_message.content}",

                                color=discord.Color.brand_green()
                            )

                            file = None
                            if guild.icon == None or tar_message == None:
                                #アイコンがなかったとき用のイメージを用意
                                file = discord.File(R"images\guest.png", filename="guest.png")

                            #サーバーアイコンとどこのやつか表示
                            author_str = f"{guild.name} | {channel.name}"
                            
                            if guild.icon != None:
                                embed.set_author(icon_url=guild.icon.url, name=author_str)
                            else:
                                embed.set_author(icon_url="attachment://guest.png", name=author_str)

                            #送信元のユーザーアイコン
                            if tar_message.author.avatar != None:
                                embed.set_thumbnail(url=tar_message.author.avatar.url)
                            else:
                                embed.set_thumbnail(url="attachment://guest.png")

                            # 埋め込みがある場合はそれも読み込む
                            if tar_message.attachments:
                                logging.debug(f"{__name__} -> ファイルを検出")
                                for attach in tar_message.attachments:
                                    #画像の場合は画像を埋め込む
                                    if attach.content_type.startswith("image"):
                                        logging.debug(f"{__name__} -> 画像を検出")
                                        embed.set_image(url=attach.url)
                                    if attach.content_type.startswith("video"):
                                        embed.add_field(name="動画URL", value=attach.url)
                            #送信
                            if file != None:
                                await message.reply(embed=embed, file=file)
                            else:
                                await message.reply(embed=embed)

async def setup(bot: commands.Bot ) -> None:
    await bot.add_cog(Discord_URL_Loader(bot))
                                

                