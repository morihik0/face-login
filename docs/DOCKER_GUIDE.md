# Docker Guide - Face Login System

このガイドでは、Face Login SystemをDockerで実行する方法を説明します。

## 前提条件

- Docker Desktop または Docker Engine がインストールされていること
- Docker Compose がインストールされていること

## クイックスタート

### 1. プロダクション環境での実行

```bash
# イメージをビルドして起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# 停止
docker-compose down
```

アプリケーションは以下のURLでアクセスできます：
- フロントエンド: http://localhost
- バックエンドAPI: http://localhost:5001

### 2. 開発環境での実行

```bash
# 開発用の設定で起動
docker-compose -f docker-compose.dev.yml up -d

# ホットリロード付きで開発
docker-compose -f docker-compose.dev.yml logs -f
```

開発環境のURL：
- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:5001

## Docker構成

### サービス構成

1. **backend** - Flask APIサーバー
   - Python 3.9
   - OpenCV, face_recognition
   - ポート: 5001

2. **frontend** - React アプリケーション
   - Node.js 16
   - Nginx (プロダクション)
   - ポート: 80 (プロダクション), 3000 (開発)

### ボリューム

- `face_images/` - 顔画像の保存
- `face_login.db` - SQLiteデータベース
- `logs/` - アプリケーションログ

### 環境変数

#### Backend
- `FLASK_ENV` - Flask環境 (production/development)
- `DB_PATH` - データベースパス
- `FACE_IMAGES_DIR` - 顔画像保存ディレクトリ
- `LOG_FILE` - ログファイルパス
- `FACE_RECOGNITION_THRESHOLD` - 認証閾値 (デフォルト: 0.6)
- `MAX_FACES_PER_USER` - ユーザーあたりの最大顔数 (デフォルト: 5)

## よく使うコマンド

### ビルド関連

```bash
# イメージを再ビルド
docker-compose build

# キャッシュを使わずに再ビルド
docker-compose build --no-cache

# 特定のサービスのみビルド
docker-compose build backend
```

### 実行・管理

```bash
# バックグラウンドで起動
docker-compose up -d

# ログを表示
docker-compose logs -f

# 特定のサービスのログ
docker-compose logs -f backend

# サービスの状態確認
docker-compose ps

# サービスの再起動
docker-compose restart backend

# 停止（コンテナは削除しない）
docker-compose stop

# 停止してコンテナを削除
docker-compose down

# ボリュームも含めて削除
docker-compose down -v
```

### デバッグ

```bash
# コンテナ内でシェルを実行
docker-compose exec backend bash
docker-compose exec frontend sh

# Pythonシェルを起動
docker-compose exec backend python

# データベースを確認
docker-compose exec backend sqlite3 /app/face_login.db
```

## トラブルシューティング

### 1. ポートが使用中

```bash
# 使用中のポートを確認
lsof -i :5001
lsof -i :80

# 別のポートで起動
# docker-compose.yml を編集してポートを変更
```

### 2. 権限エラー

```bash
# ボリュームの権限を修正
sudo chown -R $USER:$USER face_images/
sudo chown -R $USER:$USER logs/
```

### 3. イメージビルドエラー

```bash
# Dockerのキャッシュをクリア
docker system prune -a

# 再ビルド
docker-compose build --no-cache
```

### 4. メモリ不足

Docker Desktopの設定でメモリ割り当てを増やしてください：
- Mac/Windows: Docker Desktop > Preferences > Resources
- 推奨: 4GB以上

## プロダクション展開

### 1. 環境変数の設定

`.env`ファイルを作成：

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DB_PATH=/app/data/face_login.db
LOG_LEVEL=INFO
```

### 2. HTTPS設定

Nginxの設定を更新してSSL証明書を追加：

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... 他の設定
}
```

### 3. バックアップ

```bash
# データベースのバックアップ
docker-compose exec backend sqlite3 /app/face_login.db .dump > backup.sql

# 顔画像のバックアップ
tar -czf face_images_backup.tar.gz face_images/
```

## セキュリティ考慮事項

1. **本番環境では必ず環境変数を設定**
   - SECRET_KEY
   - 強力なパスワード

2. **ネットワークの分離**
   - フロントエンドとバックエンドは内部ネットワークで通信

3. **ボリュームの権限**
   - 適切なファイル権限を設定

4. **定期的なアップデート**
   - ベースイメージの更新
   - 依存関係の更新

## 監視とログ

### ログの確認

```bash
# リアルタイムログ
docker-compose logs -f

# 過去のログ
docker-compose logs --tail=100

# ログファイルの確認
docker-compose exec backend tail -f /app/logs/face_login.log
```

### リソース使用状況

```bash
# CPU/メモリ使用状況
docker stats

# ディスク使用量
docker system df
```

## まとめ

Dockerを使用することで、Face Login Systemを簡単にデプロイ・管理できます。開発環境と本番環境の切り替えも容易で、スケーラブルな構成が可能です。