"""
異なる背景のテスト画像生成スクリプト

このスクリプトは、既存の顔画像を加工して異なる背景のテスト用画像を生成します。
以下の種類の画像を生成します：
1. 単色背景（白、黒、青、緑）
2. グラデーション背景
3. ノイズ背景
"""

import cv2
import numpy as np
import os
import argparse
import face_recognition

def extract_face_mask(image, face_location, padding=10):
    """顔の領域のマスクを作成する関数"""
    top, right, bottom, left = face_location
    
    # パディングを追加（顔の周囲も含める）
    top = max(0, top - padding)
    left = max(0, left - padding)
    bottom = min(image.shape[0], bottom + padding)
    right = min(image.shape[1], right + padding)
    
    # マスク画像を作成（黒背景に白い顔）
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (left, top), (right, bottom), 255, -1)
    
    # マスクをぼかして自然な境界にする
    mask = cv2.GaussianBlur(mask, (11, 11), 0)
    
    return mask

def change_background(image, face_location, background):
    """背景を変更する関数"""
    # 顔のマスクを作成
    mask = extract_face_mask(image, face_location)
    
    # マスクを3チャンネルに拡張
    mask_3channel = cv2.merge([mask, mask, mask])
    
    # 背景と元の画像を合成
    result = np.where(mask_3channel > 0, image, background).astype(np.uint8)
    
    return result

def create_solid_background(image, color):
    """単色背景を作成する関数"""
    return np.full_like(image, color)

def create_gradient_background(image):
    """グラデーション背景を作成する関数"""
    height, width = image.shape[:2]
    background = np.zeros_like(image)
    
    # 左上から右下へのグラデーション
    for y in range(height):
        for x in range(width):
            r = int(255 * y / height)
            g = int(255 * x / width)
            b = int(255 * (1 - y / height))
            background[y, x] = [b, g, r]
    
    return background

def create_noise_background(image):
    """ノイズ背景を作成する関数"""
    return np.random.randint(0, 255, image.shape, dtype=np.uint8)

def generate_background_images(input_image_path, output_dir):
    """異なる背景のテスト画像を生成する関数"""
    # 入力画像の読み込み
    image = cv2.imread(input_image_path)
    if image is None:
        print(f"エラー: 画像を読み込めませんでした: {input_image_path}")
        return False
    
    # 顔の検出
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_image)
    
    if len(face_locations) == 0:
        print(f"エラー: 画像から顔を検出できませんでした: {input_image_path}")
        return False
    
    # 元のファイル名（拡張子なし）を取得
    base_name = os.path.splitext(os.path.basename(input_image_path))[0]
    
    # 出力ディレクトリの作成
    backgrounds_dir = os.path.join(output_dir, "backgrounds")
    os.makedirs(backgrounds_dir, exist_ok=True)
    
    # 最初に検出された顔を使用
    face_location = face_locations[0]
    
    # 白背景の画像を生成
    white_bg = create_solid_background(image, [255, 255, 255])
    white_bg_image = change_background(image, face_location, white_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_white_bg.jpg"), white_bg_image)
    print(f"白背景の画像を生成しました: {base_name}_white_bg.jpg")
    
    # 黒背景の画像を生成
    black_bg = create_solid_background(image, [0, 0, 0])
    black_bg_image = change_background(image, face_location, black_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_black_bg.jpg"), black_bg_image)
    print(f"黒背景の画像を生成しました: {base_name}_black_bg.jpg")
    
    # 青背景の画像を生成
    blue_bg = create_solid_background(image, [255, 0, 0])  # BGR形式
    blue_bg_image = change_background(image, face_location, blue_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_blue_bg.jpg"), blue_bg_image)
    print(f"青背景の画像を生成しました: {base_name}_blue_bg.jpg")
    
    # 緑背景の画像を生成
    green_bg = create_solid_background(image, [0, 255, 0])  # BGR形式
    green_bg_image = change_background(image, face_location, green_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_green_bg.jpg"), green_bg_image)
    print(f"緑背景の画像を生成しました: {base_name}_green_bg.jpg")
    
    # グラデーション背景の画像を生成
    gradient_bg = create_gradient_background(image)
    gradient_bg_image = change_background(image, face_location, gradient_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_gradient_bg.jpg"), gradient_bg_image)
    print(f"グラデーション背景の画像を生成しました: {base_name}_gradient_bg.jpg")
    
    # ノイズ背景の画像を生成
    noise_bg = create_noise_background(image)
    noise_bg_image = change_background(image, face_location, noise_bg)
    cv2.imwrite(os.path.join(backgrounds_dir, f"{base_name}_noise_bg.jpg"), noise_bg_image)
    print(f"ノイズ背景の画像を生成しました: {base_name}_noise_bg.jpg")
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='異なる背景のテスト画像生成スクリプト')
    parser.add_argument('input_image', help='入力画像のパス')
    parser.add_argument('--output_dir', default='tests/test_images', help='出力ディレクトリのパス')
    
    args = parser.parse_args()
    
    # 入力画像のパスが存在するか確認
    if not os.path.exists(args.input_image):
        print(f"エラー: 入力画像が見つかりません: {args.input_image}")
        return
    
    # 出力ディレクトリが存在するか確認し、なければ作成
    os.makedirs(args.output_dir, exist_ok=True)
    
    # テスト用画像を生成
    if generate_background_images(args.input_image, args.output_dir):
        print(f"異なる背景のテスト画像の生成が完了しました。出力ディレクトリ: {args.output_dir}/backgrounds")
    else:
        print("テスト用画像の生成に失敗しました。")

if __name__ == "__main__":
    main()