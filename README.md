# このリポジトリは?

HigaCoffee のデータベースプロジェクトのバックエンドです。

# API 仕様

| URL       | Method | 説明           | 備考       |
| :-------- | :----- | :------------- | :--------- |
| /         | GET    | hello world    |            |
| /         | POST   | オウム返し     |            |
| /entries/ | GET    | エントリー一覧 |            |
| /entries/add | POST   | エントリー追加 | title,text |

# 実行方法

1. 仮想環境作成  
   `$ python -m venv venv `
1. 関連パッケージインストール  
   `$ pip install -r requirements.txt `
1. DB 作成  
   `$ python -c "import main.models; main.models.init()"`
1. ローカルサーバ立ち上げ  
   `$ python run.py`
