import discord
import discord.ext.commands 

client: discord.ext.commands.Bot

def exception_init(cli):
    global client
    client = cli

async def sendException(e, filename, line_no):
    channel_myserv = client.get_channel(1222923566379696190)
    channel_sdev = client.get_channel(1223972040319696937)

    embed = discord.Embed( # Embedを定義する
                title="うまくいかなかったのだ。",# タイトル
                color=discord.Color.red(), # フレーム色指定(ぬーん神)
                description=f"例外エラーが発生しました！詳細はこちらをご覧ください。", # Embedの説明文 必要に応じて
                )
    embed.add_field(name="**//エラー内容//**", inline=False, value=
                    f"{filename}({line_no}行) -> [{type(e)}] {e}")
    
    await channel_myserv.send(embed=embed)
    # await channel_sdev.send(embed=embed)