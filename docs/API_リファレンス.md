# Face Login System - API リファレンス

## 概要

Face Login SystemのRESTful APIの完全なリファレンスドキュメントです。全てのエンドポイント、リクエスト・レスポンス形式、認証方法について詳しく説明します。

## ベースURL

```
http://localhost:5001
```

## 認証

### JWT認証
ほとんどのAPIエンドポイントはJWT（JSON Web Token）認証が必要です。

#### 認証ヘッダー
```http
Authorization: Bearer <access_token>
```

#### トークンの種類
- **アクセストークン**: 1時間有効、API呼び出しに使用
- **リフレッシュトークン**: 30日有効、アクセストークンの更新に使用

## エラーレスポンス形式

全てのエラーレスポンスは以下の形式で返されます：

```json
{
  "status": "error",
  "message": "エラーメッセージ",
  "data": null,
  "error": "詳細なエラー情報（オプション）"
}
```

## 成功レスポンス形式

全ての成功レスポンスは以下の形式で返されます：

```json
{
  "status": "success",
  "message": "成功メッセージ",
  "data": {
    // レスポンスデータ
  }
}
```

---

## 📋 エンドポイント一覧

### 🌐 パブリックエンドポイント（認証不要）

#### 1. システム情報取得

```http
GET /
```

**説明**: システムの基本情報を取得

**レスポンス例**:
```json
{
  "message": "Face Login API is running",
  "status": "success",
  "version": "1.0.0"
}
```

#### 2. メールアドレス確認

```http
POST /api/public/check-email
```

**説明**: メールアドレスが既に登録されているかを確認

**リクエストボディ**:
```json
{
  "email": "user@example.com"
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Email check completed",
  "data": {
    "email": "user@example.com",
    "available": true
  }
}
```

#### 3. ユーザー登録（顔認証付き）

```http
POST /api/public/register-user-with-face
```

**説明**: 新規ユーザーを顔画像と共に登録し、即座にJWTトークンを発行

**リクエストボディ**:
```json
{
  "name": "山田太郎",
  "email": "yamada@example.com",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User registered successfully with face authentication",
  "data": {
    "user": {
      "id": 1,
      "name": "山田太郎",
      "email": "yamada@example.com",
      "created_at": "2025-05-27T09:00:00Z",
      "is_active": true
    },
    "face_registration": {
      "image_path": "face_images/user_1_20250527_090000_abc123.jpg",
      "face_count": 1
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

---

### 🔐 認証エンドポイント

#### 1. 顔認証ログイン

```http
POST /api/auth/login
```

**説明**: 顔画像を使用してログインし、JWTトークンを取得

**リクエストボディ**:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Authentication successful",
  "data": {
    "user": {
      "id": 1,
      "name": "山田太郎",
      "email": "yamada@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "confidence": 0.85
  }
}
```

#### 2. トークンリフレッシュ

```http
POST /api/auth/refresh
```

**説明**: リフレッシュトークンを使用して新しいアクセストークンを取得

**ヘッダー**:
```http
Authorization: Bearer <refresh_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

#### 3. 現在のユーザー情報取得

```http
GET /api/auth/me
```

**説明**: 現在ログインしているユーザーの情報を取得

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User information retrieved",
  "data": {
    "user": {
      "id": 1,
      "name": "山田太郎",
      "email": "yamada@example.com",
      "created_at": "2025-05-27T09:00:00Z",
      "is_active": true
    }
  }
}
```

#### 4. ログアウト

```http
POST /api/auth/logout
```

**説明**: 現在のトークンを無効化してログアウト

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Logged out successfully",
  "data": null
}
```

---

### 👥 ユーザー管理エンドポイント（認証必要）

#### 1. ユーザー一覧取得

```http
GET /api/users
```

**説明**: 全ユーザーの一覧を取得

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Users retrieved successfully",
  "data": {
    "users": [
      {
        "id": 1,
        "name": "山田太郎",
        "email": "yamada@example.com",
        "created_at": "2025-05-27T09:00:00Z",
        "is_active": true
      }
    ],
    "total": 1
  }
}
```

#### 2. 特定ユーザー取得

```http
GET /api/users/{user_id}
```

**説明**: 指定されたIDのユーザー情報を取得

**パラメータ**:
- `user_id` (integer): ユーザーID

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User retrieved successfully",
  "data": {
    "user": {
      "id": 1,
      "name": "山田太郎",
      "email": "yamada@example.com",
      "created_at": "2025-05-27T09:00:00Z",
      "is_active": true
    }
  }
}
```

#### 3. ユーザー作成

```http
POST /api/users
```

**説明**: 新しいユーザーを作成（顔画像なし）

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**リクエストボディ**:
```json
{
  "name": "佐藤花子",
  "email": "sato@example.com"
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User created successfully",
  "data": {
    "user": {
      "id": 2,
      "name": "佐藤花子",
      "email": "sato@example.com",
      "created_at": "2025-05-27T10:00:00Z",
      "is_active": true
    }
  }
}
```

#### 4. ユーザー更新

```http
PUT /api/users/{user_id}
```

**説明**: 既存ユーザーの情報を更新

**パラメータ**:
- `user_id` (integer): ユーザーID

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**リクエストボディ**:
```json
{
  "name": "佐藤花子（更新）",
  "email": "sato.updated@example.com"
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User updated successfully",
  "data": {
    "user": {
      "id": 2,
      "name": "佐藤花子（更新）",
      "email": "sato.updated@example.com",
      "created_at": "2025-05-27T10:00:00Z",
      "is_active": true
    }
  }
}
```

#### 5. ユーザー削除

```http
DELETE /api/users/{user_id}
```

**説明**: 指定されたユーザーを削除

**パラメータ**:
- `user_id` (integer): ユーザーID

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "User deleted successfully",
  "data": null
}
```

---

### 🎭 顔認識エンドポイント（認証必要）

#### 1. 顔登録

```http
POST /api/recognition/register
```

**説明**: 既存ユーザーに顔画像を登録（最大5枚まで）

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**リクエストボディ**:
```json
{
  "user_id": 2,
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Face registered successfully",
  "data": {
    "user_id": 2,
    "image_path": "face_images/user_2_20250527_100000_def456.jpg",
    "face_count": 1,
    "encoding_id": 5
  }
}
```

#### 2. 顔認証

```http
POST /api/recognition/authenticate
```

**説明**: 顔画像を使用してユーザーを認証

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**リクエストボディ**:
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
}
```

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Face authentication successful",
  "data": {
    "user_id": 2,
    "user_name": "佐藤花子",
    "confidence": 0.92,
    "authenticated": true,
    "timestamp": "2025-05-27T11:00:00Z"
  }
}
```

#### 3. 認証履歴取得

```http
GET /api/recognition/history
```

**説明**: 認証履歴を取得

**ヘッダー**:
```http
Authorization: Bearer <access_token>
```

**クエリパラメータ**:
- `limit` (integer, optional): 取得件数（デフォルト: 10）
- `user_id` (integer, optional): 特定ユーザーの履歴のみ取得

**レスポンス例**:
```json
{
  "status": "success",
  "message": "Authentication history retrieved",
  "data": {
    "history": [
      {
        "id": 1,
        "user_id": 2,
        "user_name": "佐藤花子",
        "success": true,
        "confidence": 0.92,
        "timestamp": "2025-05-27T11:00:00Z"
      }
    ],
    "total": 1
  }
}
```

---

## 📊 HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | 成功 |
| 201 | 作成成功 |
| 400 | 不正なリクエスト |
| 401 | 認証が必要 |
| 403 | アクセス拒否 |
| 404 | リソースが見つからない |
| 409 | 競合（重複データなど） |
| 422 | 処理できないエンティティ |
| 500 | サーバー内部エラー |

## 🔧 画像形式

### サポートされる形式
- JPEG
- PNG
- WebP

### 画像要件
- **最小サイズ**: 100x100ピクセル
- **最大サイズ**: 2048x2048ピクセル
- **ファイルサイズ**: 最大5MB
- **顔の数**: 1つの顔のみ
- **画質**: 明るく、鮮明な画像

### Base64エンコーディング
画像はBase64形式でエンコードして送信してください：

```javascript
// JavaScript例
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
// ... 画像をcanvasに描画
const base64Image = canvas.toDataURL('image/jpeg', 0.8);
```

## 🚨 エラーコード

### 認証エラー
- `INVALID_TOKEN`: 無効なトークン
- `EXPIRED_TOKEN`: 期限切れトークン
- `MISSING_TOKEN`: トークンが未提供

### 顔認識エラー
- `NO_FACE_DETECTED`: 顔が検出されない
- `MULTIPLE_FACES_DETECTED`: 複数の顔が検出された
- `POOR_IMAGE_QUALITY`: 画像品質が低い
- `FACE_TOO_SMALL`: 顔が小さすぎる
- `FACE_TOO_DARK`: 画像が暗すぎる
- `FACE_TOO_BRIGHT`: 画像が明るすぎる

### データエラー
- `USER_NOT_FOUND`: ユーザーが見つからない
- `EMAIL_ALREADY_EXISTS`: メールアドレスが既に存在
- `MAX_FACES_REACHED`: 最大顔登録数に達している

## 📝 使用例

### JavaScript (Fetch API)

```javascript
// 顔認証ログイン
async function faceLogin(imageBase64) {
  try {
    const response = await fetch('http://localhost:5001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageBase64
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      // トークンを保存
      localStorage.setItem('access_token', result.data.access_token);
      localStorage.setItem('refresh_token', result.data.refresh_token);
      console.log('ログイン成功:', result.data.user);
    } else {
      console.error('ログイン失敗:', result.message);
    }
  } catch (error) {
    console.error('エラー:', error);
  }
}

// 認証が必要なAPIの呼び出し
async function getUsers() {
  const token = localStorage.getItem('access_token');
  
  try {
    const response = await fetch('http://localhost:5001/api/users', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      }
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('ユーザー一覧:', result.data.users);
    } else {
      console.error('取得失敗:', result.message);
    }
  } catch (error) {
    console.error('エラー:', error);
  }
}
```

### Python (requests)

```python
import requests
import base64

# 顔認証ログイン
def face_login(image_path):
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    response = requests.post(
        'http://localhost:5001/api/auth/login',
        json={
            'image': f'data:image/jpeg;base64,{image_data}'
        }
    )
    
    result = response.json()
    
    if result['status'] == 'success':
        access_token = result['data']['access_token']
        print(f"ログイン成功: {result['data']['user']['name']}")
        return access_token
    else:
        print(f"ログイン失敗: {result['message']}")
        return None

# 認証が必要なAPIの呼び出し
def get_users(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(
        'http://localhost:5001/api/users',
        headers=headers
    )
    
    result = response.json()
    
    if result['status'] == 'success':
        print("ユーザー一覧:", result['data']['users'])
    else:
        print("取得失敗:", result['message'])
```

## 🔄 レート制限

現在のレート制限設定：

- **デフォルト**: 100リクエスト/分
- **認証エンドポイント**: 5リクエスト/分
- **登録エンドポイント**: 10リクエスト/時間

レート制限に達した場合、HTTP 429ステータスコードが返されます。

## 📞 サポート

APIに関する質問や問題がある場合は、GitHubのIssuesページでお知らせください。

---

**Face Login System API** - 安全で使いやすい顔認証API