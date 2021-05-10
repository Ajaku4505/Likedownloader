import tweepy
import csv
import pandas as pd
import json
import requests
import re
import os
from sys import path
import config

'''
count                           :int型 取得する「いいね」の数。　最大200まで。「取得するいいねがなくなるまで続ける」をコメントアウトから外すと指定した「id」のいいねをapiの上限まで取得できる。
id                              :取得するtwitterIDを指定。例："@takutakumi1"
Save_directory                  :保存ディレクトリまでのパスを入力する。￥マークの入ったパスでもOK。
Name_of_save_folder             :保存フォルダの名称
Number_to_save_in_one_folder    :保存フォルダに保存する画像の数を指定。
'''

count = 100
id = "@Ajaku4505"
Save_directory = input("plese input Save_directory path:")
Name_of_save_folder = "img"
Number_to_save_in_one_folder = 250


def download_img(url, file_name):  # 「画像のあるURL」と「保存場所まで含めたファイル名」の2つを引数にする、画像保存関数。
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)


def my_makedirs(path):  # パスにファイルが存在しなかったら、ファイルを作成する関数。
    if not os.path.isdir(path):
        os.makedirs(path)


# 保存フォルダの作成関数。「count÷capacity」個分のフォルダを作る。
def Create_folders_according_to_count(count, capacity, directory, folder_name):
    if count % capacity == 0:
        if count//capacity == 0:
            folder_name_number = ""
        else:
            folder_name_number = ((count//capacity))*capacity
        new_dir_path_recursive = "{0}/{1}{2}".format(
            directory, folder_name, folder_name_number)
        my_makedirs(new_dir_path_recursive)


# 保存フォルダまでのディレクトリを作成、値を返す関数。
def Create_directory_name(count, capacity, directory, folder_name):
    if count//capacity != 0:
        folder_name = folder_name+str(((count//capacity))*capacity)
    directory_name = directory+"/"+folder_name+"/"
    return directory_name


def Extract_t_text(tweet):  # ツイートの本文を抜き出し、整形して値を返す関数。
    t_url = tweet.entities["media"][0]["url"]
    t_text = tweet.text
    t_text = t_text.replace('\n', "")
    t_text = t_text.rstrip(t_url)  # Erase extra url
    t_text = re.sub(r'[\\|/|:|?|"|<|>|\|*|]', '-', t_text)
    return t_text


key = config.api_key
key_secret = config.api_key_secret
token = config.access_token
token_secret = config.access_token_secret
"""
認証情報を設定
詳しくはtweepyドキュメント
https://kurozumi.github.io/tweepy/index.html
"""
auth = tweepy.OAuthHandler(key, key_secret)
auth.set_access_token(token, token_secret)
api = tweepy.API(auth)


all_favorites = []  # 空のリストを用意。ここにtweetを貯める。
# 指定したIDのcount分のいいねしたtweetを取得。
latest_favorites = api.favorites(id, count=count)
all_favorites.extend(latest_favorites)

"""
#上限まで取得したいとき、ここのコードをコメントアウトから外す。
while len(latest_favorites)>0:# 取得するいいねがなくなるまで続ける。
    latest_favorites=api.favorites(id,count=200,max_id=all_favorites[-1].id-1)
    all_favorites.extend(latest_favorites)
    
"""

Img_ID = 0
url_DB = pd.DataFrame(columns=["ID",
                               "user_name",
                               "img_url"])  # tweetのURLとimg_IDを保存するデータフレームを作成。

for one_favo in all_favorites:  # 格納したtweetの数だけ実行する。

    if one_favo._json.get("extended_entities") != None:  # 画像があるtweetを分岐。
        t_url = one_favo.entities["media"][0]["url"]
        t_text = Extract_t_text(one_favo)
        t_user_name = one_favo._json['user']['screen_name']
        t_media = one_favo.extended_entities['media']

        for media_number in range(len(t_media)):  # 1つのtweetにある画像の数だけ実行する。
            ns = Number_to_save_in_one_folder
            sd = Save_directory
            nf = Name_of_save_folder
            img_url = t_media[media_number]['media_url']

            Create_folders_according_to_count(Img_ID, ns, sd, nf)
            sd = Create_directory_name(Img_ID, ns, sd, nf)

            savename = "%s.jpg" % (
                str(Img_ID)+"_"+(t_text)+"_"+str(media_number+1))
            savename = sd + savename

            download_img(img_url, savename)  # 画像を保存
            url_DB = url_DB.append({'ID': Img_ID,
                                    'user_name': t_user_name,
                                    'img_url': t_url, }, ignore_index=True)
            Img_ID += 1

url_DB.to_csv(Save_directory+'/url_DB.csv', index=False)  # データフレームをCSVに出力。

