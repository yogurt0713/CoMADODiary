import json
import sys


def convertCoMADOJson(filename, convertedfilename, imagePath):
    # jsonファイルを読み込んで新しいjsonフォーマットに変換する
    with open(filename, 'r') as f:
        data = json.load(f)

    # 新しいjsonフォーマットに変換
    diary = []
    for i in range(len(data)):
        save = data[i]['action']
        if save == 'ふせん':
            action = 'note'

        if save == '指差し':
            action = 'point'

        if save == 'ふせん' or save == '指差し':
            time = data[i]['time']
            caption = data[i]['noteText']
            image = imagePath + '/' + data[i]['image']

            diary.append({'time': time, 'action': action,
                          'caption': caption, 'image': image})

    print(diary)
    with open(convertedfilename, 'w', encoding='utf-8-sig') as f:
        json.dump(diary, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    filename = sys.argv[1]
    convertedfilename = sys.argv[2]
    imagePath = sys.argv[3]
    convertCoMADOJson(filename, convertedfilename, imagePath)
