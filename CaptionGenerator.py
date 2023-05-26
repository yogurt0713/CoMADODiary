import sys
import torch
from PIL import Image
import requests
from lavis.models import load_model_and_preprocess
from IPython.display import display
import json
from translate import Translate

# classの定義（アップロードした画像のキャプションを推定)


class CaptionGenerator:
    def __init__(self):
        self.image = None
        self.raw_image = None
        self.model = None
        self.vis_processors = None
        self.device = None

    def modelready(self, arg1):

        # arg1にイメージデータを入れる
        img = arg1
        self.raw_image = Image.open(img).convert('RGB')

        # setup device to use
        self.device = torch.device(
            "cuda") if torch.cuda.is_available() else "cpu"
        # we associate a model with its preprocessors to make it easier for inference.
        self.model, self.vis_processors, _ = load_model_and_preprocess(
            name="blip2_t5", model_type="pretrain_flant5xl", is_eval=True, device=self.device
        )
        self.vis_processors.keys()

        """#### prepare the image as model input using the associated processors"""
        self.image = self.vis_processors["eval"](
            self.raw_image).unsqueeze(0).to(self.device)

        print("model ready")

        # ここの戻り値が戻ってきたらプロンプトテキストボックスをreadyにする
        return "ready"

    def generatecap(self, prompt, num_captions=0):
        # 　キャプションの入力があった時にキャプションを生成する
        if num_captions != 0:
            result = self.model.generate(
                {"image": self.image, "prompt": prompt}, num_captions=num_captions)

        else:
            result = self.model.generate(
                {"image": self.image, "prompt": prompt})

        return result


# jsonファイルを読み込んでimageがある場合はキャプションを生成し，captionに追加する
def generateCaption(jsonfile):
    with open(jsonfile, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    cg = CaptionGenerator()
    trans = Translate()

 # forで２回繰り返し
    for i in range(len(data)):
        if data[i]['image'] != None:
            image = data[i]['image']
            cg.modelready(image)
            caption = cg.generatecap("this is an image of")
            jcaption = trans.translate(
                caption, trans.translate_lang[1], trans.translate_lang[0])
            data[i]['caption'] = jcaption
            print(caption)

    with open(jsonfile, 'w', encoding='utf-8-sig') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    jsonfile = sys.argv[1]
    generateCaption(jsonfile)
