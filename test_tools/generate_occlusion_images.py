"""
顔の一部が隠れたテスト画像生成スクリプト

このスクリプトは、既存の顔画像を加工して顔の一部が隠れた状態のテスト用画像を生成します。
以下の種類の画像を生成します：
1. 目が隠れた画像（サングラス効果）
2. 口が隠れた画像（マスク効果）
3. 顔の上部が隠れた画像（帽子効果）
4. 顔の一部に影がある画像
"""

import cv2
import numpy as np
import os
import argparse
import face_recognition

def add_sunglasses(image, face_location):
    """サングラス効果を追加する関数"""
    top, right, bottom, left = face_location
    
    # 目の領域を計算（顔の上部1/3程度）
    eye_top = top + int((bottom - top) * 0.2)
    eye_bottom = top + int((bottom - top) * 0.45)
    
    # サングラス（黒い長方形）を描画
    result = image.copy()
    cv2.rectangle(result, (left, eye_top), (right, eye_bottom), (0, 0, 0), -1)
    
    return result

def add_mask(image, face_location):
    """マスク効果を追加する関数"""
    top, right, bottom, left = face_location
    
    # 口の領域を計算（顔の下部1/3程度）
    mouth_top = top + int((bottom - top) * 0.65)
    
    # マスク（白い長方形）を描画
    result = image.copy()
    cv2.rectangle(result, (left, mouth_top), (right, bottom), (255, 255, 255), -1)
    
    return result

def add_hat(image, face_location):
    """帽子効果を追加する関数"""
    top, right, bottom, left = face_location
    
    # 帽子の領域を計算（顔の上部1/4程度）
    hat_bottom = top + int((bottom - top) * 0.2)
    hat_top = max(0, top - int((bottom - top) * 0.3))  # 顔の上に少しはみ出す
    
    # 帽子（青い長方形）を描画
    result = image.copy()
    cv2.rectangle(result, (left - 20, hat_top), (right + 20, hat_bottom), (255, 0, 0), -1)
    
    return result

def add_shadow(image, face_location):
    """顔の一部に影を追加する関数"""
    top, right, bottom, left = face_location
    
    # 影の領域を計算（顔の右半分）
    shadow_left = left + int((right - left) * 0.5)
    
    # 影（暗い半透明の長方形）を描画
    result = image.copy()
    shadow = np.zeros_like(result)
    cv2.rectangle(shadow, (shadow_left, top), (right, bottom), (0, 0, 0), -1)
    
    # 影を半透明にするためにアルファブレンディング
    alpha = 0.5
    result = cv2.addWeighted(result, 1 - alpha, shadow, alpha, 0)
    
    return result

def generate_occlusion_images(input_image_path, output_dir):
    """顔の一部が隠れたテスト画像を生成する関数"""
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
    occlusions_dir = os.path.join(output_dir, "occlusions")
    os.makedirs(occlusions_dir, exist_ok=True)
    
    # 最初に検出された顔を使用
    face_location = face_locations[0]
    
    # サングラス効果の画像を生成
    sunglasses_image = add_sunglasses(image, face_location)
    cv2.imwrite(os.path.join(occlusions_dir, f"{base_name}_sunglasses.jpg"), sunglasses_image)
    print(f"サングラス効果の画像を生成しました: {base_name}_sunglasses.jpg")
    
    # マスク効果の画像を生成
    mask_image = add_mask(image, face_location)
    cv2.imwrite(os.path.join(occlusions_dir, f"{base_name}_mask.jpg"), mask_image)
    print(f"マスク効果の画像を生成しました: {base_name}_mask.jpg")
    
    # 帽子効果の画像を生成
    hat_image = add_hat(image, face_location)
    cv2.imwrite(os.path.join(occlusions_dir, f"{base_name}_hat.jpg"), hat_image)
    print(f"帽子効果の画像を生成しました: {base_name}_hat.jpg")
    
    # 影効果の画像を生成
    shadow_image = add_shadow(image, face_location)
    cv2.imwrite(os.path.join(occlusions_dir, f"{base_name}_shadow.jpg"), shadow_image)
    print(f"影効果の画像を生成しました: {base_name}_shadow.jpg")
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='顔の一部が隠れたテスト画像生成スクリプト')
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
    if generate_occlusion_images(args.input_image, args.output_dir):
        print(f"顔の一部が隠れたテスト画像の生成が完了しました。出力ディレクトリ: {args.output_dir}/occlusions")
    else:
        print("テスト用画像の生成に失敗しました。")

if __name__ == "__main__":
    main()