"""
テスト用顔画像データセット生成スクリプト

このスクリプトは、既存の顔画像を加工して様々な条件下でのテスト用画像を生成します。
以下の条件の画像を生成します：
1. 明るさの異なる画像（明るい、標準、暗い）
2. 異なるサイズの顔（大きい、小さい）
3. 異なる画質の画像（高解像度、低解像度）
4. 異なる角度の顔（回転）
"""

import cv2
import numpy as np
import os
import argparse
from pathlib import Path

def adjust_brightness(image, factor):
    """画像の明るさを調整する関数"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv = np.array(hsv, dtype=np.float64)
    hsv[:, :, 2] = hsv[:, :, 2] * factor
    hsv[:, :, 2][hsv[:, :, 2] > 255] = 255
    hsv = np.array(hsv, dtype=np.uint8)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def resize_image(image, scale_factor):
    """画像のサイズを変更する関数"""
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

def reduce_quality(image, quality):
    """画像の品質を下げる関数"""
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', image, encode_param)
    return cv2.imdecode(encimg, 1)

def rotate_image(image, angle):
    """画像を回転させる関数"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(image, rotation_matrix, (width, height), flags=cv2.INTER_LINEAR)

def generate_test_images(input_image_path, output_dir):
    """テスト用画像を生成する関数"""
    # 入力画像の読み込み
    image = cv2.imread(input_image_path)
    if image is None:
        print(f"エラー: 画像を読み込めませんでした: {input_image_path}")
        return False
    
    # 元のファイル名（拡張子なし）を取得
    base_name = os.path.splitext(os.path.basename(input_image_path))[0]
    
    # 明るさの異なる画像を生成
    brightness_dir = os.path.join(output_dir, "brightness")
    os.makedirs(brightness_dir, exist_ok=True)
    
    # 明るい画像（1.5倍）
    bright_image = adjust_brightness(image, 1.5)
    cv2.imwrite(os.path.join(brightness_dir, f"{base_name}_bright.jpg"), bright_image)
    print(f"明るい画像を生成しました: {base_name}_bright.jpg")
    
    # 標準画像（そのまま）
    cv2.imwrite(os.path.join(brightness_dir, f"{base_name}_normal.jpg"), image)
    print(f"標準画像を生成しました: {base_name}_normal.jpg")
    
    # 暗い画像（0.5倍）
    dark_image = adjust_brightness(image, 0.5)
    cv2.imwrite(os.path.join(brightness_dir, f"{base_name}_dark.jpg"), dark_image)
    print(f"暗い画像を生成しました: {base_name}_dark.jpg")
    
    # 異なるサイズの画像を生成
    sizes_dir = os.path.join(output_dir, "sizes")
    os.makedirs(sizes_dir, exist_ok=True)
    
    # 大きい画像（1.5倍）
    large_image = resize_image(image, 1.5)
    cv2.imwrite(os.path.join(sizes_dir, f"{base_name}_large.jpg"), large_image)
    print(f"大きい画像を生成しました: {base_name}_large.jpg")
    
    # 小さい画像（0.5倍）
    small_image = resize_image(image, 0.5)
    cv2.imwrite(os.path.join(sizes_dir, f"{base_name}_small.jpg"), small_image)
    print(f"小さい画像を生成しました: {base_name}_small.jpg")
    
    # 異なる画質の画像を生成
    quality_dir = os.path.join(output_dir, "quality")
    os.makedirs(quality_dir, exist_ok=True)
    
    # 高品質画像（品質90%）
    high_quality_image = reduce_quality(image, 90)
    cv2.imwrite(os.path.join(quality_dir, f"{base_name}_high_quality.jpg"), high_quality_image)
    print(f"高品質画像を生成しました: {base_name}_high_quality.jpg")
    
    # 低品質画像（品質30%）
    low_quality_image = reduce_quality(image, 30)
    cv2.imwrite(os.path.join(quality_dir, f"{base_name}_low_quality.jpg"), low_quality_image)
    print(f"低品質画像を生成しました: {base_name}_low_quality.jpg")
    
    # 異なる角度の画像を生成
    angles_dir = os.path.join(output_dir, "angles")
    os.makedirs(angles_dir, exist_ok=True)
    
    # 左に15度回転
    left_rotated_image = rotate_image(image, 15)
    cv2.imwrite(os.path.join(angles_dir, f"{base_name}_left15.jpg"), left_rotated_image)
    print(f"左に15度回転した画像を生成しました: {base_name}_left15.jpg")
    
    # 右に15度回転
    right_rotated_image = rotate_image(image, -15)
    cv2.imwrite(os.path.join(angles_dir, f"{base_name}_right15.jpg"), right_rotated_image)
    print(f"右に15度回転した画像を生成しました: {base_name}_right15.jpg")
    
    # 左に30度回転
    left_rotated_image_30 = rotate_image(image, 30)
    cv2.imwrite(os.path.join(angles_dir, f"{base_name}_left30.jpg"), left_rotated_image_30)
    print(f"左に30度回転した画像を生成しました: {base_name}_left30.jpg")
    
    # 右に30度回転
    right_rotated_image_30 = rotate_image(image, -30)
    cv2.imwrite(os.path.join(angles_dir, f"{base_name}_right30.jpg"), right_rotated_image_30)
    print(f"右に30度回転した画像を生成しました: {base_name}_right30.jpg")
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='テスト用顔画像データセット生成スクリプト')
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
    if generate_test_images(args.input_image, args.output_dir):
        print(f"テスト用画像の生成が完了しました。出力ディレクトリ: {args.output_dir}")
    else:
        print("テスト用画像の生成に失敗しました。")

if __name__ == "__main__":
    main()