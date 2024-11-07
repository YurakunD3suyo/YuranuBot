
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
from modules.yomiage_main import yomiage
from modules import pages as Page

def make_new_embed(bot):
    embed = Embed(
        title="サーバー辞書の単語を表示するのだ！",
        description="サーバー辞書の単語を表示するのだ！",
        color=Color.green()
    )
    embed.set_footer(text=f"{bot.user.display_name} | Made by yurq.", icon_url=bot.user.avatar.url)

    return embed

class Admin( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    admincmd = app_commands.Group(name="owner", description="ボット管理者のみ実行可能なコマンドなのだ")
    @admincmd.command(name="list_g")
    async def list_guilds(self, interact: Interaction):
        #Botの所有者かどうかの判断
        appinfo = await self.bot.application_info()
        # botの管理者を取得
        if appinfo.team:
            owners = [member.id for member in appinfo.team.members]
        else:
            owners = [appinfo.owner.id]

        #管理者でない場合はメッセージを流して終わり
        if not(interact.user.id in owners):
            await interact.response.send_message("このコマンドは実行できません。")
            return

        guilds = self.bot.guilds
        guild_list = [f"{guild.name} (ID: {guild.id})" for guild in guilds]
        embeds = []
        
        if guild_list:
            embed = make_new_embed(self.bot)

            for i in range(len(guild_list)):
                embed.add_field(
                    name=f"単語{i+1}",
                    value=guild_list[i]
                )
                if (i+1) % 10 == 0: #10つごとにページを１つ作成
                    embeds.append(embed)
                    embed = make_new_embed(self.bot)

            if len(embed.fields) > 0: #もしembedに残りがある場合はそれもリストに入れる
                embeds.append(embed)
                
            await Page.Simple().start(interact, pages=embeds)
            return

        else:
            await interact.response.send_message("サーバーを検索できなかったのだ...")


    @app_commands.command(name="tts")
    async def tts_announce(self, interact: Interaction, content: str, id: str):
        #Botの所有者かどうかの判断
        appinfo = await self.bot.application_info()
        # botの管理者を取得
        if appinfo.team:
            owners = [member.id for member in appinfo.team.members]
        else:
            owners = [appinfo.owner.id]

        #管理者でない場合はメッセージを流して終わり
        if not(interact.user.id in owners):
            await interact.response.send_message("このコマンドは実行できません。")
            return
        
        guild = self.bot.get_guild(int(id))

        if guild == None:
            embed = Embed(
                title="サーバーが見つからなかったのだ！",
                description="サーバーにbotがいるかーとか確認してみて！",
                color=Color.red()
            )
            await interact.response.send_message(embed=embed)
            return
    
        if guild.voice_client == None:
            embed = Embed(
                title="ボイスに接続されていなかったのだ...",
                description="VCにbotがいるかーとか確認してみて！",
                color=Color.red()
            )
            await interact.response.send_message(embed=embed)
            return
        
        await yomiage(content, guild)
        embed = Embed(
                title="読み上げしたのだ！",
                description="アナウンスに成功しました！",
                color=Color.green()
            )
        await interact.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))