import logging
import requests
import os

from discord import app_commands
from discord.app_commands import Choice
from dotenv import load_dotenv
from modules.yomiage_main import VC_HOST, VC_PORT

#VOICEVOX_coreの場合や、話者読み込みに失敗した場合に使用
spk_list = [
    ["ずんだもん", 3],
    ["春日部つむぎ", 8],
    ["四国めたん", 2],
    ["九州そら", 16],
    ["雨晴はう", 10]
]

#読み上げ時の声の特性上、登録できる話者の上限等から特定の話者を無視(解決策を考えています)
ignore_id = [51, 52, 21, 13, 12, 11]

# Choiceリストを作る-----------------------------------------------------------
# VOICEVOXアプリから話者を取得し、リスト形式で返すメソッド-----------------
def load_from_voicevox_app():
    #スピーカー情報を取得し、jsonに変換
    try:
        global spk_list
        
        #VOICEVOXにリクエスト
        spk_req = requests.get(url=f"http://{VC_HOST}:{VC_PORT}/speakers")
        des_spks = spk_req.json()

        #spk_listを初期化
        spk_list = []

        #jsonから話者名とidを取得
        for des_spk in des_spks:
            for style in des_spk["styles"]:
                if style["name"] in ("ノーマル","ふつう", "人間ver.") :
                    name=des_spk["name"]
                    spk_id=style["id"]
                    
                    #特定のIDを無視する
                    if spk_id not in ignore_id:
                        #リストに追加
                        spk_list.append([name, spk_id])
        
        logging.info(f"vc_speakers -> 読み込み完了: {len(spk_list)}人の話者が登録済")
    except:
        logging.exception("vc_speakers -> VOICEVOXアプリから話者の読み込みに失敗")

#Choiceをまとめるリストを作成
spk_choices = []
user_spk_choices = []

#設定を取得
load_dotenv()
USE_VOICEVOX_APP = os.getenv("USE_VOICEVOX_APP") 

#VOICEVOXアプリの場合はGET/speakersから利用可能な音声をすべて登録
if USE_VOICEVOX_APP == "True":
    load_from_voicevox_app()

# リストの内容からChoiceを作りリストに追加
#サーバー向けのリスト
for spk_name, spk_id in spk_list:
    spk_choices.append(Choice(name=spk_name, value=spk_id))

#ユーザー向けのリスト
for spk_name, spk_id in spk_list:
    user_spk_choices.append(Choice(name=spk_name, value=spk_id))
    
logging.debug(f"vc_speakers -> 話者リスト: {len(spk_choices)}人の話者を登録済")

#ユーザー向けChoiceリストにデフォルト設定を追加
user_spk_choices.append(Choice(name="サーバーの話者を使用する", value=-1))

logging.debug(f"vc_speakers -> ユーザー話者リスト: {len(user_spk_choices)}人の話者を登録済")


# 読み上げ話者を検索する----------------------------------------------------
def find_spker(id=None, name=None):
    # idで検索する場合
    if id is not None:
        for spk_name, spk_id in spk_list:
            if spk_id == id:
                return [spk_name, spk_id]
    elif name is not None:
        for spk_name, spk_id in spk_list:
            if spk_name == name:
                return [spk_name, spk_id]
            