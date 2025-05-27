# セキュリティ実装ガイド - Face Login System

## 実装済みのセキュリティ機能

### 1. JWT認証 ✅

#### 概要
- Flask-JWT-Extendedを使用したトークンベース認証
- アクセストークン（1時間）とリフレッシュトークン（30日）の2段階認証

#### エンドポイント
- `POST /api/auth/login` - 顔認証によるログイン
- `POST /api/auth/refresh` - トークンのリフレッシュ
- `GET /api/auth/me` - 現在のユーザー情報取得
- `POST /api/auth/logout` - ログアウト

#### 保護されたエンドポイント
すべてのAPIエンドポイントがJWT認証で保護されています：
- ユーザー管理API（CRUD操作）
- 顔登録API
- 認証履歴API

### 2. レート制限 ✅

#### 実装内容
- Flask-Limiterによるレート制限
- デフォルト制限: 200リクエスト/日、50リクエスト/時間
- 認証エンドポイント: 5リクエスト/分
- 登録エンドポイント: 10リクエスト/時間

### 3. アクセス制御 ✅

#### ユーザーレベルの制限
- ユーザーは自分のデータのみアクセス可能
- 顔登録は自分のアカウントのみ
- 認証履歴は自分の履歴のみ閲覧可能

### 4. 入力検証 ✅

#### 実装済みの検証
- Base64画像データの検証
- 必須フィールドのチェック
- メールアドレスの重複チェック
- 顔画像の品質チェック

## 使用方法

### 1. 認証フローの例

```python
import requests
import base64

# 1. ログイン
login_response = requests.post(
    "http://localhost:5001/api/auth/login",
    json={"image": base64_encoded_image}
)
tokens = login_response.json()['data']
access_token = tokens['access_token']

# 2. 認証が必要なAPIを呼び出す
headers = {"Authorization": f"Bearer {access_token}"}
users_response = requests.get(
    "http://localhost:5001/api/users",
    headers=headers
)

# 3. トークンをリフレッシュ
refresh_response = requests.post(
    "http://localhost:5001/api/auth/refresh",
    headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
)
new_access_token = refresh_response.json()['data']['access_token']
```

### 2. フロントエンドでの実装

```javascript
// APIサービスでトークンを管理
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// レスポンスインターセプター（401エラー処理）
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // トークンリフレッシュまたはログイン画面へ
      await refreshToken();
    }
    return Promise.reject(error);
  }
);
```

## セキュリティベストプラクティス

### 1. トークンの保存
- アクセストークン: メモリまたはsessionStorage
- リフレッシュトークン: httpOnly Cookie（推奨）またはlocalStorage

### 2. HTTPS必須
- 本番環境では必ずHTTPSを使用
- トークンの盗聴を防ぐ

### 3. CORS設定
- 許可するオリジンを明示的に指定
- ワイルドカード（*）は使用しない

### 4. 環境変数
```env
# .env ファイル
SECRET_KEY=your-very-secure-secret-key
JWT_SECRET_KEY=different-jwt-secret-key
FLASK_ENV=production
```

## 追加推奨セキュリティ対策

### 1. 画像暗号化
- 保存される顔画像をAES暗号化
- データベース内の顔エンコーディングも暗号化

### 2. 監査ログの強化
- すべてのAPIアクセスをログ記録
- 異常なアクセスパターンの検出

### 3. 2要素認証（2FA）
- 顔認証 + パスワード
- 顔認証 + OTP

### 4. セッション管理
- トークンのブラックリスト機能
- 同時ログインセッション数の制限

### 5. SQLインジェクション対策
- パラメータ化クエリの使用（実装済み）
- 入力のサニタイゼーション

## テスト済みのセキュリティ機能

### JWT認証テスト結果
```
✅ 顔認証によるログイン成功
✅ アクセストークンでの認証
✅ トークンなしでのアクセス拒否（401）
✅ トークンリフレッシュ
✅ ログアウト処理
```

### アクセス制御テスト
```
✅ 自分のデータのみアクセス可能
✅ 他人の顔登録は拒否（403）
✅ 他人の認証履歴閲覧は拒否（403）
```

## まとめ

Face Login Systemは、JWT認証、レート制限、アクセス制御など、基本的なセキュリティ機能を実装しています。本番環境では、HTTPS、環境変数の適切な管理、追加のセキュリティ対策を実施することを強く推奨します。