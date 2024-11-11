from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FollowEvent, FlexMessage, FlexSendMessage
)
import os

app = Flask(__name__)

# Azure App Serviceの環境変数から読み込み
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/")
def hello():
    return "LINE Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    welcome_message = TextSendMessage(text=f"""こんにちは、{profile.display_name}さん！
友だち追加ありがとうございます。

このBotでは以下のサービスをご利用いただけます：
・予約の確認
・営業時間の確認
・お問い合わせ

下のメニューからお選びください。""")
    
    line_bot_api.reply_message(event.reply_token, welcome_message)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    
    if text == "予約":
        reply_text = "予約はこちらから！\nhttps://your-booking-site.com"
    elif text == "営業時間":
        reply_text = "営業時間：10:00-20:00\n定休日：毎週水曜日"
    else:
        reply_text = "ご質問は下のメニューからお選びください。"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()