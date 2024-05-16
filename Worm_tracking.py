import cv2
import pandas as pd
from pathlib import Path
import numpy as np
import tkinter.filedialog
import os

def calculate_distance(p1, p2):
    # 2点間の距離を計算する関数
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def track_and_save_worms_with_tracking(video_path,image_path):
    # 動画読み込み
    cap = cv2.VideoCapture(video_path)
    img = cv2.imread(image_path)
    img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if not cap.isOpened():
        print("動画を開けませんでした。")
        return


    # 見つかった線虫の中心座標とラベルを保存する辞書
    worm_data = {}
    next_label_id = 1
    previous_centers = []  # 直前フレームの線虫の中心座標を保存するリスト
    previous_labels = []  # 直前フレームの線虫のラベルを保存するリスト

    frame_number = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # グレースケールに変換
        gray_frame = 255 - cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 背景除去
        gray_frame = 255 - cv2.subtract(gray_frame, img)

        # 二値化して線虫の暗い領域を抽出
        _, binary_frame = cv2.threshold(gray_frame, 240, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow('Binary Frame', binary_frame)

        # 輪郭検出
        contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 各輪郭に対して処理
        current_centers = []  # 現在フレームの線虫の中心座標を保存するリスト
        current_box = [] #現在フレームのbounding boxの幅と高さを格納


        for idx, contour in enumerate(contours):
            # 輪郭の面積を計算
            area = cv2.contourArea(contour)

            if 50 <= area <= 200:
                # 輪郭を囲む最小の矩形を取得
                x, y, w, h = cv2.boundingRect(contour)


                # bounding boxの中心座標を計算
                center_x = x + w // 2
                center_y = y + h // 2





                # 現在フレームの線虫の中心座標とラベルを保存
                current_centers.append((center_x, center_y))
                current_box.append((w, h))

        # 直前フレームの線虫の中心座標がある場合、現在フレームのラベルを決定
        if previous_centers:
            current_labels = [None] * len(current_centers)  # 現在フレームの線虫のラベルを保存するリスト
            assigned_labels = set()  # 現在フレームに割り当て済みのラベルを保存するセット
            min_distance = [float('inf')]*len(current_centers) #直前フレームの線虫と現在フレームの線虫の距離

            for i, center in enumerate(current_centers):
                closest_label = None

                #仮のラベル(closest labelを割り当てる)
                for j, prev_center in enumerate(previous_centers):
                    distance = calculate_distance(center, prev_center)
                    if distance < min_distance[i]:
                        min_distance[i] = distance
                        closest_label = previous_labels[j]

                #もし、closest_labelが未割当だった場合、current_labelにする
                if closest_label not in assigned_labels:
                    current_labels[i] = closest_label
                    assigned_labels.add(closest_label)

                #もし割りあてられていた場合、距離を比較してより短い方にclosest labelを割り当て、遠い方に新しいラベルを与える
                else:
                    first_index = current_labels.index(closest_label)
                    if min_distance[i] >= min_distance[first_index]:
                        current_labels[i] = f"Worm_{next_label_id}"
                        next_label_id += 1

                    else:
                        current_labels[i] = closest_label
                        current_labels[first_index] = f"Worm_{next_label_id}"
                        next_label_id += 1

        # 初期フレームの場合は新しいラベルを作成
        else:
            current_labels = [f"Worm_{next_label_id + i}" for i in range(len(current_centers))]
            next_label_id += len(current_centers)

        # 現在フレームの線虫の中心座標とラベルを保存
        for center, box, label in zip(current_centers, current_box, current_labels):
            if label not in worm_data:
                worm_data[label] = []

            worm_data[label].append([frame_number, center[0], center[1], box[0], box[1]])

            # 直前フレームの線虫の中心座標とラベルを更新
        previous_centers = current_centers[:]
        previous_labels = current_labels[:]

        frame_number += 1


        # フレームに bounding box とラベルを描画して表示
        for (center_x, center_y), (w,h), label in zip(current_centers, current_box, current_labels):
            x = center_x - (w // 2)
            y = center_y - (h // 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        cv2.imshow('Tracking', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break



    # 個別のCSVファイルとして中心座標を保存
    video_folder = Path(video_path).parent
    for label, data in worm_data.items():
        # ラベルごとにフォルダを作成
        label_folder = video_folder / label
        os.makedirs(label_folder, exist_ok=True)

        # x 座標と y 座標を別々の CSV ファイルに保存
        x_csv_path = label_folder / f"{label}_x_coordinates.csv"
        y_csv_path = label_folder / f"{label}_y_coordinates.csv"
        box_csv_path = label_folder / f"{label}_box.csv"


        df = pd.DataFrame(data, columns=['Frame', 'Center_X', 'Center_Y', 'Width', 'Height'])
        df_x = df[['Frame', 'Center_X']]
        df_y = df[['Frame', 'Center_Y']]
        df_box = df[['Frame', 'Width', 'Height']]

        df_x.to_csv(x_csv_path, index=False)
        df_y.to_csv(y_csv_path, index=False)
        df_box.to_csv(box_csv_path, index=False)

    # 後処理
    cap.release()
    cv2.destroyAllWindows()

image_path = "C:\\Users\\yhlab\\Documents\\wormtrack\\background\\background.jpg"

def main():
    # select file
    root = tkinter.Tk()
    root.withdraw()
    video_path = tkinter.filedialog.askopenfilename()

    track_and_save_worms_with_tracking(video_path, image_path)

if __name__ == '__main__':
    main()


