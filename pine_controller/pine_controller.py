class pine_controller:
    def __init__(self,target=""):
        self.target = target
        self.return_text = "それはできません。ごめんなさい。"        

    def get_target(self):
        return self.target
    
    def message(self, message):
        if message == "ヘルプ":
            self.return_text = "ヘルプはまだない"
        elif message == "設定確認":
            self.return_text = "JSONを読んで加工して返そうと思っている"
        elif message == "畑指定":

            self.return_text = "畑を"
            