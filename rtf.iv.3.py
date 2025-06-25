import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
import mysql.connector
import time

# ---------- SETUP Wajah Dataset ----------
dataset_path = "dataset/"
known_encodings = []
known_names = []

for file in os.listdir(dataset_path):
    if file.endswith(".jpg") or file.endswith(".png"):
        path = os.path.join(dataset_path, file)
        img = face_recognition.load_image_file(path)
        encoding = face_recognition.face_encodings(img)
        if encoding:
            known_encodings.append(encoding[0])
            known_names.append(os.path.splitext(file)[0])

def get_jam():
    return datetime.now().strftime("%H:%M")

def get_tanggal():
    return datetime.now().strftime("%A, %d %B %Y")

def get_hari_indonesia():
    mapping = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jumat",
        "Saturday": "Sabtu",
        "Sunday": "Minggu"
    }
    return mapping[datetime.now().strftime("%A")]

def to_time(value):
    if isinstance(value, timedelta):
        return (datetime.min + value).time()
    return value

def ambil_jadwal_matkul_terurut():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gpuasamu",
        database="mylab"
    )
    cursor = conn.cursor()
    hari_ini = get_hari_indonesia()
    cursor.execute("""
        SELECT matkul, start_time, end_time, dosen
        FROM jadwal_matkul
        WHERE hari = %s AND kode_ruangan = %s
        ORDER BY start_time
    """, (hari_ini, "RTF.IV.4"))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [(d[0], "Perkuliahan", to_time(d[1]), to_time(d[2]), d[3]) for d in data]

def ambil_data_api_terurut():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gpuasamu",
        database="mylab"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nama_mahasiswa, jenis_kegiatan, start_time, end_time, nama_penanggungjawab
        FROM api
        WHERE tanggal_pinjam = CURDATE() AND kode_ruangan = %s
        ORDER BY start_time
    """, ("RTF.IV.4",))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return [(d[0], d[1], to_time(d[2]), to_time(d[3]), d[4]) for d in data]

def ambil_data_laboran():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gpuasamu",
        database="mylab"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nama_laboran, status, datetime
        FROM aktivitas_ruang_lab
        WHERE nama_laboran = 'saif'
        ORDER BY datetime DESC
        LIMIT 1
    """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result
    
def tambah_status_normal_ke_db(nama_laboran):
    if nama_laboran.lower() != "saif":
        return  # Abaikan jika bukan saif

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gpuasamu",
        database="mylab"
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aktivitas_ruang_lab (nama_laboran, status, datetime)
        VALUES (%s, %s, NOW())
    """, (nama_laboran, "normal"))
    conn.commit()
    cursor.close()
    conn.close()
    print("[✓] Status normal ditambahkan ke database.")

def tambah_status_ke_db(nama_laboran, status):
    if nama_laboran.lower() != "saif":
        return  # Abaikan jika bukan saif

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="gpuasamu",
        database="mylab"
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aktivitas_ruang_lab (nama_laboran, status, datetime)
        VALUES (%s, %s, NOW())
    """, (nama_laboran, status))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"[✓] Status '{status}' ditambahkan ke database.")


def tampilkan_panel():
    width, height = 1280, 720
    margin_top = -40
    img = np.zeros((height + margin_top, width, 3), dtype=np.uint8)

    img[:, :960] = (167, 101, 47)
    img[:, 960:] = (64, 35, 12)

    cv2.putText(img, get_tanggal(), (530, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, get_jam(), (730, 95), cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 2)
    cv2.putText(img, "Jadwal RTF.IV.4 Hari Ini", (200, 220), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
    cv2.line(img, (50, 270), (910, 270), (255, 255, 255), 2)

    aktivitas = ambil_data_laboran()
    if aktivitas:
        nama, status, waktu = aktivitas

        if status.lower() != "normal":
            cv2.putText(img, "Mohon Maaf, Ruangan Tidak Dapat Digunakan", (60, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(img, f"Alasan: '{status}'", (60, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            return img

    now = datetime.now().time()
    current = None
    next_up = None

    jadwal_utama = ambil_jadwal_matkul_terurut()
    jadwal_api = ambil_data_api_terurut()
    jadwal = jadwal_utama + jadwal_api

    def bertabrakan(j1, j2):
        return j1[2] < j2[3] and j2[2] < j1[3]

    jadwal_prioritas = []
    for j in jadwal:
        if any(bertabrakan(j, m) for m in jadwal_utama if j != m):
            if j in jadwal_utama:
                jadwal_prioritas.append(j)
        else:
            jadwal_prioritas.append(j)

    jadwal_prioritas.sort(key=lambda x: x[2])

    for entry in jadwal_prioritas:
        start = entry[2]
        end = entry[3]
        if start <= now <= end:
            current = entry
        elif start > now:
            if not next_up or start < next_up[2]:
                next_up = entry

    def tampilkan_ke_panel(panel_offset, label_lines, entry, font_scale=1.2, text_scale=0.9, thickness=2):
        y_start = 300
        line_spacing = 40
        for i, baris in enumerate(label_lines):
            cv2.putText(img, baris, (panel_offset + 40, y_start + i * line_spacing),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)

        info_y = y_start + len(label_lines) * line_spacing + 20
        if entry:
            nama, kegiatan, start, end, penanggung = entry
            cv2.putText(img, f"Nama      : {nama}", (panel_offset + 40, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), thickness)
            cv2.putText(img, f"Kegiatan  : {kegiatan}", (panel_offset + 40, info_y + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), thickness)
            cv2.putText(img, f"Waktu     : {start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
                        (panel_offset + 40, info_y + 80), cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), thickness)
            cv2.putText(img, f"Penanggung: {penanggung}", (panel_offset + 40, info_y + 120),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, (255, 255, 255), thickness)
        else:
            cv2.putText(img, "Tidak Ada Jadwal", (panel_offset + 40, info_y),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, (180, 180, 180), thickness)

    tampilkan_ke_panel(60, ["Sedang", "Berlangsung"], current)
    tampilkan_ke_panel(930, ["Jadwal", "Berikutnya"], next_up, font_scale=1.0, text_scale=0.5, thickness=2)

    return img

def tampilkan_wajah_dikenali(frame, nama):
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    img[:, :] = (0, 0, 0)
    wajah_kecil = cv2.resize(frame, (400, 400))
    x_offset, y_offset = 440, 100
    img[y_offset:y_offset+400, x_offset:x_offset+400] = wajah_kecil
    cv2.putText(img, f"Nama: {nama}", (440, 600), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    return img

if __name__ == "__main__":
    cap = cv2.VideoCapture(1)
    nama_dikenali = None
    waktu_terakhir_dikenali = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        detected_now = None
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            if True in matches:
                index = matches.index(True)
                detected_now = known_names[index]
                break

        if detected_now:
            nama_dikenali = detected_now
            waktu_terakhir_dikenali = datetime.now()
            panel = tampilkan_wajah_dikenali(frame, nama_dikenali)
        else:
            if nama_dikenali and waktu_terakhir_dikenali and (datetime.now() - waktu_terakhir_dikenali).seconds < 5:
                panel = tampilkan_wajah_dikenali(frame, nama_dikenali)
            else:
                nama_dikenali = None
                panel = tampilkan_panel()

        cv2.imshow("Panel RTF.IV.4", panel)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif nama_dikenali == "saif":
            if key == ord('k'):
                tambah_status_ke_db(nama_dikenali, "normal")
            elif key == ord('l'):
                tambah_status_ke_db(nama_dikenali, "Rapat Mendadak")
            elif key == ord('o'):
                tambah_status_ke_db(nama_dikenali, "Maintenance")



    cap.release()
    cv2.destroyAllWindows()
