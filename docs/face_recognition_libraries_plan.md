# 顔認識ライブラリ実装計画

## タスク3.1: 必要なライブラリ（OpenCV, face_recognition）のインストール

### 1. requirements.txtの更新

以下のライブラリをrequirements.txtに追加します：

```
# Face recognition dependencies
opencv-python==4.8.0
face-recognition==1.3.0
numpy==1.24.3
```

更新後のrequirements.txtの全内容：

```
# Core dependencies
Flask==2.3.3
Flask-Cors==4.0.0
Werkzeug==2.3.7
python-dotenv==1.0.0

# Face recognition dependencies
opencv-python==4.8.0
face-recognition==1.3.0
numpy==1.24.3

# Testing dependencies
pytest==7.4.0
```

### 2. ライブラリのインストール

以下のコマンドを実行して、必要なライブラリをインストールします：

```bash
pip install -r requirements.txt
```

### 3. インストール確認

インストールが正常に完了したことを確認するために、以下のPythonコードを実行します：

```python
import cv2
import face_recognition
import numpy as np

print(f"OpenCV version: {cv2.__version__}")
print(f"NumPy version: {np.__version__}")
print("face_recognition imported successfully")
```

### 4. 注意点

- face_recognitionライブラリはdlibに依存しています。dlibのインストールに問題がある場合は、システムに適したビルドツールが必要になる可能性があります。
- OpenCVは画像処理に使用され、face_recognitionは顔検出と特徴抽出に使用されます。
- NumPyは数値計算と配列操作に使用されます。

### 5. 次のステップ

ライブラリのインストールが完了したら、次のタスク「3.2. `detect_faces(image)` 関数の実装」に進みます。