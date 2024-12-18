# import discord
import os
import logging
import subprocess
import sys
import time

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from modules.exception import exception_init
from modules.db_settings import db_load, db_init
from modules.db_vc_dictionary import dictionary_load
from modules.db_soundtext import soundtext_load
from modules import prometheus

logging.basicConfig(level=logging.INFO)

# ディレクトリの取得
ROOT_DIR = os.path.dirname(__file__)

# .envから設定値を取得
load_dotenv()
TOKEN = os.getenv("TOKEN")
DIC_DIR = os.getenv("DIC_DIR")
PREFIX = os.getenv("PREFIX")
PROMETHEUS = True if os.getenv("PROMETHEUS") == "True" else False

###データベースの読み込み

## サーバー辞書共有用
# ディレクトリが設定されている場合はその場所を指定
if type(DIC_DIR) is str:
    dict_dir = os.path.join(DIC_DIR, "dictionary.db")
# ディレクトリが設定されていない場合はデフォルトの場所
else:
    dict_dir = "dictionary.db"

# サーバー辞書読み込み
dic_res = dictionary_load(dict_dir)

if dic_res==False:
    logging.exception("Database -> dictionaryの読み込みに失敗しました")
    sys.exit()
else:
    logging.info("Database -> dictionaryを読み込みました。")

# サーバー設定読み込み
db_load("database.db")
db_result = db_init()

if db_result==False:
    logging.exception("Database -> databaseの読み込みに失敗しました")
    sys.exit()
else:
    logging.info("Database -> databaseを読み込みました。")

st_result = soundtext_load("soundtext.db")

if st_result==False:
    logging.exception("Database -> soundtextの読み込みに失敗しました")
    sys.exit()
else:
    logging.info("Database -> soundtextを読み込みました。")

### インテントの生成
intents = Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.guilds = True
logging.info("bot -> インテント生成完了")

if type(PREFIX) == str:
    bot = commands.Bot(command_prefix=PREFIX, intents=intents)
    logging.info("bot -> クライアント生成完了")
else:
    logging.error("setting -> .envに「PREFIX」が設定されていません！")
    sys.exit()

#スタート時間を作成
bot.start_time = time.time()
bot.metrics = prometheus.MetricsGenerator()

#Prometheus監視用のやつ
bot.prometheus = PROMETHEUS

bot.metrics.create_gauge("tts_total_times", "The number of times the TTS processed")
bot.metrics.create_gauge("tts_total_length", "The total length of speak")
bot.metrics.create_gauge("tts_errors", "Total of errors in TTS Bot")
bot.metrics.create_gauge("tts_guilds", "Total of guilds TTS bot installed")
bot.metrics.create_gauge("tts_users", "Total of users in guilds")


##sendExceptionが利用できるようにする
exception_init(bot)

### コマンドツリーの作成
tree = bot.tree
logging.info("bot -> ツリー生成完了")

@bot.event
async def on_ready():
    loaded_cogs = 0
    exceptions_cogs = 0

    # cogファイルを読み込む(cogフォルダ内すべてのフォルダを検索)
    for dirpath, _, files in os.walk(os.path.join(ROOT_DIR, "cogs")):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == ".py":
                path = os.path.relpath(os.path.join(dirpath, file), ROOT_DIR)
                module = path.replace(os.sep, ".")[:-3]
                try:
                    await bot.load_extension(module)
                    logging.info(f'bot -> 読み込み完了: {module}')
                    loaded_cogs += 1
                except Exception as e:
                    logging.exception(f'bot -> 読み込み失敗: {module}')
                    logging.exception(e)
                    exceptions_cogs += 1
            elif not ext:
                try: 
                    await bot.load_extension(name)
                    logging.info(f'bot -> 読み込み完了: {name}')
                    loaded_cogs += 1
                except Exception as e:
                    logging.exception(f'bot -> 読み込み失敗: {name}')
                    logging.exception(e)
                    exceptions_cogs += 1
    logging.info(f"bot -> cogを読み込みました(読み込み済: {loaded_cogs}、 エラー: {exceptions_cogs})")

    logging.info(f"bot -> {bot.user}に接続しました！やったのだー！ ")
    await tree.sync()
    logging.info("bot -> コマンドツリーを同期しました")

    try:
        # APIを起動
        subprocess.Popen(R"python modules\api.py", shell=True)
        logging.info(f'main -> APIサーバーを起動')
    except:
        logging.exception(f'main -> APIサーバーの起動に失敗')

    if PROMETHEUS:
        try:
            # Prometheus Clientを起動
            prometheus.start(5001)
            logging.info(f'main -> Prometheus Clientを起動')
        except:
            logging.exception(f'main -> Prometheus Clientの起動に失敗')

# クライアントの実行
if type(TOKEN)==str:
    bot.run(TOKEN)
else:
    logging.error("settings -> トークンの読み込みに失敗しました。.envファイルがあるか、正しく設定されているか確認してください。")

