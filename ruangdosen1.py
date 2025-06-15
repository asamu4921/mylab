import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from playsound import playsound
import locale
import mysql.connector

# Locale biar tanggal bisa lokal
locale.setlocale(locale.LC_TIME, '')

# Load wajah dari dataset
dataset_path = "dataset/"
known_encodings = []
known_names = []

for file in os.listdir(dataset_path):
    if file.endswith(".jpg") or file.endswith(".png"):
        path = os.path.join(dataset_path, file)
        img = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(img)
        if encodings:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(file)[0])

def get_jam():
    return datetime.now().strftime("%H:%M")

def get_tanggal():
    return datetime.now().strftime("%A, %d %B %Y")

def get_data_log():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ahmadsaif899.",
            database="mylab"
        )
        cursor = db.cursor()
        query = """
        SELECT a.nama_dosen, a.datetime, a.status
        FROM aktivitas_ruang_dosen a
        INNER JOIN (
            SELECT nama_dosen, MAX(datetime) AS latest_time
            FROM aktivitas_ruang_dosen
            WHERE nama_dosen IN ('saif', 'jokowi')
            GROUP BY nama_dosen
        ) b ON a.nama_dosen = b.nama_dosen AND a.datetime = b.latest_time;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print("Gagal ambil data:", e)
        return []

def simpan_log(nama_dosen, status):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Ahmadsaif899.",
            database="mylab"
        )
        cursor = db.cursor()
        query = "INSERT INTO aktivitas_ruang_dosen (nama_dosen, datetime, status) VALUES (%s, %s, %s)"
        data = (nama_dosen, datetime.now(), status)
        cursor.execute(query, data)
        db.commit()
        print(f"[✓] Log disimpan: {nama_dosen} - {status}")
    except Exception as e:
        print("[X] Gagal simpan log:", e)

def tampilkan_panel():
    width, height = 1280, 720
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # LEFT PANEL
    img[:, :960] = (167, 101, 47)
    # RIGHT PANEL
    img[:, 960:] = (64, 35, 12)

    # TANGGAL & JAM
    cv2.putText(img, get_tanggal(), (530, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, get_jam(), (730, 95), cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 2)

    # JUDUL
    cv2.putText(img, "Ruang Dosen 1", (250, 220), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (255, 255, 255), 3)
    # GARIS
    cv2.line(img, (50, 270), (910, 270), (255, 255, 255), 2)

    # HEADER TABEL
    cv2.putText(img, "Nama Dosen", (60, 320), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    cv2.putText(img, "Waktu Terakhir", (330, 320), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    cv2.putText(img, "Status", (700, 320), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

    # ISI TABEL
    logs = get_data_log()
    y = 360
    for nama, waktu, status in logs:
        waktu_str = waktu.strftime('%H:%M:%S')
        cv2.putText(img, nama, (60, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(img, waktu_str, (340, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        cv2.putText(img, status, (700, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        y += 50

    return img

# ==============================
# START PROGRAM
# ==============================

cap = cv2.VideoCapture(0)
cv2.namedWindow("Checklog Panel", cv2.WINDOW_NORMAL)
is_fullscreen = False
wajah_terdeteksi = False
last_detect_time = None
nama_terdeteksi = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("Gagal ambil kamera")
        break

    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame)

    if len(face_locations) > 0:
        last_detect_time = datetime.now()
        wajah_terdeteksi = True

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                matched_idx = matches.index(True)
                name = known_names[matched_idx]
                nama_terdeteksi = name
            else:
                nama_terdeteksi = None

            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow("Checklog Panel", frame)
    else:
        if wajah_terdeteksi and last_detect_time:
            selisih = (datetime.now() - last_detect_time).total_seconds()
            if selisih > 5:
                wajah_terdeteksi = False
                nama_terdeteksi = None

        if not wajah_terdeteksi:
            panel = tampilkan_panel()
            cv2.imshow("Checklog Panel", panel)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('f'):
        is_fullscreen = True
        cv2.setWindowProperty("Checklog Panel", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    elif key == ord('n'):
        is_fullscreen = False
        cv2.setWindowProperty("Checklog Panel", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    elif key == ord('k') and nama_terdeteksi:
        simpan_log(nama_terdeteksi, "Diluar")
        playsound("sukses_diluar.mp3")
    elif key == ord('l') and nama_terdeteksi:
        simpan_log(nama_terdeteksi, "Didalam")
        playsound("sukses_didalam.mp3")

cap.release()
cv2.destroyAllWindows()
