from PIL import Image, ImageDraw, ImageFont, ImageFilter
from discord.ext import commands
from io import BytesIO
from modules.pc_status import PCStatus
import os
import time
import requests
import discord

# フォントのパスを設定
welcome_img = os.path.join('images', 'welcome.png')

def make_welcome_image(user: discord.Member, guild: discord.Guild):
    # 画像のサイズを設定
    width, height = 1280, 720

    # ベースの画像を読みこむ
    base = Image.open(welcome_img).convert("RGBA")

    # 描画オブジェクトを作成
    main = ImageDraw.Draw(base)

    ### アイコン画像の生成###
    # URLからアイコン画像を取得
    response = requests.get(user.avatar.url)
    icon_ = Image.open(BytesIO(response.content)).convert("RGBA")

    #config
    icon_size = (280,280)
    icon_border = 10

    #リサイズ
    icon_ = icon_.resize(icon_size)

    # サイズを取得
    i_width, i_height = icon_.size
    min_size = min(i_width, i_height)

    #アイコンのポジションを取得
    icon_pos = (int(width/2-i_width/2), int(height*0.12))
    border_pos = (int(icon_pos[0]-icon_border), int(icon_pos[1]-icon_border))

    # 正方形にトリミング
    left = (i_width - min_size) // 2
    top = (i_height - min_size) // 2
    right = (i_width + min_size) // 2
    bottom = (i_height + min_size) // 2
    icon_ = icon_.crop((left, top, right, bottom))


    #アイコンのボーダーを作る
    border = Image.new("RGB", (min_size+icon_border*2, min_size+icon_border*2), 0).convert("RGBA")
    border_ = ImageDraw.Draw(border)
    border_.ellipse((0, 0, min_size+icon_border*2, min_size+icon_border*2), fill=(204,204,204,255))

    # 透明ようマスクとつくる
    mask = Image.new("L", (min_size+icon_border*2, min_size+icon_border*2), 0)
    draw_ = ImageDraw.Draw(mask)
    draw_.ellipse((0, 0, min_size+icon_border*2, min_size+icon_border*2), fill=255)

    # ボーダーを生成
    base.paste(border, border_pos, mask)
    

    # 円形のマスクを作成
    mask = Image.new("L", (min_size, min_size), 0)
    draw_ = ImageDraw.Draw(mask)
    draw_.ellipse((0, 0, min_size, min_size), fill=255)
    
    # マスクを適用+画像に張り付け
    base.paste(icon_, icon_pos, mask)


    # フォントのパスを設定
    font_semi = os.path.join('fonts', 'Koruri-Semibold.ttf')
    font_bold = os.path.join('fonts', 'Koruri-Bold.ttf')

    # フォントサイズを指定
    font_size = 80
    font = ImageFont.truetype(font_bold, font_size)

    # ユーザーテキストの生成
    text = user.global_name
    text_color = (255, 255, 255)  # 黒
    text_position = (width/2, height*0.67)

    # テキストを画像に描画
    main.text(text_position, text, fill=text_color, font=font, anchor="mm")


    # フォントサイズを指定
    font_size = 45
    font = ImageFont.truetype(font_semi, font_size)

    # 描画するテキストと位置を設定
    text = f"{guild.name}へようこそなのだ！"
    text_position = (width/2, height*0.82)

    # テキストを画像に描画
    main.text(text_position, text, fill=text_color, font=font, anchor="mm")

    # 画像を保存
    name = f'welcome-{guild.id}.png'

    output_path = os.path.join("images", name)

    base.save(output_path)

    return output_path, name
