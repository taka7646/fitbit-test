#fitbit-test

fitbitのAPIをproxyするWebアプリのサンプル実装です

## 必要なmodule
* fitbit
* fastapi
* uvicorn
* jinja2
* requests
* sqlalchemy
* gunicorn

## 初期化
* 以下を実行してsqliteのデータベースを初期化します
`db.sqlite3`ファイルが生成されます
```
python init.py
```
* setting.sample.jsonをsetting.jsonにコピーして内容を設定してください
  * client_id, client_secret, redirect_uri を書き換えてください
```json
{
    "client_id": "************",
    "client_secret": "***********************",
    "redirect_uri": "http://localhost:8000/auth/result",
    "scope": "activity heartrate location nutrition profile settings sleep social weight oxygen_saturation respiratory_rate temperature",
    "response_type": "code",
    "end": ""
}
```


## 起動
以下のコマンドで起動してください
```
uvicorn main:app
```
