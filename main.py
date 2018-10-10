from __future__ import unicode_literals

import os

from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from pine_controller import pine_controller
from pine_controller.message import message_type

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

controller = pine_controller("ue")

def callback(request):
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        exit()

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        
        return_text = event.message.text

        if event.message.text == "畑指定":
            return_text = "現在の畑は" + controller.get_target()

        line_bot_api.reply_message(
            event.reply_token,
            # TextSendMessage(text=event.message.text)
            #TextSendMessage(text="あらしろパイン")
            TextMessage(text=return_text)
        )

    return 'OK'