import subprocess
import json
import sys
import datetime
import time
import os
# mp4ファイルを読み込んで，指定秒ごとに静止画生成


def generateTimelapse(videoPath, jsonfile, outputDir, interval, starttime):
    output_file = outputDir + "/%03d.jpg"
    json_file = jsonfile

    # ffmpegでmp4を指定秒ごとに静止画に変換
    command = ['ffmpeg', '-i', videoPath,
               '-vf', f'fps=1/{interval}', output_file]
    subprocess.call(command)

    # キャプチャファイルのファイルリストを作成
    file_count = len(os.listdir(outputDir))
    file_list = [output_file % (i+1) for i in range(file_count)]
    print(file_list)

    timelapse = []
    # ファイル名と時間をjsonに保存
    # starttimeはUnixtimeで，それにintervalを足していく
    for i in range(len(file_list)):
        time_to_write = convertTime(starttime, interval, i+1)
        data = {'time': time_to_write, 'action': 'scene',
                'caption': None, 'image': file_list[i]}
        timelapse.append(data)

    with open(json_file, 'r', encoding='utf-8-sig') as f:
        existing_data = json.load(f)

    updated = existing_data + timelapse
    updated.sort(key=lambda x: x['time'])

    with open(json_file, 'w', encoding='utf-8-sig') as f:
        json.dump(updated, f, indent=4, ensure_ascii=False)


def convertTime(starttime, interval, num_of_seconds):
    datetime_str = starttime
    seconds_to_add = interval * num_of_seconds
    # convert ISO 8601 to datetime object
    datetime_object = datetime.datetime.strptime(
        datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # add seconds to datetime object
    datetime_object_new = datetime_object + \
        datetime.timedelta(seconds=seconds_to_add)
    # convert datetime object to ISO 8601 string without microseconds
    time = datetime_object_new.strftime('%Y-%m-%dT%H:%M:%SZ')
    return time


if __name__ == '__main__':
    videoPath = sys.argv[1]
    jsonfile = "test.json"
    outputDir = "video"
    interval = 60
    starttime = "2023-03-08T03:29:00.000Z"
    generateTimelapse(videoPath, jsonfile, outputDir, interval, starttime)
