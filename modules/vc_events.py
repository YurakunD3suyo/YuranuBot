from discord import Member, VoiceState, Client
import random
import re

from modules.messages import conn_message, zunda_conn_message
from modules.yomiage_main import yomiage
from modules.db_settings import get_server_setting, get_user_setting

async def vc_inout_process(
        member: Member, 
        before: VoiceState, 
        after: VoiceState,
        bot: Client
):
    # ボットなら無視
    if member.bot: 
        return      

    # #####!!!!!!自動接続関連!!!!!!!!!!########
    # ##接続時に自動接続する
    if after.channel != None:
        auto_channel = get_server_setting(member.guild.id, "auto_connect")
        if auto_channel == after.channel.id:
            if not member.guild.voice_client or member.guild.voice_client.channel != after.channel:
                await after.channel.connect()
            
                spkID = get_server_setting(member.guild.id, "vc_speaker")
                if spkID == 3:
                    mess = random.choice(zunda_conn_message)
                    await yomiage(mess, member.guild)
                else:
                    mess = random.choice(conn_message)
                    await yomiage(mess, member.guild)

                return # 接続しましただけを読ませるために終わらせる

    if member.guild.voice_client and before.channel != after.channel:
        if before.channel == member.guild.voice_client.channel:
            if before.channel != None:
                members = before.channel.members
                count = 0
                for m in before.channel.members:
                    if m.bot:
                        members.pop(count)
                        count -= 1
                    count += 1
                    
                if len(members) == 0:
                    await member.guild.voice_client.disconnect()
                    return

        if before.channel != after.channel:
            for bot_client in bot.voice_clients:
                ##参加時に読み上げる
                if after.channel is not None:
                    _announce = get_server_setting(after.channel.guild.id, "vc_user_announce")
                    mess = get_server_setting(after.channel.guild.id, "vc_join_message")#==が参加したのだ

                    if (after.channel.id == bot_client.channel.id):
                        if _announce == 2:
                            user_mess = get_user_setting(member.id, "conn_msg")
                            
                            if user_mess == "nan" and mess is not None:
                                await yomiage(f"{member.display_name}{mess}", member.guild)

                            elif user_mess != None:
                                user_mess = user_mess.replace("<user>", member.display_name)
                                await yomiage(user_mess, member.guild)
                                
                        elif _announce == 1:
                            if mess is not None:
                                await yomiage(f"{member.display_name}{mess}", member.guild)
                    
                ##退席時に読み上げる
                if before.channel is not None:
                    _announce = get_server_setting(before.channel.guild.id, "vc_user_announce")
                    mess = get_server_setting(before.channel.guild.id, "vc_exit_message")#==が退席したのだ

                    if (before.channel.id == bot_client.channel.id):
                        if _announce == 2:
                            user_mess = get_user_setting(member.id, "disconn_msg")

                            if user_mess == "nan" and mess is not None:
                                await yomiage(f"{member.display_name}{mess}", member.guild)

                            elif user_mess != None:
                                user_mess = user_mess.replace("<user>", member.display_name)
                                await yomiage(user_mess, member.guild)

                        elif _announce == 1:
                            if mess is not None:
                                await yomiage(f"{member.display_name}{mess}", member.guild)
                        
                        
    if member.guild.voice_client:
        if after.channel == member.guild.voice_client.channel:
            #カメラ配信の開始・終了を読み上げる
            if before.self_video != after.self_video:
                if after.self_video:
                    await yomiage(f"{member.display_name}がカメラ配信を開始しました。", member.guild)
                else:
                    await yomiage(f"{member.display_name}がカメラ配信を終了しました。", member.guild)

            #画面共有の開始・終了を読み上げる
            if before.self_stream != after.self_stream:
                if after.self_stream:
                    await yomiage(f"{member.display_name}が画面共有を開始しました。", member.guild)
                else:
                    await yomiage(f"{member.display_name}が画面共有を終了しました。", member.guild)

