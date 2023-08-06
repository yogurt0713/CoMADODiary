import subprocess
import json
import sys
import datetime
import time
import os
# mp4ファイルを読み込んで，指定秒ごとに静止画生成


class TimelapseMaker:
    def __init__(self, videoPath, jsonfile, outputDir, interval, starttime):
        self.videoPath = videoPath
        self.jsonfile = jsonfile

        # self.jsonfileのパスを取得して，jsonファイル名をのぞいたパスを取得
        # outputDirの名前のパスがなかったら新しく作成

        self.outputDir = self.jsonfile[:self.jsonfile.rfind('/')]+"/"+outputDir
        self.outputDir = os.path.abspath(self.outputDir)
        if not os.path.exists(self.outputDir):
            os.mkdir(self.outputDir)

        self.interval = interval
        self.starttime = starttime

    def maketimelapse(self):
        output_file = self.outputDir + "/%03d.jpg"
        json_file = self.jsonfile

        # ffmpegでmp4を指定秒ごとに静止画に変換
        command = ['ffmpeg', '-i', self.videoPath,
                   '-vf', f'fps=1/{self.interval}', output_file]
        subprocess.call(command)

        # キャプチャファイルのファイルリストを作成
        file_count = len(os.listdir(self.outputDir))
        file_list = [output_file % (i+1) for i in range(file_count)]
        print(file_list)

        timelapse = []
        # ファイル名と時間をjsonに保存
        # starttimeはUnixtimeで，それにintervalを足していく
        for i in range(len(file_list)):
            time_to_write = self.converttime(i+1)
            data = {'time': time_to_write, 'action': 'scene',
                    'caption': None, 'image': file_list[i]}
            timelapse.append(data)

        with open(json_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)

        updated = existing_data + timelapse
        updated.sort(key=lambda x: x['time'])

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(updated, f, indent=4, ensure_ascii=False)

    # jsonファイルのtimeに共通のISO 8601形式の文字列に時間情報を変更
    def converttime(self, additional_seconds):
        datetime_str = self.starttime
        seconds_to_add = self.interval * additional_seconds
        # convert ISO 8601 to datetime object
        datetime_object = datetime.datetime.strptime(
            datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        # add seconds to datetime object
        datetime_object_new = datetime_object + \
            datetime.timedelta(seconds=seconds_to_add)
        # convert datetime object to ISO 8601 string with microseconds
        time = datetime_object_new.strftime('%Y-%m-%dT%H:%M:%SZ')
        return time


if __name__ == '__main__':
    videoPath = sys.argv[1]
    jsonfile = sys.argv[2]
    outputDir = sys.argv[3]
    interval = 60
    starttime = sys.argv[4]

    tm = TimelapseMaker(videoPath, jsonfile, outputDir, interval, starttime)
    tm.maketimelapse()
