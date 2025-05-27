# Face Login System 🔐

顔認証技術を使用したモダンなWebベース認証システム

## 🌟 主な機能

- **顔認証ログイン**: 高精度な顔認識による安全な認証
- **ユーザー管理**: 直感的なユーザー登録・管理機能
- **リアルタイム顔検出**: Webカメラを使用したリアルタイム顔キャプチャ
- **認証履歴**: 詳細な認証ログとCSVエクスポート機能
- **レスポンシブデザイン**: デスクトップ・モバイル対応

## 🚀 クイックスタート

### 必要な環境
- Python 3.9+
- Node.js 16+
- Webカメラ

### インストールと起動

```bash
# リポジトリをクローン
git clone https://github.com/morihik0/face-login.git
cd face-login

# バックエンドを起動
pip install -r requirements.txt
python run.py

# フロントエンドを起動（別ターミナル）
cd frontend
npm install
npm start
```

### アクセス
- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:5001
- **テストツール**: `test_tools/test_browser.html`

## 📊 システム性能

- **顔検出率**: 95%以上
- **認証精度**: 98%以上
- **処理時間**: 200-300ms
- **誤認証率**: 2%未満

## 🔧 技術スタック

### バックエンド
- **Python** + **Flask** - RESTful API
- **SQLite** - データベース
- **OpenCV** + **face_recognition** - 顔認識
- **JWT** - 認証トークン

### フロントエンド
- **React 18** + **TypeScript** - UI
- **Tailwind CSS** - スタイリング
- **React Router** - ルーティング

## 🛡️ セキュリティ

- JWT認証（アクセス・リフレッシュトークン）
- 入力値検証とサニタイゼーション
- CORS設定
- 認証ログ記録

## 📁 プロジェクト構造

```
face-login/
├── app/                    # バックエンドアプリケーション
│   ├── api/               # APIルート
│   ├── database/          # データベースモデル
│   └── services/          # ビジネスロジック
├── frontend/              # Reactフロントエンド
├── tests/                 # ユニットテスト
├── test_tools/           # テスト・分析ツール
├── docs/                 # ドキュメント
└── face_images/          # 顔画像ストレージ
```

## 🧪 テスト

```bash
# データベーステスト
python tests/test_database.py

# 顔検出テスト
python tests/test_face_detection.py

# 顔認識テスト
python tests/test_face_recognition.py

# APIテスト
python test_tools/test_api_simple.py
```

## 📖 ドキュメント

- [プロジェクト状況](./プロジェクト状況.md) - 詳細な実装状況
- [テスト結果サマリー](./テスト結果サマリー.md) - 包括的なテスト結果
- [セキュリティ実装ガイド](./SECURITY_IMPLEMENTATION.md) - セキュリティ機能詳細
- [Docker実行ガイド](./DOCKER_GUIDE.md) - Docker環境での実行方法

## 🎯 使用方法

### 1. ユーザー登録
1. 「ユーザー管理」→「新規ユーザー追加」
2. 名前とメールアドレスを入力
3. 顔写真を撮影して登録

### 2. 顔認証ログイン
1. 「ログイン」ページにアクセス
2. カメラに顔を向ける
3. 「認証」ボタンをクリック

### 3. 認証履歴確認
1. ダッシュボードで最近の認証を確認
2. 「履歴」ページで詳細な認証ログを表示
3. CSVエクスポートで分析用データを取得

## 🔄 開発状況

- ✅ **フェーズ1**: 顔認識エンジン（完了）
- ✅ **フェーズ2**: API・UI実装（完了）
- ✅ **フェーズ3**: テスト・最適化（完了）
- ✅ **フェーズ4**: ドキュメント整備（完了）

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesページでお知らせください。

---

**Face Login System** - 安全で使いやすい顔認証ソリューション