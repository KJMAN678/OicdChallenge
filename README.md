### Devin

- [Devin's Machine](https://app.devin.ai/workspace) でリポジトリ追加

#### 1.Git Pull
- そのまま

#### 2.Configure Secrets
```sh
# 環境変数用のファイル作成
$ touch .envrc
$ cp .envrc.example .envrc

# .envrc を適宜更新

# 環境変数を読み込む
$ direnv allow
```

- ローカル用
```sh
$ brew install direnv
```
#### 4.Maintain Dependencies
```sh
$ docker compose up -d

# コンテナ作り直し
$ source remake_container.sh
```

#### 5.SetUp Lint
```sh
$ docker compose -f run --rm backend uv run ruff check .
```

#### 6.SetUp Tests
- no tests ran in 0.00s だと Devin の Verify が通らないっぽい
```sh
$ docker compose -f run --rm backend uv run pytest
```

### 7.Setup Local App

```sh
$ http://localhost:8000/ がバックエンドのURL
```

## OIDC認証設定

### 必要な環境変数

このプロジェクトでは、KeyCloak + django-allauth を使用したOIDC認証を実装しています。以下の環境変数が必要です：

#### 基本設定
| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|-------------|------|
| `DJANGO_SECRET_KEY` | Django秘密鍵 | - | ✅ |
| `POSTGRES_DB` | PostgreSQLデータベース名 | - | ✅ |
| `POSTGRES_USER` | PostgreSQLユーザー名 | - | ✅ |
| `POSTGRES_PASSWORD` | PostgreSQLパスワード | - | ✅ |

#### KeyCloak設定
| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|-------------|------|
| `KEYCLOAK_SERVER_URL` | KeyCloakサーバーURL | `http://localhost:8080` | ✅ |
| `KEYCLOAK_REALM` | KeyCloakレルム名 | `myrealm` | ✅ |
| `KEYCLOAK_CLIENT_ID` | KeyCloakクライアントID | `django-client` | ✅ |
| `KEYCLOAK_CLIENT_SECRET` | KeyCloakクライアントシークレット | - | ✅ |
| `KEYCLOAK_ADMIN_USERNAME` | KeyCloak管理者ユーザー名 | `admin` | ✅ |
| `KEYCLOAK_ADMIN_PASSWORD` | KeyCloak管理者パスワード | `admin` | ✅ |

#### Google OAuth2設定（KeyCloak Identity Provider用）
| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|-------------|------|
| `GOOGLE_OAUTH2_CLIENT_ID` | Google OAuth2クライアントID | - | ⚠️ |
| `GOOGLE_OAUTH2_CLIENT_SECRET` | Google OAuth2クライアントシークレット | - | ⚠️ |

⚠️ Googleソーシャルログインを使用する場合は必須

#### AWS OIDC設定（オプション）
| 環境変数名 | 説明 | デフォルト値 | 必須 |
|-----------|------|-------------|------|
| `AWS_OIDC_ISSUER_URL` | AWS OIDC発行者URL | - | ❌ |
| `AWS_OIDC_CLIENT_ID` | AWS OIDCクライアントID | - | ❌ |
| `AWS_OIDC_CLIENT_SECRET` | AWS OIDCクライアントシークレット | - | ❌ |

#### 3. KeyCloak初期設定
```sh
# KeyCloak設定コマンド実行
$ docker compose run --rm web uv run manage.py setup_keycloak

# Google OAuth2認証情報を指定する場合
$ docker compose run --rm web uv run python manage.py setup_keycloak \
  --google-client-id GOOGLE_OAUTH2_CLIENT_ID \
  --google-client-secret GOOGLE_OAUTH2_CLIENT_SECRET
```

### アクセスURL

- **Django アプリケーション**: http://localhost:8000
- **KeyCloak管理コンソール**: http://localhost:8080/admin
  - ユーザー名: `admin` (環境変数で変更可能)
  - パスワード: `admin` (環境変数で変更可能)

- http://localhost:8080/admin にアクセス
- myrealm レルムを選択
- Clients → django-client を選択
- Credentials タブでClient Secretを確認
- 環境変数に設定
  - export KEYCLOAK_CLIENT_SECRET="<KeyCloakから取得したシークレット>"

#### django-clientの作成手順

1. クライアントの作成開始
- 「Create client」ボタンをクリック

2. General Settings
- Client type: OpenID Connect を選択
- Client ID: django-client と入力（正確に）
- 「Next」をクリック

3. Capability config
- Client authentication: ON に設定（これでConfidentialクライアントになります）
- Authorization: OFF のまま

4. Login settings
- Valid redirect URIs: 以下の2つを追加
http://localhost:8000/*

- Web origins: 以下の2つを追加

http://localhost:8000

- 「Save」をクリック

5. Client Secretの取得
- 保存後、「Credentials」タブをクリック
- Client secretの値をコピーして環境変数 export KEYCLOAK_CLIENT_ID=xxx を更新

### Google OAuth2設定

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクト作成
2. APIs & Services > Credentials で OAuth 2.0 Client ID を作成
3. 承認済みリダイレクト URI に以下を追加:
   ```
   http://localhost:8080/realms/myrealm/broker/google/endpoint
   ```
4. クライアントIDとシークレットを環境変数に設定

### AWS OIDC設定（オプション）

1. AWS IAM Identity Center でアプリケーション作成
2. OIDC設定を取得
3. 環境変数に設定

### トラブルシューティング

#### KeyCloakに接続できない
```sh
# KeyCloakログ確認
$ docker compose logs keycloak

# KeyCloakサービス再起動
$ docker compose restart keycloak
```

#### Django設定エラー
```sh
# Django設定チェック
$ docker compose run --rm web uv run python manage.py check

# 詳細なエラー情報
$ docker compose run --rm web uv run python manage.py check --deploy
```

#### Additional Notes
- 必ず日本語で回答してください
- Python, Django を利用する
- データベースは Postgres
- テストは pytest を利用する
を入力
