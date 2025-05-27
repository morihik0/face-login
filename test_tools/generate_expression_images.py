"""
異なる表情のテスト画像生成スクリプト

このスクリプトは、既存の顔画像を加工して異なる表情のテスト用画像を生成します。
以下の種類の画像を生成します：
1. 笑顔効果（口元を変更）
2. 驚いた表情効果（目と口を変更）
3. 悲しい表情効果（口元を変更）
"""

import cv2
import numpy as np
import os
import argparse
import face_recognition

def add_smile(image, face_landmarks):
    """笑顔効果を追加する関数"""
    result = image.copy()
    
    # 口の位置を取得
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']
    
    # 口の中心点を計算
    mouth_center_x = int(np.mean([p[0] for p in top_lip + bottom_lip]))
    mouth_center_y = int(np.mean([p[1] for p in top_lip + bottom_lip]))
    
    # 口の幅を計算
    mouth_width = int(max([p[0] for p in top_lip + bottom_lip]) - min([p[0] for p in top_lip + bottom_lip]))
    
    # 笑顔の口を描画（半円）
    cv2.ellipse(result, 
                (mouth_center_x, mouth_center_y), 
                (mouth_width // 2, mouth_width // 4), 
                0, 0, 180, (0, 0, 255), 2)
    
    return result

def add_surprised(image, face_landmarks):
    """驚いた表情効果を追加する関数"""
    result = image.copy()
    
    # 目の位置を取得
    left_eye = face_landmarks['left_eye']
    right_eye = face_landmarks['right_eye']
    
    # 左目の中心点を計算
    left_eye_center_x = int(np.mean([p[0] for p in left_eye]))
    left_eye_center_y = int(np.mean([p[1] for p in left_eye]))
    
    # 右目の中心点を計算
    right_eye_center_x = int(np.mean([p[0] for p in right_eye]))
    right_eye_center_y = int(np.mean([p[1] for p in right_eye]))
    
    # 目の幅を計算
    left_eye_width = int(max([p[0] for p in left_eye]) - min([p[0] for p in left_eye]))
    right_eye_width = int(max([p[0] for p in right_eye]) - min([p[0] for p in right_eye]))
    
    # 驚いた目を描画（大きな円）
    cv2.circle(result, (left_eye_center_x, left_eye_center_y), left_eye_width, (255, 255, 255), -1)
    cv2.circle(result, (left_eye_center_x, left_eye_center_y), left_eye_width, (0, 0, 0), 2)
    cv2.circle(result, (right_eye_center_x, right_eye_center_y), right_eye_width, (255, 255, 255), -1)
    cv2.circle(result, (right_eye_center_x, right_eye_center_y), right_eye_width, (0, 0, 0), 2)
    
    # 口の位置を取得
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']
    
    # 口の中心点を計算
    mouth_center_x = int(np.mean([p[0] for p in top_lip + bottom_lip]))
    mouth_center_y = int(np.mean([p[1] for p in top_lip + bottom_lip]))
    
    # 口の幅を計算
    mouth_width = int(max([p[0] for p in top_lip + bottom_lip]) - min([p[0] for p in top_lip + bottom_lip]))
    
    # 驚いた口を描画（円）
    cv2.circle(result, (mouth_center_x, mouth_center_y), mouth_width // 2, (0, 0, 255), 2)
    
    return result

def add_sad(image, face_landmarks):
    """悲しい表情効果を追加する関数"""
    result = image.copy()
    
    # 口の位置を取得
    top_lip = face_landmarks['top_lip']
    bottom_lip = face_landmarks['bottom_lip']
    
    # 口の中心点を計算
    mouth_center_x = int(np.mean([p[0] for p in top_lip + bottom_lip]))
    mouth_center_y = int(np.mean([p[1] for p in top_lip + bottom_lip]))
    
    # 口の幅を計算
    mouth_width = int(max([p[0] for p in top_lip + bottom_lip]) - min([p[0] for p in top_lip + bottom_lip]))
    
    # 悲しい口を描画（逆向きの半円）
    cv2.ellipse(result, 
                (mouth_center_x, mouth_center_y + mouth_width // 4), 
                (mouth_width // 2, mouth_width // 4), 
                0, 180, 360, (0, 0, 255), 2)
    
    return result

def generate_expression_images(input_image_path, output_dir):
    """異なる表情のテスト画像を生成する関数"""
    # 入力画像の読み込み
    image = cv2.imread(input_image_path)
    if image is None:
        print(f"エラー: 画像を読み込めませんでした: {input_image_path}")
        return False
    
    # 顔のランドマークを検出
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    face_landmarks_list = face_recognition.face_landmarks(rgb_image)
    
    if len(face_landmarks_list) == 0:
        print(f"エラー: 画像から顔のランドマークを検出できませんでした: {input_image_path}")
        return False
    
    # 元のファイル名（拡張子なし）を取得
    base_name = os.path.splitext(os.path.basename(input_image_path))[0]
    
    # 出力ディレクトリの作成
    expressions_dir = os.path.join(output_dir, "expressions")
    os.makedirs(expressions_dir, exist_ok=True)
    
    # 最初に検出された顔のランドマークを使用
    face_landmarks = face_landmarks_list[0]
    
    # 笑顔効果の画像を生成
    smile_image = add_smile(image, face_landmarks)
    cv2.imwrite(os.path.join(expressions_dir, f"{base_name}_smile.jpg"), smile_image)
    print(f"笑顔効果の画像を生成しました: {base_name}_smile.jpg")
    
    # 驚いた表情効果の画像を生成
    surprised_image = add_surprised(image, face_landmarks)
    cv2.imwrite(os.path.join(expressions_dir, f"{base_name}_surprised.jpg"), surprised_image)
    print(f"驚いた表情効果の画像を生成しました: {base_name}_surprised.jpg")
    
    # 悲しい表情効果の画像を生成
    sad_image = add_sad(image, face_landmarks)
    cv2.imwrite(os.path.join(expressions_dir, f"{base_name}_sad.jpg"), sad_image)
    print(f"悲しい表情効果の画像を生成しました: {base_name}_sad.jpg")
    
    return True

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='異なる表情のテスト画像生成スクリプト')
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
    if generate_expression_images(args.input_image, args.output_dir):
        print(f"異なる表情のテスト画像の生成が完了しました。出力ディレクトリ: {args.output_dir}/expressions")
    else:
        print("テスト用画像の生成に失敗しました。")

if __name__ == "__main__":
    main()