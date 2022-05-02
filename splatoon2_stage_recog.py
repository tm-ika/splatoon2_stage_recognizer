import cv2
import numpy as np
import requests
import tweepy
import datetime
import os
import glob

# 認証用外部ファイルの読み込み
import twitter_auth_info
from bs4 import BeautifulSoup


splat_info = "SplatoonJP"
rules = ["area","yagura","hoko","asari"]
stages = ["ajifry","ama","anchovy","arowana","battera","bbass","chozame","devon","engawa","fujitsubo","gangaze","hakofugu","hokke","kombu","manta","mongara","mozuku","mutsugoro","otoro","shottsuru","sumeshi","tachiuo","zatou"]

url_list = []

area_stage = []
yagura_stage = []
hoko_stage = []
asari_stage = []


stageimg_list = glob.glob("stg_img/*.jpg")
tmpimg_list = []
threshold = 0.99

cut_list = [
   [189, 390, 42, 401],
   [189, 390, 421, 780],
   [189, 390, 800, 1159],
   [189, 390, 1179, 1538],
   [416, 617, 42, 401],
   [416, 617, 421, 780],
   [416, 617, 800, 1159],
   [416, 617, 1179, 1538]
   ]

# Twitterの認証、取得したキーを格納 twitter_auth_info.pyから読み込み
ck = twitter_auth_info.ck   # consumer_key
cs = twitter_auth_info.cs   # consumer_secret
at = twitter_auth_info.at   # access_token
ats = twitter_auth_info.ats # access_token_secret


# フォルダ作成
print("[!] stg_img フォルダにステージ見本データが存在することを確認してください")
if not os.path.exists("stg_img"):
   os.mkdir("stg_img")
if not os.path.exists("tmp_img"):
   os.mkdir("tmp_img")


# Twitter APIの認証情報を設定
auth = tweepy.OAuth1UserHandler(consumer_key=ck, consumer_secret=cs, access_token=at, access_token_secret=ats)
api = tweepy.API(auth)

print("\n[>] Splatoon公式アカウント @" + splat_info+" が発信したステージ情報を確認")
print("[>] タイムラインの検索結果")
tws = api.search_tweets(q="ルールとステージの組み合わせ from:SplatoonJP",result_type="recent",tweet_mode="extended",include_entities=True)
for tw in tws:
   full_url = "https://twitter.com/"+splat_info +"/status/"+tw._json["id_str"]
   tw_id = tw._json["id_str"]
   print("url: " + full_url)
   print("ID : " + tw_id)
   print(tw._json["full_text"])
   #print(tw._json["extended_entities"])


# 解析対象となるツイートの選択
flag = input("\n[?] このIDでOK? " + tw_id + " [Y/N]:")
if flag in "YyＹｙ":
   tw_id = tw_id
else:
   tw_id = input("\n[?] IDを指定してください:")


# ツイート内容の取得
# ツイートが省略されないよう tweet_mode='extended', include_entities=True を付与
tw = api.get_status(id=int(tw_id), tweet_mode='extended', include_entities=True)


# ステージ情報のツイートでない場合、終了
if "ルールとステージの組み合わせ" in tw._json["full_text"]:
   print("[>] ツイート投稿日")
   print(tw.created_at)
   dt1 = tw.created_at
   dt2 = dt1 + datetime.timedelta(days=10)
   dt = str(dt2).split("-")
   timestamp = dt[0] + dt[1] # 2022 + 05
   print("[>] ツイート全文")
   print(tw._json["full_text"])
   
   print("[>] 画像URL")
   for s in tw._json["extended_entities"]["media"]:
      url = s["media_url_https"]
      if url.startswith("https://pbs.twimg.com/media/"):
         url_list.append(url + "?format=jpg&name=large") #通常サイズ:1200x512pxl ラージサイズ:1573x671pxl
         print(url)
else:
   print("[!] 指定したツイートはステージ情報ツイートではありません")
   print("[>] ツイート投稿日")
   print(tw.created_at)
   print("[>] ツイート全文")
   print(tw._json["full_text"])   
   exit()

         
# ツイートから画像を取得し名前を付けて保存
print("\n[>] ツイート内の画像をtmp_imgに保存")
for url,rule in zip(url_list,rules):
   res =requests.get(url)
   cnt = res.content
   file_name = timestamp + "_" + rule+".jpg"
   tmpimg_list.append(file_name)
   with open("tmp_img/" + file_name, "wb") as img:
      img.write(cnt)


# 画像の一致度を解析
# img1:解析対象, img2:解析対象から切り出した部分, img3:ステージ見本
print("[>] 画像の一致度を解析　閾値:" + str(threshold))
for img,rule in zip(tmpimg_list,rules):
   img1 = cv2.imread("tmp_img/" + img)
   i = 1
   for cut in cut_list:
      print("[>] " + rule +":"+str(i)+"番目の画像解析を始めます。解析範囲:"+str(cut))
      img2 = img1[cut[0]:cut[1],cut[2]:cut[3]]
      cv2.imwrite("tmp_img/out.jpg", img2)
      img2 = cv2.imread('tmp_img/out.jpg')
      img2_hist = cv2.calcHist([img2], [0], None, [256], [0, 256])
      ret_stg = ""
      ret_score = 0
      for st in stageimg_list:
         img3 = cv2.imread(st)
         img3_hist = cv2.calcHist([img3], [0], None, [256], [0, 256])
         
         st = st.split("\\")[-1].split(".")[0]
         score = cv2.compareHist(img2_hist, img3_hist, 0)
         if score > ret_score:
            ret_score = score
            ret_stg = st
            
      if ret_score > threshold:
         print("\tTrue:",ret_score,ret_stg)
         if rule == "area":
            area_stage.append(ret_stg)
         elif rule == "yagura":
            yagura_stage.append(ret_stg)
         elif rule == "hoko":
            hoko_stage.append(ret_stg)
         elif rule == "asari":
            asari_stage.append(ret_stg)
      else:
         print("\t!!!!! False:",ret_score,ret_stg)
         if rule == "area":
            area_stage.append(ret_stg+"?")
         elif rule == "yagura":
            yagura_stage.append(ret_stg+"?")
         elif rule == "hoko":
            hoko_stage.append(ret_stg+"?")
         elif rule == "asari":
            asari_stage.append(ret_stg+"?")
      i+=1


print("\n[+] " + timestamp + "エリアステージ")
for st in stages:
   if st in area_stage:
      print(st,"\t○")
   elif st+"?" in area_stage:
      print(st.replace("?",""),"\t？")
   else:
      print(st)
print("\n[+] " + timestamp + "ヤグラステージ")
for st in stages:
   if st in yagura_stage:
      print(st,"\t○")
   elif st+"?" in yagura_stage:
      print(st.replace("?",""),"\t？")
   else:
      print(st)
print("\n[+] " + timestamp + "ホコステージ")
for st in stages:
   if st in hoko_stage:
      print(st,"\t○")
   elif st+"?" in hoko_stage:
      print(st.replace("?",""),"\t？")
   else:
      print(st)
print("\n[+] " + timestamp + "アサリステージ")
for st in stages:
   if st in asari_stage:
      print(st,"\t○")
   elif st+"?" in asari_stage:
      print(st.replace("?",""),"\t？")
   else:
      print(st)

print("\n[+] " + timestamp + "全ステージ")
print(" "+"*"*10+"\tarea\tyagura\thoko\tasari",end="")
for st in stages:
   st_ = (st+"*"*10)[:10]
   print("\n",st_,end="\t")
   if st in area_stage:
      print("○",end="\t")
   elif st+"?" in area_stage:
      print("？",end="\t")
   else:
      print("■",end="\t")
   if st in yagura_stage:
      print("○",end="\t")
   elif st+"?" in yagura_stage:
      print("？",end="\t")
   else:
      print("■",end="\t")
   if st in hoko_stage:
      print("○",end="\t")
   elif st+"?" in hoko_stage:
      print("？",end="\t")
   else:
      print("■",end="\t")
   if st in asari_stage:
      print("○",end="\t")
   elif st+"?" in asari_stage:
      print("？",end="\t")
   else:
      print("■",end="\t")

print("\n○：アリ、？：閾値イカの有力候補、■：ナシ")
