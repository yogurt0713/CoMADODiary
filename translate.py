# deepl APIを使って，日本語の文章を英語にしてシステムに渡し，システムからの回答を日本語にして返す

import requests
import json


class Translate:

    translate_lang = ["JA", "EN"]

    def __init__(self):
        self.url = "https://api-free.deepl.com/v2/translate"
        self.auth_key = ""
        self.params = {
            "auth_key": self.auth_key,
            "text": "",
            "source_lang": "",
            "target_lang": ""
        }

    def translate(self, text, source_lang, target_lang):
        self.params["text"] = text
        self.params["source_lang"] = source_lang
        self.params["target_lang"] = target_lang
        response = requests.post(self.url, data=self.params)
        json_data = json.loads(response.text)
        return json_data["translations"][0]["text"]


if __name__ == "__main__":
    trans = Translate()
    text = "Summarize this dialogue in 800 or less words."

    print(trans.translate(
        text, trans.translate_lang[1], trans.translate_lang[0]))
