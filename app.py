import os
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# ⚠️ 請在下方填入您的 LINE 機器人金鑰
CHANNEL_ACCESS_TOKEN = 'wXxkJ8bWop2nituxGEyPw13jGiiBEJQjvVJq6zdFLpt098lFEM8QcoIHbWJmePw1Kxlo/EswI8zb4Vhq8yefaB06mUQe8/M+pyFpRKIS9l4YrTFE31hMoyuN/51hQLXpgmkB2XCfdx0eHeNQXt4DbwdB04t89/1O/w1cDnyilFU='
CHANNEL_SECRET = '60bbf9a1a1bcbd6cfb59adaf0b9dca06'

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    if user_msg.isdigit():
        address = int(user_msg)
        address = max(0, min(address, 65535))
        
        # 準備填入 Flex Message 的動態內容字典
        flex_data = {"address": str(address)}
        
        # 1. 計算 RIGHT DIP (2^0 ~ 2^7)
        for i in range(8):
            bit = (address >> i) & 1
            flex_data[f"R{i}"] = "ON" if bit == 1 else " · "
            flex_data[f"C{i}"] = "#E63946" if bit == 1 else "#CCCCCC" # ON為紅色，OFF為灰色
            
        # 2. 計算 LEFT DIP (2^8 ~ 2^15)
        for i in range(8, 16):
            bit = (address >> i) & 1
            flex_data[f"L{i}"] = "ON" if bit == 1 else " · "
            flex_data[f"C{i}"] = "#007AFF" if bit == 1 else "#CCCCCC" # ON為藍色，OFF為灰色

        # 動態將計算好的顏色和狀態塞入圖形版型中
        flex_contents = {
          "type": "bubble",
          "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
              {"type": "text", "text": "16-bit DIP Switch 狀態", "weight": "bold", "size": "xl"},
              {"type": "text", "text": f"十進位地址: {flex_data['address']}", "size": "sm", "color": "#666666", "margin": "md"},
              {"type": "separator", "margin": "lg"},
              {"type": "text", "text": "LEFT DIP (高位 2^8 ~ 2^15)", "weight": "bold", "size": "sm", "margin": "lg", "color": "#007AFF"},
              {
                "type": "box", "layout": "horizontal", "margin": "md",
                "contents": [
                  {"type": "text", "text": flex_data["L8"], "align": "center", "weight": "bold", "color": flex_data["C8"]},
                  {"type": "text", "text": flex_data["L9"], "align": "center", "weight": "bold", "color": flex_data["C9"]},
                  {"type": "text", "text": flex_data["L10"], "align": "center", "weight": "bold", "color": flex_data["C10"]},
                  {"type": "text", "text": flex_data["L11"], "align": "center", "weight": "bold", "color": flex_data["C11"]},
                  {"type": "text", "text": flex_data["L12"], "align": "center", "weight": "bold", "color": flex_data["C12"]},
                  {"type": "text", "text": flex_data["L13"], "align": "center", "weight": "bold", "color": flex_data["C13"]},
                  {"type": "text", "text": flex_data["L14"], "align": "center", "weight": "bold", "color": flex_data["C14"]},
                  {"type": "text", "text": flex_data["L15"], "align": "center", "weight": "bold", "color": flex_data["C15"]}
                ]
              },
              {
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                  {"type": "text", "text": "8", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "9", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "10", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "11", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "12", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "13", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "14", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "15", "align": "center", "size": "xs", "color": "#aaaaaa"}
                ]
              },
              {"type": "separator", "margin": "lg"},
              {"type": "text", "text": "RIGHT DIP (低位 2^0 ~ 2^7)", "weight": "bold", "size": "sm", "margin": "lg", "color": "#E63946"},
              {
                "type": "box", "layout": "horizontal", "margin": "md",
                "contents": [
                  {"type": "text", "text": flex_data["R0"], "align": "center", "weight": "bold", "color": flex_data["C0"]},
                  {"type": "text", "text": flex_data["R1"], "align": "center", "weight": "bold", "color": flex_data["C1"]},
                  {"type": "text", "text": flex_data["R2"], "align": "center", "weight": "bold", "color": flex_data["C2"]},
                  {"type": "text", "text": flex_data["R3"], "align": "center", "weight": "bold", "color": flex_data["C3"]},
                  {"type": "text", "text": flex_data["R4"], "align": "center", "weight": "bold", "color": flex_data["C4"]},
                  {"type": "text", "text": flex_data["R5"], "align": "center", "weight": "bold", "color": flex_data["C5"]},
                  {"type": "text", "text": flex_data["R6"], "align": "center", "weight": "bold", "color": flex_data["C6"]},
                  {"type": "text", "text": flex_data["R7"], "align": "center", "weight": "bold", "color": flex_data["C7"]}
                ]
              },
              {
                "type": "box", "layout": "horizontal", "margin": "xs",
                "contents": [
                  {"type": "text", "text": "0", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "1", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "2", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "3", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "4", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "5", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "6", "align": "center", "size": "xs", "color": "#aaaaaa"},
                  {"type": "text", "text": "7", "align": "center", "size": "xs", "color": "#aaaaaa"}
                ]
              }
            ]
          }
        }
        
        reply_message = FlexMessage(alt_text="DIP Switch 狀態計算結果", contents=FlexContainer.from_dict(flex_contents))
        
    else:
        from linebot.v3.messaging import TextMessage
        reply_message = TextMessage(text="請輸入想要轉換的十進位地址數字（例如：1023）")

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
