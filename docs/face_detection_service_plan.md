# 顔検出サービス実装計画

## 概要

顔検出サービスは、画像から顔を検出し、顔の特徴量を抽出するための機能を提供します。このサービスは、ユーザー登録時の顔画像の検証や、認証時の顔比較の基盤となる重要なコンポーネントです。

## ディレクトリ構造

```
app/
  services/
    __init__.py
    face_detection.py  # 顔検出サービスの実装
    face_recognition.py  # 顔認識サービスの実装（次のフェーズ）
  tests/
    test_face_detection.py  # 顔検出サービスのテスト
```

## タスク詳細

### 3.2. `detect_faces(image)` 関数の実装

この関数は、入力画像から顔を検出し、検出された顔の位置情報を返します。

```python
def detect_faces(image):
    """
    画像から顔を検出する
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        list: 検出された顔の位置情報のリスト [(top, right, bottom, left), ...]
        
    Raises:
        ValueError: 画像データが無効な場合
    """
    # OpenCVとface_recognitionを使用して顔を検出
    face_locations = face_recognition.face_locations(image)
    return face_locations
```

### 3.3. 顔が検出されない場合のエラーハンドリング

顔が検出されない場合は、適切なエラーメッセージを含む例外をスローします。

```python
def detect_faces(image):
    """
    画像から顔を検出する
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        list: 検出された顔の位置情報のリスト [(top, right, bottom, left), ...]
        
    Raises:
        ValueError: 画像データが無効な場合
        FaceDetectionError: 顔が検出されない場合
    """
    # OpenCVとface_recognitionを使用して顔を検出
    face_locations = face_recognition.face_locations(image)
    
    if not face_locations:
        raise FaceDetectionError("No faces detected in the image")
    
    return face_locations
```

### 3.4. 複数の顔が検出された場合のエラーハンドリング

複数の顔が検出された場合は、適切なエラーメッセージを含む例外をスローします。

```python
def detect_single_face(image):
    """
    画像から単一の顔を検出する
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        tuple: 検出された顔の位置情報 (top, right, bottom, left)
        
    Raises:
        ValueError: 画像データが無効な場合
        FaceDetectionError: 顔が検出されない場合
        MultipleFacesError: 複数の顔が検出された場合
    """
    face_locations = detect_faces(image)
    
    if len(face_locations) > 1:
        raise MultipleFacesError(f"Multiple faces detected in the image: {len(face_locations)}")
    
    return face_locations[0]
```

### 3.5. `validate_face_image(image)` 関数の実装

この関数は、顔画像が登録や認証に適しているかを検証します。

```python
def validate_face_image(image):
    """
    顔画像が登録や認証に適しているかを検証する
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        bool: 画像が有効な場合はTrue、そうでない場合はFalse
        
    Raises:
        ValueError: 画像データが無効な場合
    """
    # 画像サイズの検証
    if image.shape[0] < 100 or image.shape[1] < 100:
        return False, "Image is too small"
    
    # 画像の明るさの検証
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    if brightness < 50 or brightness > 200:
        return False, "Image is too dark or too bright"
    
    # 顔の検出と検証
    try:
        face_location = detect_single_face(image)
        
        # 顔のサイズの検証
        face_height = face_location[2] - face_location[0]
        face_width = face_location[1] - face_location[3]
        
        if face_height < 50 or face_width < 50:
            return False, "Detected face is too small"
        
        return True, "Image is valid"
    except FaceDetectionError:
        return False, "No face detected in the image"
    except MultipleFacesError:
        return False, "Multiple faces detected in the image"
```

### 3.6. 画像品質チェックロジックの実装

画像の品質をチェックするためのより詳細なロジックを実装します。

```python
def check_image_quality(image):
    """
    画像の品質をチェックする
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        dict: 品質チェック結果の辞書
            {
                'is_valid': bool,
                'brightness': float,
                'contrast': float,
                'blur': float,
                'message': str
            }
    """
    result = {
        'is_valid': True,
        'message': "Image quality is good"
    }
    
    # グレースケールに変換
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 明るさの計算
    brightness = np.mean(gray)
    result['brightness'] = brightness
    
    if brightness < 50:
        result['is_valid'] = False
        result['message'] = "Image is too dark"
    elif brightness > 200:
        result['is_valid'] = False
        result['message'] = "Image is too bright"
    
    # コントラストの計算
    contrast = np.std(gray)
    result['contrast'] = contrast
    
    if contrast < 20:
        result['is_valid'] = False
        result['message'] = "Image has low contrast"
    
    # ぼかしの検出
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    result['blur'] = laplacian_var
    
    if laplacian_var < 100:
        result['is_valid'] = False
        result['message'] = "Image is blurry"
    
    return result
```

### 3.7. `extract_face_encoding(image)` 関数の実装

この関数は、顔画像から特徴量を抽出します。

```python
def extract_face_encoding(image):
    """
    顔画像から特徴量を抽出する
    
    Args:
        image (numpy.ndarray): OpenCV形式の画像データ
        
    Returns:
        numpy.ndarray: 顔の特徴量ベクトル
        
    Raises:
        ValueError: 画像データが無効な場合
        FaceDetectionError: 顔が検出されない場合
        MultipleFacesError: 複数の顔が検出された場合
    """
    # 単一の顔を検出
    face_location = detect_single_face(image)
    
    # 顔の特徴量を抽出
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    
    return face_encoding
```

### 3.8. 顔検出サービスのユニットテスト作成

顔検出サービスの各機能をテストするためのユニットテストを作成します。

```python
# tests/test_face_detection.py

import unittest
import cv2
import numpy as np
from app.services.face_detection import (
    detect_faces,
    detect_single_face,
    validate_face_image,
    check_image_quality,
    extract_face_encoding,
    FaceDetectionError,
    MultipleFacesError
)

class TestFaceDetection(unittest.TestCase):
    def setUp(self):
        # テスト用の画像を読み込む
        self.valid_image = cv2.imread('tests/test_images/valid_face.jpg')
        self.no_face_image = cv2.imread('tests/test_images/no_face.jpg')
        self.multiple_faces_image = cv2.imread('tests/test_images/multiple_faces.jpg')
        self.low_quality_image = cv2.imread('tests/test_images/low_quality.jpg')
    
    def test_detect_faces(self):
        # 有効な画像で顔を検出できることを確認
        faces = detect_faces(self.valid_image)
        self.assertGreater(len(faces), 0)
        
        # 顔がない画像で例外がスローされることを確認
        with self.assertRaises(FaceDetectionError):
            detect_faces(self.no_face_image)
    
    def test_detect_single_face(self):
        # 有効な画像で単一の顔を検出できることを確認
        face = detect_single_face(self.valid_image)
        self.assertIsInstance(face, tuple)
        self.assertEqual(len(face), 4)
        
        # 複数の顔がある画像で例外がスローされることを確認
        with self.assertRaises(MultipleFacesError):
            detect_single_face(self.multiple_faces_image)
    
    def test_validate_face_image(self):
        # 有効な画像が検証をパスすることを確認
        is_valid, message = validate_face_image(self.valid_image)
        self.assertTrue(is_valid)
        
        # 低品質な画像が検証に失敗することを確認
        is_valid, message = validate_face_image(self.low_quality_image)
        self.assertFalse(is_valid)
    
    def test_check_image_quality(self):
        # 有効な画像の品質チェック結果を確認
        result = check_image_quality(self.valid_image)
        self.assertTrue(result['is_valid'])
        
        # 低品質な画像の品質チェック結果を確認
        result = check_image_quality(self.low_quality_image)
        self.assertFalse(result['is_valid'])
    
    def test_extract_face_encoding(self):
        # 顔の特徴量を抽出できることを確認
        encoding = extract_face_encoding(self.valid_image)
        self.assertIsInstance(encoding, np.ndarray)
        self.assertEqual(encoding.shape[0], 128)  # face_recognitionは128次元の特徴量を返す
```

## 例外クラスの定義

顔検出サービスで使用する例外クラスを定義します。

```python
class FaceDetectionError(Exception):
    """顔が検出されない場合のエラー"""
    pass

class MultipleFacesError(Exception):
    """複数の顔が検出された場合のエラー"""
    pass

class ImageQualityError(Exception):
    """画像品質が低い場合のエラー"""
    pass
```

## 実装手順

1. `app/services/face_detection.py`ファイルを作成し、上記の関数を実装します。
2. 例外クラスを定義します。
3. テスト用の画像を準備し、`tests/test_face_detection.py`ファイルを作成してテストを実装します。
4. テストを実行して、各機能が正しく動作することを確認します。

## 次のステップ

顔検出サービスの実装が完了したら、次のタスク「4.1. `get_user_encodings(user_id)` 関数の実装」に進みます。これは顔認識サービスの一部として実装されます。