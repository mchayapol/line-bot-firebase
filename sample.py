from __future__ import unicode_literals

import errno
import os
import sys
import tempfile
from argparse import ArgumentParser
from flask import Flask, request, abort
import threading
import time
import locale

from linefirebase import (
    LineFirebase
)

import firebase_admin
from firebase_admin import (
    credentials, db
)


from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
databaseURL = os.getenv('DATABASE_URL', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if databaseURL is None:
    print('Specify DATABASE_URL as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

cred = credentials.Certificate('../run/serviceAccountKey.json')
default_app = firebase_admin.initialize_app(cred, {'databaseURL': databaseURL})

lfb = LineFirebase.LineFirebase(line_bot_api, db)


@app.route("/callback", methods=['POST'])
def callback():
    global lfb
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    global lfb

    lfb.save(event)
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextMessage(text="Saved to Firebase"))

    # TODO extract image to save to storage


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    global lfb

    lfb.save(event)
    text = event.message.text.lower()

    if text == 'profile':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='User ID: ' + event.source.user_id
                    ),
                    TextSendMessage(
                        text='Display name: ' + profile.display_name
                    ),
                    TextSendMessage(
                        text='Status message: ' + profile.status_message
                    )
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="Bot can't use profile API without user ID"))
    else:
        # Unknown command
        # Do nothing when you are in group.
        if isinstance(event.source, SourceUser):
            # Handle Webhook verification
            if event.reply_token == "00000000000000000000000000000000":
                return

            # Echo for unknown command
            print("Unhandled command: ", TextSendMessage(text=event.message.text))

            # line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text + '?'))


@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # Handle webhook verification
    if isinstance(event.source, SourceUser):
        if event.reply_token == 'ffffffffffffffffffffffffffffffff':
            return

    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id,
            sticker_id=event.message.sticker_id)
    )


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)

    # print('Default App:', default_app.name)
    # ref = db.reference('/customers')
    # i = 0
    # for c in ref.get():
    #     print(type(c))
    #     obj = ref.child(c)
    #     print(c)
    #     print('\t', obj.child('id').get())
    #     print('\t', obj.child('name').get())
    #     obj.child('name').set(i)
    #     i += 1
    # print(ref.get())
