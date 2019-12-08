# attendance-notifier

### 機能
1. 月曜から金曜の午前9時に
    - 昨日までの労働時間
    - 超過or不足労働時間

    をSlackに投稿する
2. スラッシュコマンド「/today」で今日の出勤時刻をSlackに投稿する
3. スラッシュコマンド「/summary」で1.と同じ内容をSlackに投稿する。


### デプロイ方法

[serverless framework](https://serverless.com)でデプロイして、AWS Lambdaで動かす

まずは設定情報をconfig.jsonに書き込む

```
cp config.sample.json config.json
```

config.jsonの中身
```
{
    "url": "勤怠管理ページのログインURL",
    "company_id": "会社ID",
    "user_id": "ユーザーID",
    "password": "パスワード",
    "token": "Slack Appのトークン",
    "verification_token": "Slackの検証用トークン",
    "channel_id": "投稿先のSlackチャンネルID",
    "python_bin": "pythonのpath"
}
```

実行にはseleniumのlayerが必要となるので用意する。

設定が終わったら

```
sls deploy
```

でデプロイ
