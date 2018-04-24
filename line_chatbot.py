import time


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

from my_token import MyToken
from NTUST_API.toeic_vocab import ToeicVocab
from NTUST_API.free_classroom import FreeClassroom
from NTUST_API.crosslink_anaylize import CrosslinkAnaylize


download_time = time.gmtime(time.time())

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = MyToken.CHANNEL_ACCESS_TOKEN
CHANNEL_SECRET = MyToken.CHANNEL_SECRET
ERROR_MSG = """
抱歉，目前查詢課堂的伺服器有點問題，請晚點再試，
或是聯絡電研社粉專，我們會盡快修復。
https://www.facebook.com/ntustcc/
"""

INFO_MSG = """
社課時間為每週一晚上7~9點
地點在電算中心RB-508
因此可不用帶電腦
而且不收社費，也不需事先報名～

預計5/7, 5/14教導如何建置一個server，並且架設一個LINE Chatbot。

台科電研社成立於民國九十七年十二月十九日，宗旨在於推廣資訊教育，隨時掌握科技新知與未來趨勢，匯集校內各種不同科系的人才，透過本社團相互切磋與交流，激勵社員組隊參加各種競賽，激盪出創新的資訊應用，並透過其中尋求創新創業的可能；此外本社團將提供各種資訊研習課程，鼓勵同學報考各種資訊證照，並組成資訊志工服務團隊。

"""

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
# line_bot_api = LineBotApi('YOUR_CHANNEL_ACCESS_TOKEN')
# handler = WebhookHandler('YOUR_CHANNEL_SECRET')




@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == "查詢空教室":
        info = get_free_classroom()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=info))

    elif event.message.text == "本週多益單字":
        link = download_vocab()
        if(link[:4] == "http"):
            link = link.replace("http", "https")
            line_bot_api.reply_message(
                event.reply_token,
                ImageSendMessage(original_content_url=link, preview_image_url=link)
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=ERROR_MSG))

    elif event.message.text == "電研社介紹":
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=INFO_MSG))

    elif len(event.message.text) > 1:
        if event.message.text[0] == "#":
            search_name = event.message.text[1:]
            link, courses = get_crosslink_info(search_name)
            user_id = event.source.user_id
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=courses))
            line_bot_api.push_message(
                user_id,
                ImageSendMessage(original_content_url=link, preview_image_url=link)
            )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text))



@app.route('/')
def homepage():
    return 'Hello, World!'

def download_vocab():
    """
    download toeic vocabulary
    use this link:http://fls.ntust.edu.tw/files/11-1094-5131.php?Lang=zh-tw
    """
    toeic_vocab = ToeicVocab()
    # toeic_vocab.download()
    try:
        return toeic_vocab.get_image_href()
    except Exception as e:
        return ERROR_MSG

def get_free_classroom():
    """
    search free classroom
    use this link:http://stuinfo.ntust.edu.tw/classroom_user/qry_classroom.htm
    """
    free_classroom = FreeClassroom()
    free_rooms = []
    try:
        free_rooms = free_classroom.get_free_classroom()
    except Exception as e:
        return ERROR_MSG
    else:
        info = "目前的時段(本小時)\n可使用的教室為\n"
        if(free_rooms):
            for classroom in free_rooms:
                info += classroom + '\n'
        else:
            info = "母湯喔，這時候還待在學校！"
        return info
    finally:
        pass

def get_crosslink_info(search_name):
    '''
    search_name : string 想搜尋的人名
    return 
        image_link :str
        courses :str

        image_link => crosslink上的個人網址
        courses => crosslink上的課程資訊
    '''
    
    CA = CrosslinkAnaylize()
    profile_link = CA.search_whos_profile(search_name)
    print(profile_link)
    # print(profile_link)
    image_link = CA.get_profile_image_href(profile_link)
    courses = CA.get_profile_courses(profile_link)
    return (image_link, courses)

    
if __name__ == "__main__":
    # import imp,os
    # imp.reload(CrosslinkAnaylize)
    app.run()
    