# splatoon2_stage_recognizer
画像認識を用いてステージ情報を取得するスクリプト  

# 事前準備
- python実行環境  
- twitter開発者権限(APIの実行)  twitter_auth_info.pyに記入

# 主な処理の流れ
- ステージ情報の見本となる画像ファイルを用意（stg_img）  
- 公式のステージ情報ツイートを取得
- ツイートに添付された画像を保存
- 各画像から８ステージを切り出し、見本ファイルとのヒストグラム比較で一致度を解析  
- 一致度が99%の場合は同一と判断し○、99%以下で最も一致度が高い候補を？と判定し出力する

# 実行結果
![image](https://user-images.githubusercontent.com/102900238/166237304-ba98ba0a-c83f-4916-b2c4-e44840f96fce.png)
![image](https://user-images.githubusercontent.com/102900238/166237339-3ecbf9a8-4fa1-4b53-a238-4c1ed4921cd7.png)

# 参考URL
- [tweetから extended_entities が取得できない場合の対策](https://qiita.com/soma_sekimoto/items/65c664f00573284b0b74)
- [2018年6月のステージ情報](https://twitter.com/SplatoonJP/status/1001995245863698432)
