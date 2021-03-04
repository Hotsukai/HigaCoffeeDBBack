# このリポジトリは?

HigaCoffee のデータベースプロジェクトのバックエンドです。
HigaCoffee ではコーヒーを題材にフロント開発・バックエンド開発・機械学習をやってみたい人を募集しています。

## API 仕様

| URL               | Method | 説明                   | 備考 |
| :---------------- | :----- | :--------------------- | :--- |
| /                 | GET    | hello world            |      |
| /                 | POST   | オウム返し             |      |
| /coffees          | GET    | 条件にあうコーヒー取得 |      |
| /coffees          | POST   | コーヒー登録           |      |
| /reviews          | GET    | レビュー取得           |      |
| /reviews          | POST   | レビュー登録           |      |
| /auth/login       | POST   | ログイン               |      |
| /auth/create_user | POST   | ユーザー登録           |      |
| /beans            | GET    | 豆の種類取得           |      |

## 実行方法

1. 仮想環境作成
   `$ python -m venv venv `
1. 仮想環境有効化
   `$ source venv/bin/activate`
1. パッケージインストール(requirements.txt から)  
   `$ pip install -r requirements.txt `
1. インストール済みのパッケージを requirements.txt に記載
   `pip freeze > requirements.txt`
1. DB 作成
   1. データベースを作成し、URI を環境変数`DATABASE_URI`に保存  
      ※ デフォルトでは higa という PostgreSQL の DB が使われる。この場合 PostgreSQL に higa という DB を作成する必要がある。
1. マイグレーション

   1. (マイグレーションディレクトリ作成)  
      マイグレーション(DB 構造を models と自動で一致させる)するために必要。  
      ただしこのリポジトリではすでに存在しているため不要
      ```
      $ flask db init
      ```
   1. マイグレーションファイル作成  
      「DB 構造をこう変えてくださいね」っていう[ファイル](./migrations/versions)ができる(=マイグレーションファイル)
      ```sh
      $ flask db migrate
      ```
   1. マイグレーション実行  
      マイグレーションファイルに基づいて DB 構造が変更される。
      ```sh
      $ flask db upgrade
      ```

1. [.env.sample](/.env.sample)を参考に.env ファイルを作成。
1. ローカルサーバ立ち上げ  
   `$ python run.py`

## テスト

1. テスト DB 作成。
1. URI を環境変数`TEST_DATABASE_URI`に保存  
   ※ デフォルトでは higa_test という PostgreSQL の DB が使われる。この場合 PostgreSQL に higa_test という DB を作成する必要がある。
1. テスト実行

   ```sh
   # 通常実行
   $ pytest

   # ログありで実行
   $ pytest -v
   
   # 詳細なログありで実行
   $ pytest -vv

   # PASSしたテストもprintを出力
   $ pytest --capture=no
   ```

   `test_*.py`がすべて実行される。  
   ※[base.py](./src/tests/base.py)に記載の処理が test メソッドのたびに行われる。
