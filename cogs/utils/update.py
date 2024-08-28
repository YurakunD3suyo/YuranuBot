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

    # 管理コマンド関係 -----------------------------
    op = app_commands.Group(name="op", description="管理コマンドなのだ")

    @op.command(name="update", description="(管理コマンド)botをアップデートして自動再起動するのだ") 
    async def op_update(self, interact: Interaction):
        #Botの所有者かどうかの判断
        appinfo = await self.bot.application_info()
        
        # botの管理者を取得
        owners = []
        if appinfo.team:
            owners = [member.id for member in appinfo.team.members]
        else:
            owners = [appinfo.owner.id]

        #管理者でない場合はメッセージを流して終わり
        if not(interact.user.id in owners):
            await interact.response.send_message("このコマンドは実行できません。")
            return

        # Contextを取得
        ctx = await commands.Context.from_interaction(interact)
        
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
        message = await ctx.send(embed=embed)

        #githubからpullする
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)
        output = result.stdout
        errcode = result.returncode
        error = result.stderr

        logging.debug(f"update -> Bot Updated (output: {output}, err: {error})")

        #エラーがない場合は続行、エラーの場合は停止
        if errcode != 0:
            # すでに最新の場合は起動したままにする。
            if output == "Already up to date.\n":
                embed = Embed(
                    title="すでに最新なのだ！",
                    description="更新の必要はありません。",
                    color=Color.green()
                )
                embed.add_field(
                    name="アップデート状態",
                    value=f"`{output}`"
                )
                await message.edit(embed=embed)
                return
            
            embed = Embed(
                title="更新中できたのだ！！",
                description="アップデートが完了しました！",
                color=Color.green()
            )
            embed.add_field(
                name="アップデート状態",
                value=f"`{output}`"
            )
            await message.edit(embed=embed)
            await asyncio.sleep(2)
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
            await message.edit(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Update(bot))

