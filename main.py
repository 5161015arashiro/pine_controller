from __future__ import unicode_literals

import os
import sys
import json
from argparse import ArgumentParser
import urllib

from flask import Flask, request, abort, render_template

from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage,
    Template, ConfirmTemplate,PostbackAction,MessageAction,PostbackEvent,
    ButtonsTemplate
)

from pine_controller import pine_controller

channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)
pine = pine_controller()

app = Flask(__name__)

@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route("/callback", methods=['POST'])
# def callback(request):
def callback():
    # if request.query.liff is not None:
    #     return render_template('timer.html')
    # else:
    # print(dir(request.method))
    signature = request.headers['X-Line-Signature']
    # get request body as textvagra
    body = request.get_data(as_text=True)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        exit()

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:

        if isinstance(event , PostbackEvent):
            
            line_bot_api.reply_message(
                event.reply_token,
                pine.postback(urllib.parse.parse_qs(event.postback.data))
            )
        
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessage):
            line_bot_api.reply_message(
                event.reply_token,
                pine.reply_message(event.message.text)
            )

    return 'OK'

@app.route("/liff", methods=['GET'])
def liff():
    return render_template('timer.html')

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8080, help='port')
    arg_parser.add_argument('-d', '--debug', default=True, help='debug')
    options = arg_parser.parse_args()

    # app.run(debug=options.debug, port=options.port, host="0.0.0.0")
    app.run(host='127.0.0.1', port=8080, debug=True)