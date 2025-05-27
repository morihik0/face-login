# Roo-code向け顔認証システム開発指示書

## プロジェクト概要

**プロジェクト名**: Face Recognition System  
**説明**: ローカル環境で動作する顔認証システム。ユーザーの顔を登録し、リアルタイムで認証を行うWebアプリケーション。

## 技術スタック指定

### バックエンド
- Python 3.9+
- Flask
- OpenCV
- face_recognition
- SQLite
- NumPy

### フロントエンド
- React.js
- Tailwind CSS
- Axios

### その他
- Docker (コンテナ化)
- WebRTC (カメラアクセス)

## ファイル構成

```
face-recognition-system/
├── backend/
│   ├── app.py                    # メインアプリケーション
│   ├── requirements.txt          # Python依存関係
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # ユーザーモデル
│   │   └── database.py          # データベース設定
│   ├── services/
│   │   ├── __init__.py
│   │   ├── face_detection.py    # 顔検出サービス
│   │   ├── face_recognition.py  # 顔認識サービス
│   │   └── image_processing.py  # 画像処理ユーティリティ
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # 認証API
│   │   ├── users.py             # ユーザー管理API
│   │   └── recognition.py       # 顔認識API
│   └── data/
│       ├── faces/               # 顔画像保存ディレクトリ
│       └── database.db          # SQLiteデータベース
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.js               # メインコンポーネント
│   │   ├── components/
│   │   │   ├── Camera.js        # カメラコンポーネント
│   │   │   ├── UserRegistration.js  # ユーザー登録
│   │   │   ├── FaceAuthentication.js # 顔認証
│   │   │   ├── Dashboard.js     # ダッシュボード
│   │   │   └── UserList.js      # ユーザー一覧
│   │   ├── services/
│   │   │   └── api.js           # API通信
│   │   └── utils/
│   │       └── camera.js        # カメラユーティリティ
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

## 詳細な実装指示

### 1. バックエンド実装

#### `app.py` (メインアプリケーション)

```python
# 以下の機能を実装してください:
# - Flask アプリケーションの初期化
# - CORS設定
# - データベース初期化
# - ルート登録
# - エラーハンドリング
# - ログ設定

# 必要なライブラリ:
# - Flask
# - Flask-CORS
# - sqlite3
# - logging
```

**実装要件:**
- Flaskアプリケーションの基本設定
- 環境変数による設定管理
- グローバルエラーハンドラー
- ログレベルの設定（DEBUG, INFO, ERROR）

#### `models/database.py`

**データベース設定とテーブル作成**

**テーブル定義:**

1. **usersテーブル**
   - `id` (PRIMARY KEY)
   - `name` (VARCHAR)
   - `email` (VARCHAR, UNIQUE)
   - `created_at` (TIMESTAMP)
   - `is_active` (BOOLEAN)

2. **face_encodingsテーブル**
   - `id` (PRIMARY KEY)
   - `user_id` (FOREIGN KEY)
   - `encoding` (BLOB) - NumPy配列をバイナリ化
   - `image_path` (VARCHAR)
   - `created_at` (TIMESTAMP)

3. **auth_logsテーブル**
   - `id` (PRIMARY KEY)
   - `user_id` (FOREIGN KEY)
   - `success` (BOOLEAN)
   - `confidence` (REAL)
   - `timestamp` (TIMESTAMP)

#### `services/face_detection.py`

**顔検出サービスの実装**

**機能:**
- `detect_faces(image)`: 画像から顔を検出
- `extract_face_encoding(image)`: 顔の特徴量を抽出
- `validate_face_image(image)`: 顔画像の品質チェック

**使用ライブラリ:** OpenCV, face_recognition

**エラーハンドリング:**
- 顔が検出されない場合
- 複数の顔が検出された場合
- 画像品質が低い場合

#### `services/face_recognition.py`

**顔認識サービスの実装**

**機能:**
- `register_face(user_id, image)`: 顔を登録
- `authenticate_face(image)`: 顔認証を実行
- `compare_faces(known_encodings, face_encoding)`: 顔比較
- `get_user_encodings(user_id)`: ユーザーの顔データ取得

**設定可能なパラメータ:**
- 認証閾値 (デフォルト: 0.6)
- 最大登録可能顔数 (デフォルト: 5)

#### `routes/users.py`

**ユーザー管理API**

**エンドポイント:**
- `POST /api/users` - ユーザー作成
- `GET /api/users` - ユーザー一覧取得
- `GET /api/users/{id}` - ユーザー詳細取得
- `PUT /api/users/{id}` - ユーザー更新
- `DELETE /api/users/{id}` - ユーザー削除

**要件:**
- レスポンス形式: JSON
- HTTPステータスコードの適切な設定
- 入力値バリデーション

#### `routes/recognition.py`

**顔認識API**

**エンドポイント:**

1. **POST** `/api/recognition/register` - 顔登録
   - **リクエスト:** `{user_id: int, image: base64}`
   - **レスポンス:** `{success: bool, message: string}`

2. **POST** `/api/recognition/authenticate` - 顔認証
   - **リクエスト:** `{image: base64}`
   - **レスポンス:** `{success: bool, user_id: int, confidence: float}`

3. **GET** `/api/recognition/history` - 認証履歴
   - **レスポンス:** 認証ログの配列

### 2. フロントエンド実装

#### `App.js`

**メインアプリケーション**

**機能:**
- ルーティング設定 (React Router)
- 共通レイアウト
- ナビゲーション
- 状態管理 (Context API使用)

**ページ構成:**
- `/` : ダッシュボード
- `/register` : ユーザー登録
- `/authenticate` : 顔認証
- `/users` : ユーザー一覧

#### `components/Camera.js`

**カメラコンポーネント**

**機能:**
- WebRTCを使用したカメラアクセス
- 顔検出枠の表示
- 写真撮影機能
- プレビュー表示

**Props:**
- `onCapture`: 撮影時のコールバック
- `showFaceDetection`: 顔検出枠表示フラグ
- `autoCapture`: 自動撮影モード

**使用技術:** getUserMedia API, Canvas API

#### `components/UserRegistration.js`

**ユーザー登録コンポーネント**

**機能:**
- ユーザー情報入力フォーム
- 顔写真撮影
- 複数角度での顔登録
- 登録プロセスの進行状況表示

**フォーム項目:**
- 名前 (必須)
- メールアドレス (必須、一意)
- 顔写真 (3-5枚推奨)

**バリデーション:**
- 入力値チェック
- 顔検出確認
- 重複チェック

#### `components/FaceAuthentication.js`

**顔認証コンポーネント**

**機能:**
- リアルタイム顔検出
- 認証実行
- 結果表示
- 認証履歴表示

**状態管理:**
- カメラ状態
- 認証状態 (待機中/処理中/成功/失敗)
- エラーメッセージ

**UI要素:**
- カメラプレビュー
- 認証ボタン
- ステータス表示
- 結果カード

#### `components/Dashboard.js`

**ダッシュボードコンポーネント**

**機能:**
- システム概要表示
- 最近の認証履歴
- 登録ユーザー数統計
- クイックアクション

**表示項目:**
- 総ユーザー数
- 今日の認証回数
- 成功率
- 最新の認証結果5件

#### `services/api.js`

**API通信サービス**

**機能:**
- HTTP通信のラッパー
- エラーハンドリング
- レスポンス正規化
- 画像のBase64変換

**メソッド:**
- `createUser(userData)`
- `getUsers()`
- `registerFace(userId, imageData)`
- `authenticateFace(imageData)`
- `getAuthHistory()`

**エラーハンドリング:**
- ネットワークエラー
- HTTPエラー
- タイムアウト

### 3. Docker設定

#### `docker-compose.yml`

**サービス構成:**
- `backend`: Python Flask アプリケーション
- `frontend`: React アプリケーション

**ポート設定:**
- backend: 5000
- frontend: 3000

**ボリューム:**
- 顔画像データの永続化
- データベースファイルの永続化

**環境変数:**
- `FLASK_ENV=development`
- `REACT_APP_API_URL=http://localhost:5000`

### 4. 設定ファイル

#### `backend/requirements.txt`

```txt
Flask==2.3.3
Flask-CORS==4.0.0
opencv-python==4.8.1.78
face_recognition==1.3.0
numpy==1.24.3
Pillow==10.0.1
python-dotenv==1.0.0
```

#### `frontend/package.json`

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.15.0",
    "axios": "^1.5.0",
    "tailwindcss": "^3.3.3"
  }
}
```

## セキュリティ要件

### 1. 画像データ保護
- 顔画像の暗号化保存
- アクセス権限の制限
- 定期的なデータ削除

### 2. API セキュリティ
- レート制限の実装
- 入力値検証
- SQLインジェクション対策

### 3. プライバシー対応
- データ使用目的の明示
- ユーザー同意の取得
- データ削除機能

## パフォーマンス要件

### 1. 応答時間
- 顔検出: **2秒以内**
- 認証処理: **3秒以内**
- ユーザー登録: **5秒以内**

### 2. 精度目標
- 顔検出率: **95%以上**
- 認証精度: **90%以上**
- 誤認証率: **5%以下**

## テスト要件

### 1. 単体テスト
- 顔検出機能
- 認証ロジック
- API エンドポイント

### 2. 統合テスト
- フロントエンド・バックエンド連携
- カメラ機能
- データベース操作

### 3. ユーザビリティテスト
- 登録フローの確認
- 認証操作の確認
- エラーハンドリングの確認

## 開発優先順位

### フェーズ1: 基本機能 (Week 1-2)
1. データベース設計・構築
2. 顔検出・認識エンジン実装
3. 基本API実装
4. シンプルなフロントエンド

### フェーズ2: UI/UX向上 (Week 3)
1. カメラコンポーネント改善
2. ユーザーインターフェース洗練
3. エラーハンドリング強化
4. レスポンシブデザイン対応

### フェーズ3: 運用機能 (Week 4)
1. 管理機能実装
2. ログ・監視機能
3. セキュリティ強化
4. パフォーマンス最適化

## 注意事項

> **⚠️ 重要な考慮事項**

1. **カメラ権限**: ブラウザでのカメラアクセス許可が必要
2. **計算リソース**: 顔認識処理はCPU集約的
3. **データサイズ**: 顔画像データの容量管理
4. **ブラウザ互換性**: WebRTC対応ブラウザでの動作確認
5. **プライバシー**: 生体認証データの適切な取り扱い

---

**📝 開発ガイドライン**

この指示書に従って実装することで、実用的な顔認証システムを構築できます。開発中に技術的な課題が発生した場合は、段階的にアプローチし、最小限の機能から始めて徐々に拡張していくことをお勧めします。

**🔄 更新履歴**

- v1.0: 初回作成
- 最終更新: 2025年5月23日
