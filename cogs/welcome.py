from discord import Member, File, Embed, Color
from discord.ext import commands
from modules.delete import delete_file_latency
from modules.db_settings import get_server_setting
from modules.image_creator import make_welcome_image

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: Member):
        guild = member.guild
        channel_ = get_server_setting(guild.id, "welcome_server")

        if channel_ != 0:
            for chn in guild.text_channels:
                if chn.id == channel_:
                    path = make_welcome_image(member, guild)

                    file = File(path[0], filename=f"{path[1]}")
                    embed = Embed(title=f"「{guild.name}」へようこそなのだ！", 
                                        description=f"{member.mention}がやってきました。",
                                        color= Color.green(),
                                        )
                    embed.set_image(url=f"attachment://{path[1]}")
                    embed.set_footer(text=f"{self.bot.user.display_name} | Made by yurq.", icon_url=self.bot.user.avatar.url)

                    await chn.send(file=file, embed=embed)

                    delete_file_latency(path[0], 2)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Welcome(bot))