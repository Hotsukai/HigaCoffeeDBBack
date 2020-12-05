# このリポジトリは?

HigaCoffee のデータベースプロジェクトのバックエンドです。
HigaCoffee ではコーヒーを題材にフロント開発・バックエンド開発・機械学習をやってみたい人を募集しています。

# API 仕様

| URL               | Method | 説明                   | 備考 |
| :---------------- | :----- | :--------------------- | :--- |
| /                 | GET    | hello world            |      |
| /                 | POST   | オウム返し             |      |
| /coffees          | GET    | 条件にあうコーヒー取得 |      |
| /coffees          | POST   | コーヒー登録           |      |
| /reviews          | GET    | レビュー取得           |      |
| /reviews          | POST   | レビュー登録           |      |
| /auth/login       | POST   | ログイン               |      |
| /auth/create_user | POST   | 登録                   |      |

# 実行方法

1. 仮想環境作成・有効化  
   `$ python -m venv venv `  
   `$ source venv/bin/activate`
1. 関連パッケージインストール  
   `$ pip install -r requirements.txt `
1. migrate

   1. マイグレーションリポジトリ作成  
      ※マイグレーション(DB 構造を models と自動で一致させる)するために必要  
      `$ flask db init`
   1. マイグレーション作成  
      「DB 構造をこう変えてくださいね～」っていうファイルができる  
      `$ flask db migrate`
   1. マイグレーション実行  
      `$ flask db upgrade`

1. ローカルサーバ立ち上げ  
   `$ python run.py`
