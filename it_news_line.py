# ---- ライブラリ宣言 ----

import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from linebot import LineBotApi
from googletrans import Translator  # 追加
from linebot.models import TextSendMessage

# 環境変数読み込み
load_dotenv()

# --- 設定情報 ---
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN") # LINEのアクセストークン
NEWS_API_KEY = os.getenv("NEWS_API_KEY")           # NewsAPIのキー


# 送信先ID（自分のユーザーID）。LINE Developersのチャネル基本設定から確認可能
USER_ID = os.getenv("USER_ID") 

# 取得テスト
print(LINE_ACCESS_TOKEN)
print(NEWS_API_KEY)
print(USER_ID)


def get_it_news():
    """今日（または昨日）のニュースを取得する"""
    # 実行時の日付を取得（例: 2026-01-01）
    # 無料プランでは「今日」のニュースがまだ反映されていないことがあるため、
    # 1日前（昨日）から今日までの範囲を指定するのが確実です。
    
    """ニュースを取得して日本語に翻訳する"""
    translator = Translator() # 翻訳器の準備
    
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 日付を動的に埋め込む
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"q=technology&"
        # f"country=jp&"
        f"from={yesterday}&"
        f"to={today}&"
        f"sortBy=popularity&"
        f"apiKey={NEWS_API_KEY}"
    )
    
    response = requests.get(url).json()
    
    # デバッグ用：APIからどんな応答が来ているか確認（不要になったら消してください）
    # print(f"DEBUG: Status -> {response.get('status')}")
    # print(f"DEBUG: TotalResults -> {response.get('totalResults')}")
    
    articles = response.get("articles", [])[:5]  # 最新5件を取得
    
    if not articles:
        return "ニュースが見つかりませんでした。"
    
    msg = "【本日のITニュース（翻訳済）】\n\n"
    
    for i, article in enumerate(articles, 1):
        original_title = article['title']
        url = article['url']
        
        try:
            # 日本語に翻訳 (dest='ja' で日本語指定)
            translated = translator.translate(original_title, dest='ja').text
        except Exception:
            # 翻訳に失敗した場合は元のタイトルを使う
            translated = original_title
            
        msg += f"{i}. {translated}\n{url}\n\n"
        
    return msg.strip()

def send_line_notification(message):
    """LINEにメッセージを送信する"""
    line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=message))
        print("LINEに通知を送信しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    news_content = get_it_news()
    send_line_notification(news_content)