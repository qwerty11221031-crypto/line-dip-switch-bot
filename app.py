import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FlexSendMessage

app = Flask(__name__)

# 這裡換成您在 LINE Developer 取得的金鑰
LINE_CHANNEL_ACCESS_TOKEN = 'wXxkJ8bWop2nituxGEyPw13jGiiBEJQjvVJq6zdFLpt098lFEM8QcoIHbWJmePw1Kxlo/EswI8zb4Vhq8yefaB06mUQe8/M+pyFpRKIS9l4YrTFE31hMoyuN/51hQLXpgmkB2XCfdx0eHeNQXt4DbwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '60bbf9a1a1bcbd6cfb59adaf0b9dca06'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 核心轉換邏輯：將數字轉為符合您定義的高低位 8-bit 字串
def convert_to_dip(num):
    # 確保在 0~65535 之間 (16位元)
    num = max(0, min(num, 65535))
    
    # 1. RIGHT DIP (低位 2^0 ~ 2^7)
    right_bits = []
    for i in range(8):
        right_bits.append(str((num >> i) & 1))
    right_dip = "".join(right_bits)
    
    # 2. LEFT DIP (高位 2^8 ~ 2^15)
    left_bits = []
    for i in range(8, 16):
        left_bits.append(str((num >> i) & 1))
    left_dip = "".join(left_bits)
    
    return left_dip, right_dip

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    # 檢查使用者輸入的是否為純數字
    if user_msg.isdigit():
        address = int(user_msg)
        left_dip, right_dip = convert_to_dip(address)
        
        # 組合回覆訊息 (這裡先用純文字，熟練後可以改成精美的圖形 Flex Message)
        reply_text = (
            f"🔢 十進位地址: {address}\n\n"
            f"⬅️ LEFT DIP (高位):\n{left_dip}\n"
            f"(2^8.........2^15)\n\n"
            f"➡️ RIGHT DIP (低位):\n{right_dip}\n"
            f"(2^0..........2^7)"
        )
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    else:
        # 如果輸入不是數字，給予提示
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text="請輸入想要轉換的十進位地址數字（例如：1023）")
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
