from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage,
    Template, ConfirmTemplate,PostbackAction,MessageAction,URIAction,PostbackEvent,DatetimePickerAction,
    ButtonsTemplate,CarouselTemplate
)
import json
from datetime import datetime, timedelta, timezone

JST = timezone(timedelta(hours=+9), 'JST')
liff_uri = 'line://app/1579181659-kK0nxD7v'

class pine_controller:

    def __init__(self):
        self.__load_json()

    def __load_json(self):
        with open('./field.json') as f:
            self.df = json.load(f)
    
    def __save_json(self):
        with open('./field.json', 'w') as f:
            json.dump(self.df, f, indent=4)

    def sprinkle_water(self, action):
        now = datetime.now(JST).strftime("%H:%M")
        after_hour = (datetime.now(JST) + timedelta(hours=1)).strftime("%H:%M")
        target = self.df["target"]
        self.df["target"] = "none"
        if action == "start":
            if self.df[target]["state"] == "off" :
                self.df[target]["state"] = "on"
                self.df[target]["start"] = now
                self.df[target]["stop"] = after_hour
                self.__save_json()
                return self.df[target]["name"] + "の散水を開始しました\n(1時間で自動停止)"
            else:
                return self.df[target]["name"] + "はすでに散水中です\n(" + self.df[target]["stop"] + "まで)"
        elif action == "stop":
            if self.df[target]["state"] == "on":
                self.df[target]["state"] = "off"
                self.df[target]["stop"] = ""
                self.__save_json()
                return self.df[target]["name"] + "の散水を停止しました"
            else:
                return self.df[target]["name"] + "は散水していません"

    def postback(self,data):
        action = data["action"][0]
        field  = data["field"][0]

        if action == 'set':
            self.df["target"] = field
            self.__save_json()
            return TextSendMessage(text=self.df[field]["name"] + "を指定しました")
        elif action == 'start' or action == 'stop':
            return TextSendMessage(text=self.sprinkle_water(action))
        else:
            self.df["target"] = "none"
            self.__save_json()
            return TextSendMessage(text="何もしません")


    def reply_message(self, message):
        if message == "ヘルプ":
            return_text = [TextSendMessage(text="新城パインの使い方\n\n" + \
                            "■ 設定を確認する\n────────────\n" + \
                            "３つの畑の散水状況とタイマーの設定をいつでも確認することができます。"),
                           TextSendMessage(text="■ 畑を選ぶ\n────────────\n" + \
                            "スプリンクラー操作を行う畑の指定です。畑を指定すると、次の３つの操作が可能となります\n" + \
                            "・水をまく\n・水をとめる\n・タイマーの設定"),
                           TextSendMessage(text="■ 水をまく\n────────────\n" + \
                            "「畑を選ぶ」で指定した畑のスプリンクラーを動かして水をまきます。１時間経つと自動停止します"),
                           TextSendMessage(text="■ 水をとめる\n────────────\n" + \
                            "「畑を選ぶ」で指定した畑のスプリンクラーの散水を止めます"),
                           TextSendMessage(text="■ タイマーの設定\n────────────\n" + \
                            "「畑を選ぶ」で指定した畑の自動水まきタイマーを設定することができます。タイマーを設定すると、毎日指定した日時に水をまきます")]
            return return_text
        elif message == "タイマー設定":
            return TemplateSendMessage(
            alt_text='Field Selection',
                template=ButtonsTemplate(
                    title="タイマー設定",
                    text="入力フォームから入力してください",
                    actions=[
                        URIAction(
                            label='入力フォームを開く',
                            uri=liff_uri
                        ),
                    ]
                )
            )
        elif message == "設定確認":
            return_text = ""
            for field in ["ue","shita","ura"]:
                if self.df[field]["state"] == "on":
                    state = "散水中 \n(" + self.df[field]["stop"] + "まで)"
                elif self.df[field]["start"] != "":
                    state = "止水中 \n(前回は" + self.df[field]["start"] + "に散水)"
                else:
                    state = "止水中"

                if self.df["timer"][field]["state"] == "off":
                    timer = "タイマー未設定"
                else:
                    timer = "タイマー:" + self.df["timer"][field]["run"]

                return_text += "■" + self.df[field]["name"] + "■\n" + \
                               "────────────\n" + state + "\n" + timer + "\n\n"
            
            return TextSendMessage(text=return_text.rstrip())
        elif message == "畑指定":
            return TemplateSendMessage(
                alt_text='Field Selection',
                template=ButtonsTemplate(
                    title="畑を選ぶ",
                    text="指定する畑を選んでください",
                    actions=[
                        PostbackAction(
                            label='上の畑',
                            data='action=set&field=ue'
                        ),
                        PostbackAction(
                            label='下の畑',
                            data='action=set&field=shita'
                        ),
                        PostbackAction(
                            label='裏の畑',
                            data='action=set&field=ura'
                        )
                    ]
                )
            )
        elif message == "散水" or message == "止水":
            if self.df["target"] != "none":
                if message == "散水":
                    message = 'に水を撒きますか？'
                    action = 'start'
                else:
                    message = 'の水を止めますか？'
                    action = 'stop'

                return TemplateSendMessage(
                    alt_text='Confirm template',
                    template=ConfirmTemplate(
                        text=self.df[self.df["target"]]["name"] + message,
                        actions=[
                            PostbackAction(
                                label='Yes',
                                data='action=' + action + '&field=' + self.df["target"]
                            ),
                            PostbackAction(
                                label='No',
                                data='action=none&field=none'
                            )
                        ]
                    )
                )
            else:
                return TextSendMessage(text="畑が指定されていません")

        else:
            messages = message.split("\n")
            if messages[1] == "上の畑":
                target = "ue"
            elif messages[1] == "下の畑":
                target = "shita"
            else:
                target = "ura"

            if messages[0] == "タイマーを設定してください":
                self.df["timer"][target]["state"] = "on"                
                self.df["timer"][target]["run"] = messages[2]                
                self.__save_json()
                return TextSendMessage(text=messages[1] + "のタイマーを設定しました")
            elif messages[0] == "タイマーを解除してください":
                self.df["timer"][target]["state"] = "off"                
                self.df["timer"][target]["run"] = ""                
                self.__save_json()
                return TextSendMessage(text=messages[1] + "のタイマーを解除しました")


            else:
                return TextSendMessage(text="ちょっと何言っているか分かりません")
    
    def push_agent(self):
        pass

