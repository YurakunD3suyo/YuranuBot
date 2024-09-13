import platform
import logging
import requests
import emoji
import time
import json
import wave
import sys
import re
import os

os_name = platform.uname().system

from discord import FFmpegPCMAudio, PCMVolumeTransformer, Message, Guild, VoiceClient, Embed, Colour
import discord.utils as utils
from modules.db_soundtext import get_soundtext_list
from cogs.tts.soundtext_cmds import SOUNDTEXT_DIR
from modules.db_settings import get_server_setting, get_user_setting
from modules.exception import sendException
from modules.db_vc_dictionary import get_dictionary
from modules.delete import delete_file_latency
from dotenv import load_dotenv
from collections import deque, defaultdict


load_dotenv()
USE_VOICEVOX_APP = os.getenv("USE_VOICEVOX_APP")

if USE_VOICEVOX_APP == "True":
    print("VOICEVOXアプリを使用します")
else:
    print("voicevox coreを利用します")
    from voicevox_core import AccelerationMode, AudioQuery, VoicevoxCore

    ###読み上げ用のコアをロードし、作成します
    core = VoicevoxCore(
        acceleration_mode=AccelerationMode.AUTO,
        open_jtalk_dict_dir = './voicevox/open_jtalk_dic_utf_8-1.11'
    )

## VOICEVOX用の設定
VC_OUTPUT = "./yomiage_data/"
FS = 24000
VC_HOST = "127.0.0.1"
VC_PORT = 50021

fix_words = [
    [r'(https?://\S+)', "URL省略 "],
    [r'<a:\w+:\d+>', "アニメ絵文字 "],
    [r'<:\w+:\d+>', "絵文字 "],
    [r':\w+\:', "絵文字 "],
    [r'```[\s\S]*?```', "コードブロック省略"],
    [r'\|\|.*?\|\|', "、"],
    ["～", "ー"], # のばしぼうの置き換え
    ["\n", "、"] # 改行はすこし間をあける
]

yomiage_serv_list = defaultdict(deque)
ace_left = 0

##ディレクトリがない場合は作成する
if (not os.path.isdir(VC_OUTPUT)):
    os.mkdir(VC_OUTPUT)

##読み上げのキューに入れる前に特定ワードを変換します
async def yomiage(content, guild: Guild):
    """
        # yomiage
        読み上げのキューに入れる前の処理を行います。

        - content: 読み上げる内容 ( str )
        - guild: 読み上げサーバー ( Guild )
    """
    # サウンドボード
    
    global ace_left
    if type(content) == Message:
        soundtext_mode = get_server_setting(guild.id, "soundtext_mode")

        if soundtext_mode != 0:
            sound_effects = get_soundtext_list(guild.id)
            for sound in sound_effects:
                [ word, sound_dir ] = sound
                volume = 0.2 # 仮なので0.2で統一

                fixed = content.content.replace("～", "ー")

                if fixed == word:
                    if soundtext_mode == 1:
                        embed = Embed(
                            title="ちょっと待つのだ！",
                            description="ゲームモードが有効です！VCの状況を確認してみよう。",
                            color=Colour.orange()
                        )
                        message = await content.reply(embed=embed)
                        await message.delete(delay=4.0)
                        return

                    if sound == "explosion.mp3":
                        ace_left += 1
                        
                        if ace_left >= 5:
                            sound_dir = "explosion2.mp3"
                            
                    else:
                        ace_left = 0
                    
                    logging.debug(f"サウンドボードの単語を検出: {content.content}")

                    sound_file = f"{SOUNDTEXT_DIR}{guild.id}/{sound_dir}"

                    file_list = [sound_file, -1, volume]
                    queue = yomiage_serv_list[guild.id]
                    queue.append(file_list)

                    if not guild.voice_client.is_playing():
                        send_voice(queue, guild.voice_client)

                    # if reply_url is not None:
                    #     await content.reply(reply_url)

                    return

    if type(content) == Message:
            ace_left == 0

            fixed_content = content.content

            ## 絵文字を文字に変換
            fixed_content = emoji.demojize(fixed_content)

            ## メンションされたユーザーのIDを名前に変換
            for mention in content.mentions:
                fixed_content = fixed_content.replace(f'<@{mention.id}>', "@"+mention.display_name)

            ## チャンネルIDをチャンネル名に置き換える
            channel_mentions = re.findall(r'<#([0-9]+)>', fixed_content)
            for channel_id in channel_mentions:
                channel = utils.get(content.guild.channels, id=int(channel_id))
                if channel:
                    fixed_content = fixed_content.replace(f'<#{channel_id}>', f'{channel.name}')

            ##コンテンツ関連の文章を生成する
            files_content = search_content(content)

            ##コンテンツ  +　文章
            if files_content != None:
                fixed_content = files_content + fixed_content

    elif type(content) == str:
        fixed_content = content

    ##サーバー辞書に登録された内容で置き換える
    dicts = get_dictionary(guild.id)
    if dicts != None:
        for text, reading, user in dicts:
            fixed_content = re.sub(text, reading, fixed_content, flags=re.IGNORECASE)

    ##fix_wordに含まれたワードをfix_end_wordに変換する
    for word in fix_words:
        [ replace_reg, replace_word ] = word
        fixed_content = re.sub(replace_reg, replace_word, fixed_content, flags=re.IGNORECASE)

    ##文字制限の設定を取得する
    length_limit = get_server_setting(guild.id, "length_limit")

    if (length_limit > 0): ##文字数制限(1文字以上なら有効化)
        speak_content = fixed_content[:length_limit] ##文字数制限（省略もつけちゃうよ♡）
    else:
        speak_content = fixed_content

    if (speak_content != fixed_content):
        speak_content = speak_content + "、省略"

    #ユーザ読み上げ速度がある場合はそっちを優先
    speed = get_server_setting(guild.id, "speak_speed")

    usr_speed = None
    if (type(content) == Message):
        usr_speed = get_user_setting(content.author.id, "speak_speed")

    if usr_speed != 0 and usr_speed is not None:
        speed = usr_speed

    ##サーバー話者を取得する
    spkID = get_server_setting(guild.id, "vc_speaker")

    ##読み上げ内容がメっセージの場合はユーザー話者を取得する
    spkID_usr = None
    if (type(content) == Message):
        spkID_usr = get_user_setting(content.author.id, "vc_speaker")

    ##ユーザー話者がない場合はサーバー話者を利用する
    if spkID_usr != -1 and spkID_usr is not None:
        spkID = spkID_usr

    await queue_yomiage(speak_content, guild, spkID, speed)

async def queue_yomiage(content: str, guild: Guild, spkID: int, speed: float = 1):
    try:
        logging.debug(f'"{content}" 速度: {speed}, 話者ID: {spkID}')

        if USE_VOICEVOX_APP == "True":
            params = (
                ('text', content),
                ('speaker', spkID)
            )
            _query = requests.post(
                f'http://{VC_HOST}:{VC_PORT}/audio_query',
                params=params
            )
            query = _query.json()
            query["speedScale"] = speed

            synthesis = requests.post(
                f'http://{VC_HOST}:{VC_PORT}/synthesis',
                headers = {"Content-Type": "application/json"},
                params = params,
                data = json.dumps(query)
            )
            voice_byte = synthesis.content

        elif USE_VOICEVOX_APP == "False" or USE_VOICEVOX_APP is None:
            core.load_model(spkID)

            audio_query = core.audio_query(content, spkID)
            audio_query.speed_scale = speed

            voice_byte = core.synthesis(audio_query, spkID)

        ###作成時間を記録するため、timeを利用する
        wav_time = time.time()
        voice_file = f"{VC_OUTPUT}{guild.id}-{wav_time}.wav"

        if synthesis.status_code == 200:
            with open(voice_file, "wb") as f:
                f.write(voice_byte)
        else:
            raise SystemError("VOICEVOXでの音声生成に失敗しました。")

        with wave.open(voice_file,  'rb') as f:
            # 情報取得
            framerate = f.getframerate()
            frames = f.getnframes()
            length = frames / framerate

        file_list = [voice_file, length, 1]

        queue = yomiage_serv_list[guild.id]
        queue.append(file_list)

        if not guild.voice_client.is_playing():
            send_voice(queue, guild.voice_client)
        return

    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_no = exception_traceback.tb_lineno
        await sendException(e, filename, line_no)

##コンテンツが添付されている場合の処理
def search_content(content: Message):
    send_content = ""

    attach_length = len(content.attachments)
    sticker_length = len(content.stickers)

    if attach_length > 0:
        if attach_length >= 3: ##ファイル数が３つ以上なら
            _len = 2
            file_count = True
        else:
            _len = attach_length
            file_count = False


        for i in range(_len):
            attachment = content.attachments[i]

            if attachment.content_type == "image/gif":
                fixed_content = f"GIFファイル"
            elif attachment.content_type.startswith("image"):
                fixed_content = f"画像ファイル"
            if attachment.content_type.startswith("video"):
                fixed_content = f"動画ファイル"
            if attachment.content_type.startswith("audio"):
                fixed_content = f"音声ファイル"
            if attachment.content_type.startswith("text"):
                fixed_content = f"テキストファイル"
            if attachment.content_type.startswith("application"):
                fixed_content = f"その他ファイル"
            if attachment.content_type.startswith("zip"):
                fixed_content = f"じっぷファイル"
            if attachment.content_type.startswith("pdf"):
                fixed_content = f"PDFファイル"
            send_content += fixed_content

            if i != _len-1:#と　もつける
                send_content += "と"
        #ファイルが多すぎてもこれでおっけ！
        if file_count:
            send_content += f"とその他{attach_length-2}ファイル"
        #語尾もちゃんとつける！
        send_content += "が添付されました、"

    if sticker_length > 0:
        send_content += "スタンプが送信されました、"

    return send_content



def send_voice(queue, voice_client: VoiceClient):
    if not queue or voice_client.is_playing():
        return

    source = queue.popleft()
    [ directory, latency, volume ] = source

    pcmaudio_fixed = PCMVolumeTransformer(FFmpegPCMAudio(directory))
    pcmaudio_fixed.volume = volume

    voice_client.play(pcmaudio_fixed, after=lambda e:send_voice(queue, voice_client))

    if latency != -1:
        ## 再生スタートが完了したら時間差でファイルを削除する。
        delete_file_latency(directory, latency)

