import cv2
import pandas as pd
from pathlib import Path
import numpy as np
import tkinter.filedialog
import os

def calculate_distance(p1, p2):

    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def track_and_save_worms_with_tracking(video_path,image_path):

    cap = cv2.VideoCapture(video_path)
    img = cv2.imread(image_path)
    img = 255 - cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if not cap.isOpened():
        print("動画を開けませんでした。")
        return



    worm_data = {}
    next_label_id = 1
    previous_centers = []
    previous_labels = []

    frame_number = 0
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if out is None:
            frame_height, frame_width = frame.shape[:2]
            output_path = Path(video_path).with_name('labeled_output.avi')
            out = cv2.VideoWriter(str(output_path), fourcc, 20.0, (frame_width, frame_height))


        gray_frame = 255 - cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        gray_frame = 255 - cv2.subtract(gray_frame, img)


        _, binary_frame = cv2.threshold(gray_frame, 240, 255, cv2.THRESH_BINARY_INV)
        cv2.imshow('Binary Frame', binary_frame)


        contours, _ = cv2.findContours(binary_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        current_centers = []
        current_box = []


        for idx, contour in enumerate(contours):

            area = cv2.contourArea(contour)

            if 30 <= area <= 200:

                x, y, w, h = cv2.boundingRect(contour)



                center_x = x + w // 2
                center_y = y + h // 2






                current_centers.append((center_x, center_y))
                current_box.append((w, h))


        if previous_centers:
            current_labels = [None] * len(current_centers)
            assigned_labels = set()
            min_distance = [float('inf')]*len(current_centers)

            for i, center in enumerate(current_centers):
                closest_label = None


                for j, prev_center in enumerate(previous_centers):
                    distance = calculate_distance(center, prev_center)
                    if distance < min_distance[i]:
                        min_distance[i] = distance
                        closest_label = previous_labels[j]


                if closest_label not in assigned_labels:
                    current_labels[i] = closest_label
                    assigned_labels.add(closest_label)


                else:
                    first_index = current_labels.index(closest_label)
                    if min_distance[i] >= min_distance[first_index]:
                        current_labels[i] = f"Worm_{next_label_id}"
                        next_label_id += 1

                    else:
                        current_labels[i] = closest_label
                        current_labels[first_index] = f"Worm_{next_label_id}"
                        next_label_id += 1


        else:
            current_labels = [f"Worm_{next_label_id + i}" for i in range(len(current_centers))]
            next_label_id += len(current_centers)


        for center, box, label in zip(current_centers, current_box, current_labels):
            if label not in worm_data:
                worm_data[label] = []

            worm_data[label].append([frame_number, center[0], center[1], box[0], box[1]])


        previous_centers = current_centers[:]
        previous_labels = current_labels[:]

        frame_number += 1



        for (center_x, center_y), (w,h), label in zip(current_centers, current_box, current_labels):
            x = center_x - (w // 2)
            y = center_y - (h // 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


        rectangle_color = (128, 128, 128) if frame_number < 480 else (255, 0, 0)


        cv2.rectangle(frame, (frame_width - 110, 10), (frame_width - 10, 110), rectangle_color, -1)

        out.write(frame)
        cv2.imshow('Tracking', frame)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break




    video_folder = Path(video_path).parent
    for label, data in worm_data.items():

        label_folder = video_folder / label
        os.makedirs(label_folder, exist_ok=True)


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


    cap.release()
    out.release()
    cv2.destroyAllWindows()

image_path = ".\\background.jpg"

def main():
    # select file
    root = tkinter.Tk()
    root.withdraw()
    video_path = tkinter.filedialog.askopenfilename()

    track_and_save_worms_with_tracking(video_path, image_path)

if __name__ == '__main__':
    main()


