import cv2
import pandas as pd
from ultralytics import YOLO
from tracker import *
import cvzone
import time
import os
import json
import glob
import Jetson.GPIO as GPIO
from fungsidrive import uploaddrive
from jaraklok import create_pdf
from fungsisheet import update_sheet
import shutil
import requests
from datetime import datetime

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Load model YOLO ke GPU jika tersedia
model = YOLO('1junbgt.pt').cuda()

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

cv2.namedWindow('Output', cv2.WINDOW_GUI_NORMAL)
cv2.setMouseCallback('Output', RGB)
cap = cv2.VideoCapture("real.mp4")

my_file = open("coco1.txt", "r")
data = my_file.read()
class_list = data.split("\n")

count = 0
cy1 = 300
font = cv2.FONT_HERSHEY_PLAIN

starting_time = None  # Waktu mulai deteksi
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

detecting = False

def check_internet_connection(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

while True:
    ret, frame = cap.read()
    frame_id += 1
    if not ret:
        break

    # Check GPIO status
    if GPIO.input(4) == GPIO.HIGH and GPIO.input(17) == GPIO.HIGH:
        if not detecting:
            detecting = True
            starting_time = time.time()  # Waktu mulai deteksi
            prev_log_time = starting_time  # Atur ulang prev_log_time
            
            # Hapus hasil deteksi sebelumnya
            counter1.clear()
            counter2.clear()
            counter3.clear()

            # Hapus file gambar sebelumnya
            file_list = glob.glob(os.path.join(output_folder, "*.png"))
            for f in file_list:
                os.remove(f)
    elif GPIO.input(4) == GPIO.LOW:
        if detecting:
            detecting = False
            ending_time = time.time()  # Waktu akhir deteksi

            # Hitung durasi deteksi
            time_diff_seconds = ending_time - starting_time
            hours = int(time_diff_seconds // 3600)
            minutes = int((time_diff_seconds % 3600) // 60)
            seconds = int(time_diff_seconds % 60)

            counts = {
                "bercak": len(counter1),
                "kuning": len(counter2),
                "berlubang": len(counter3),
                "start_time": time.strftime("%H:%M:%S", time.localtime(starting_time)),
                "end_time": time.strftime("%H:%M:%S", time.localtime(ending_time)),
                "duration": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
                "date": time.strftime("%d-%m-%Y")
            }

            with open("counts.json", "w") as json_file:
                json.dump(counts, json_file)

            if check_internet_connection():
                uploaddrive()
                create_pdf('counts.json')
#                 time.sleep(30)
                update_sheet()
            else:
                max_attempts = 1
                delay_between_attempts = 1  # dalam detik
                attempt_count = 0
                while not check_internet_connection() and attempt_count < max_attempts:
                    print("Tidak ada koneksi internet. Menunggu...")
                    time.sleep(delay_between_attempts)
                    attempt_count += 1
                
                if check_internet_connection():
                    uploaddrive()
                    create_pdf('counts.json')
#                     time.sleep(30)
                    update_sheet()
                else:
                    print("Gagal mengunggah data karena tidak ada koneksi internet.")
                    # Cek apakah folder backup sudah ada
                    backup_folder = "backup/" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    if not os.path.exists(backup_folder):
                        os.makedirs(backup_folder)
                        # Salin folder output_frames ke folder backup
                        shutil.copytree("output_frames", os.path.join(backup_folder, "output_frames"))
                        # Salin file counts.json ke folder backup
                        shutil.copy("counts.json", backup_folder)
                    else:
                        print("Folder backup sudah ada.")

    if detecting:
        count += 1
        if count % 3 != 0:
            continue

        frame = cv2.resize(frame, (640, 480))

        # Lakukan prediksi menggunakan GPU
        results = model.predict(frame, device='cuda', conf=0.5, imgsz=320)
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

#         cv2.putText(frame, "FPS: " + str(round(fps, 2)), (19, 200), font, 2, (0, 0, 255), 3)

        cv2.imshow("Output", frame)
    else:
        # Jika tidak mendeteksi, tetap tampilkan frame tanpa prediksi
        cv2.imshow("Output", frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Cleanup GPIO
GPIO.cleanup()

