import os
import sys
import dotenv
import logging
# import discord
import asyncio
import subprocess

from discord import app_commands, Object, Interaction, Embed, Color
from discord.ext import commands


class Update(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 管理用サーバーにコマンドを追加 ------------------------
    #サポートサーバーが利用可能かの認識用
    support_enable = False

    try:
        #.envを読み込み
        dotenv.load_dotenv()
        #サポート鯖のIDを取得
        support_id = os.getenv("OP_SERVER")
        #strである場合はintに変換
        if type(support_id) == str:
            support_id = int(support_id)
            support_obj = Object(support_id)

            logging.debug(f"update -> サポートサーバーID: {support_id}")
            support_enable = True

        elif type(support_id) != None:
            logging.exception("update -> サポートサーバーのID記述が不適切")
        else:
            logging.warn("update -> サポートサーバー未登録(管理コマンドが利用不可)")
    except:
        logging.exception("update -> サポートサーバーの読み込みに失敗")

    # 管理コマンド関係 -----------------------------
    @app_commands.command(name="op-update", description="(管理コマンド)botをアップデートして自動再起動するのだ")
    @app_commands.guilds(support_obj)
    async def op_update(self, interact: Interaction):
        # Embedを先に送信し、アップデートを促す
        #embedを作成
        embed = Embed(
            title="更新中なのだ...",
            description="しばらくお待ちください...",
            color=Color.blue()
        )
        embed.add_field(
            name="アップデート状態",
            value="`githubから取得中...`"
        )
        interact.response.send_message(embed=embed)

        #githubからpullする
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        output = result.stdout
        error = result.stderr

        #エラーがない場合は続行、エラーの場合は停止
        if len(error) <= 0:
            embed = Embed(
                title="更新中なのだ...",
                description="しばらくお待ちください...",
                color=Color.green()
            )
            embed.add_field(
                name="アップデート状態",
                value="`アップデート完了、再起動します`"
            )
            interact.response.edit_message(embed=embed)
            asyncio.sleep(2)
            sys.exit()
        else: 
            embed = Embed(
                title="更新に失敗したのだ",
                description="エラーが発生したようです...",
                color=Color.red()
            )
            embed.add_field(
                name="アップデート状態",
                value=f"`{error}`"
            )
            interact.response.edit_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Update(bot))

