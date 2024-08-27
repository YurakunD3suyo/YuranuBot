
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
from modules.yomiage_main import yomiage

class Admin( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="list_guilds", description="ボットが参加しているサーバーのリストを表示します。")
    @app_commands.default_permissions(administrator=True)
    async def list_guilds(self, interaction: Interaction):
        guilds = self.bot.guilds
        guild_list = "\n".join([f"{guild.name} (ID: {guild.id})" for guild in guilds])

        if guild_list:
            embed = Embed(
                title="これが知りたいのか？",
                color=Color.blue()
            )
            embed.add_field(name="> どこに参加してるのかな～", value=f"- {guild_list}", inline=False)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="tts_announce")
    async def tts_announce(self, interact: Interaction, content: str, id: str):
        is_owner = await self.bot.is_owner(interact.user)
        if is_owner != False:
            embed = Embed(
                title="bot管理者のみ実行可能なのだ！",
                color=Color.red()
            )
            await interact.response.send_message(embed=embed)
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