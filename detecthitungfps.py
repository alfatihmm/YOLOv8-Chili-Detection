import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import cvzone
import time
import os
import json
import random
import glob

# Load model YOLO ke GPU jika tersedia
model = YOLO('1junbgt.pt').cuda()

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

cv2.namedWindow('Output', cv2.WINDOW_GUI_NORMAL)
cv2.setMouseCallback('Output', RGB)
cap = cv2.VideoCapture('/home/jetson/TA/real.mp4')

my_file = open("coco1.txt", "r")
data = my_file.read()
class_list = data.split("\n")

count = 0
cy1 = 300
font = cv2.FONT_HERSHEY_PLAIN

starting_time = time.time() # Waktu mulai deteksi
frame_id = 0

tracker1 = Tracker()
tracker2 = Tracker()
tracker3 = Tracker()

counter1 = []
counter2 = []
counter3 = []
offset = 10

output_folder = "output_frames"
os.makedirs(output_folder, exist_ok=True)

# Hapus file dari eksekusi sebelumnya
file_list = glob.glob(os.path.join(output_folder, "*.png"))
for f in file_list:
    os.remove(f)

fps_time_list = []  # List untuk menyimpan pasangan (waktu, FPS)
prev_log_time = time.time()

while True:
    ret, frame = cap.read()
    frame_id += 1
    if not ret:
        break

    count += 1
    if count % 3 != 0:
        continue

    frame = cv2.resize(frame, (640, 480))

    # Lakukan prediksi menggunakan GPU
    results = model.predict(frame, device='cuda',conf=0.4,imgsz = 320)
    a = results[0].boxes.data.cpu().numpy()
    px = pd.DataFrame(a).astype("float")

    list1 = []
    bercak = []
    list2 = []
    kuning = []
    list3 = []
    berlubang = []

    for index, row in px.iterrows():
        x1 = int(row[0])
        y1 = int(row[1])
        x2 = int(row[2])
        y2 = int(row[3])
        d = int(row[5])
        c = class_list[d]

        if 'bercak' in c:
            list1.append([x1, y1, x2, y2])
            bercak.append(c)
        elif 'kuning' in c:
            list2.append([x1, y1, x2, y2])
            kuning.append(c)
        elif 'berlubang' in c:
            list3.append([x1, y1, x2, y2])
            berlubang.append(c)

    bbox1_idx = tracker1.update(list1)
    bbox2_idx = tracker2.update(list2)
    bbox3_idx = tracker3.update(list3)

    for bbox1 in bbox1_idx:
        for i in bercak:
            x3, y3, x4, y4, id1 = bbox1
            cxb = int(x3 + x4) // 2
            cyb = int(y3 + y4) // 2
            if cxb < (cy1 + offset) and cxb > (cy1 - offset):
                cv2.circle(frame, (cxb, cyb), 4, (0, 255, 0), -1)
                cv2.rectangle(frame, (x3, y3), (x4, y4), (0, 0, 255), 1)
                cvzone.putTextRect(frame, f'{id1}', (x3, y3), 1, 1)
                if id1 not in counter1:
                    counter1.append(id1)
                    # Save the frame when a bercak is detected
                    frame_filename = os.path.join(output_folder, f"bercak_{time.strftime('%H-%M-%S')}.png")
                    cv2.imwrite(frame_filename, frame)

    for bbox2 in bbox2_idx:
        for j in kuning:
            x5, y5, x6, y6, id2 = bbox2
            cxt = int(x5 + x6) // 2
            cyt = int(y5 + y6) // 2
            if cxt < (cy1 + offset) and cxt > (cy1 - offset):
                cv2.circle(frame, (cxt, cyt), 4, (0, 255, 0), -1)
                cv2.rectangle(frame, (x5, y5), (x6, y6), (0, 0, 255), 1)
                cvzone.putTextRect(frame, f'{id2}', (x5, y5), 1, 1)
                if id2 not in counter2:
                    counter2.append(id2)
                    # Save the frame when a kuning is detected
                    frame_filename = os.path.join(output_folder, f"kuning_{time.strftime('%H-%M-%S')}.png")
                    cv2.imwrite(frame_filename, frame)

    for bbox3 in bbox3_idx:
        for k in berlubang:
            x7, y7, x8, y8, id3 = bbox3
            cxk = int(x7 + x8) // 2
            cyk = int(y7 + y8) // 2
            if cxk < (cy1 + offset) and cxk > (cy1 - offset):
                cv2.circle(frame, (cxk, cyk), 4, (0, 255, 0), -1)
                cv2.rectangle(frame, (x7, y7), (x8, y8), (0, 0, 255), 1)
                cvzone.putTextRect(frame, f'{id3}', (x7, y7), 1, 1)
                if id3 not in counter3:
                    counter3.append(id3)
                    # Save the frame when a berlubang is detected
                    frame_filename = os.path.join(output_folder, f"berlubang_{time.strftime('%H-%M-%S')}.png")
                    cv2.imwrite(frame_filename, frame)

    cv2.line(frame, (cy1, 2), (cy1, 794), (0, 0, 255), 2)

    bercakc = len(counter1)
    kuningc = len(counter2)
    berlubangc = len(counter3)

    cvzone.putTextRect(frame, f'bercak: {bercakc}', (19, 30), 2, 1)
    cvzone.putTextRect(frame, f'kuning: {kuningc}', (19, 71), 2, 1)
    cvzone.putTextRect(frame, f'berlubang: {berlubangc}', (19, 112), 2, 1)

    # Hitung FPS
    current_time = time.time()
    elapsed_time = current_time - starting_time
    fps = 1 / (current_time - prev_log_time)
    
    # Simpan pasangan (waktu relatif, FPS) setiap 1/4 detik
    if elapsed_time - len(fps_time_list) * 0.25 >= 0.25:
        fps_time_list.append((round(elapsed_time, 2), fps))
        prev_log_time = current_time

#     cv2.putText(frame, "FPS: " + str(round(fps, 2)), (19, 200), font, 2, (0, 0, 255), 3)
    
    # Hitung selisih waktu antara waktu selesai dan waktu mulai deteksi
    time_diff_seconds = elapsed_time
    hours = int(time_diff_seconds // 3600)
    minutes = int((time_diff_seconds % 3600) // 60)
    seconds = int(time_diff_seconds % 60)

    counts = {
        "bercak": bercakc,
        "kuning": kuningc,
        "berlubang": berlubangc,
        "start_time": time.strftime("%H:%M:%S", time.localtime(starting_time)), # Catat waktu mulai deteksi
        "end_time": time.strftime("%H:%M:%S", time.localtime()), # Catat waktu selesai deteksi
        "duration": f"{hours:02d}:{minutes:02d}:{seconds:02d}", # Catat durasi deteksi
        "date" : time.strftime("%d-%m-%Y")
    }

    with open("counts.json", "w") as json_file:
        json.dump(counts, json_file)

    cv2.imshow("Output", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Tulis nilai FPS dan waktu ke file CSV
fps_time_df = pd.DataFrame(fps_time_list, columns=["Time (s)", "FPS"])
fps_time_df.to_csv("fps_log.csv", index=False)
