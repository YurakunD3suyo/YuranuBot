# import discord
import os
import logging
import subprocess
import sys
import time

from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
from modules.db_settings import db_load, db_init
from modules.exception import exception_init
from modules.db_vc_dictionary import dictionary_load

logging.basicConfig(level=logging.DEBUG)

# ディレクトリの取得
ROOT_DIR = os.path.dirname(__file__)

# .envから設定値を取得
load_dotenv()
TOKEN = os.getenv("TOKEN")
DIC_DIR = os.getenv("DIC_DIR")
PREFIX = os.getenv("PREFIX")

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
    logging.exception("サーバー「辞書」データベースの読み込みに失敗しました")
    sys.exit()
else:
    logging.debug("Database -> サーバー辞書を読み込みました。")

# サーバー設定読み込み
db_load("database.db")
db_result = db_init()

if db_result==False:
    logging.exception("サーバー「設定」データベースの読み込みに失敗しました")
    sys.exit()
else:
    logging.debug("Database -> サーバー設定を読み込みました。")


### インテントの生成
intents = Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.guilds = True
logging.debug("discord.py -> インテント生成完了")

### クライアントの生成
# bot = discord.Client(intents=intents, activity=discord.Game(name="起きようとしています..."))

if type(PREFIX) == str:
    bot = commands.Bot(command_prefix=PREFIX, intents=intents)
    logging.debug("discord.py -> クライアント生成完了")
else:
    logging.error("dotenv -> .envに「PREFIX」が設定されていません！")
    sys.exit()

#スタート時間を作成
bot.start_time = None

##sendExceptionが利用できるようにする
exception_init(bot)

### コマンドツリーの作成
tree = bot.tree
logging.debug("discord.py -> ツリー生成完了")

@bot.event
async def on_ready():
    exceptions = False

    ##cogファイルを読み込む
    for file in os.listdir(os.path.join(ROOT_DIR, "cogs")):
        if file.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{file[:-3]}")
                logging.info(f'discord.py -> 読み込み完了: {file[:-3]}')
            except Exception as e:
                logging.exception(f'discord.py -> 読み込み失敗: {file[:-3]}')
                logging.exception(e)
                
    try:
        ##jishakuを読み込む
        await bot.load_extension('jishaku')
        logging.info(f'discord.py -> 読み込み完了: jishaku')
    except Exception as e:
        logging.error(f'discord.py -> 読み込み失敗: jishaku')
        logging.error(e)

    try:
        # APIを起動
        logging.info(f'api.py -> APIサーバーを起動')
        subprocess.Popen(R"python modules\api.py", shell=True)
    except:
        logging.exception(f'api.py -> APIサーバーの起動に失敗')

    #稼働時間を表示するために保存する
    bot.start_time = time.time()

    logging.info(f'discord.py -> {bot.user}に接続しました！やったのだー！ ')
    await tree.sync()
    logging.debug("discord.py -> コマンドツリーを同期しました")

    channel_myserv = bot.get_channel(1222923566379696190)
    
    if exceptions == True:
        channel_myserv.send("botは起動しました！\n⚠一部のcogファイルにエラー発生⚠")
    else:
        await channel_myserv.send("botは起動しました！")

# クライアントの実行
if type(TOKEN)==str:
    bot.run(TOKEN)
else:
    logging.error("dotenv -> トークンの読み込みに失敗しました。.envファイルがあるか、正しく設定されているか確認してください。")

