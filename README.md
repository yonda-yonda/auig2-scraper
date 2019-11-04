# AUIG2スクレイピング

## palsar2.py
シーン詳細を取得しローカルに保存する。  
ファイルは1日単位で作成される。  

## 使い方
AUIG2がSilverlightで構築されているためwindowsでのみ動作します。

### Seleniumを使えるようにする
`pip install selenium`

### IEDriverServerをダウンロードする
[https://www.seleniumhq.org/download/](https://www.seleniumhq.org/download/)  
32bitをダウンロードし、解答後パスの通った場所に配置する。

### 実行
`python palsar2.py 2019-01-01 2019-02-01`

`palsar2_{日付}.json`が日付分作成される。  
5000件以上結果が返ってきた、何かしらのエラーが出た場合、`palsar2_{日付}_error.log`というファイルが作成される。

### issue
* 検索期間以外のパラメータも指定できるようにする
* selenium非依存、マルチプラットフォーム化