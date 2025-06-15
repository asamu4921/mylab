import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, timedelta
import mysql.connector

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


def ambil_data_terurut():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ahmadsaif899.",
        database="mylab"
    )
    cursor = conn.cursor()
    query = """
    SELECT nama_mahasiswa, jenis_kegiatan, start_time, end_time, nama_penanggungjawab
    FROM api
    WHERE tanggal_pinjam = CURDATE()
      AND kode_ruangan = 'RTF.IV.4'
    ORDER BY start_time
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data


def get_status_laboran_terakhir():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ahmadsaif899.",
        database="mylab"
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT status
        FROM aktivitas_ruang_lab
        WHERE nama_laboran = 'saif'
        ORDER BY datetime DESC
        LIMIT 1;
    """)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None


def ambil_data_laboran():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ahmadsaif899.",
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

def simpan_status_ke_db(nama, status):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ahmadsaif899.",
        database="mylab"
    )
    cursor = conn.cursor()
    query = """
        INSERT INTO aktivitas_ruang_lab (nama_laboran, datetime, status)
        VALUES (%s, NOW(), %s)
    """
    cursor.execute(query, (nama, status))
    conn.commit()
    cursor.close()
    conn.close()


def tampilkan_panel():
    width, height = 1280, 720
    margin_top = -40
    img = np.zeros((height + margin_top, width, 3), dtype=np.uint8)

    # Panel kiri & kanan
    img[:, :960] = (167, 101, 47)  # Biru kecoklatan
    img[:, 960:] = (64, 35, 12)    # Panel kanan gelap

    # Tanggal dan jam
    cv2.putText(img, get_tanggal(), (530, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(img, get_jam(), (730, 95),
                cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 2)

    # Judul
    cv2.putText(img, "Jadwal RTF.IV.4 Hari Ini", (200, 220),
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 3)
    cv2.line(img, (50, 270), (910, 270), (255, 255, 255), 2)

    current = None
    next_up = None

    # Cek status terakhir laboran
    status_terakhir = get_status_laboran_terakhir()

    if status_terakhir == 'Maintenance':
        # Tampilkan panel maintenance
        data_lab = ambil_data_laboran()
        if data_lab:
            nama, status, waktu = data_lab
            cv2.putText(img, "STATUS MAINTENANCE AKTIF!", (200, 320),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
            cv2.putText(img, f"Laboran   : {nama}", (200, 380),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(img, f"Waktu     : {waktu.strftime('%H:%M:%S %d-%m-%Y')}", (200, 420),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
            cv2.putText(img, f"Status    : {status}", (200, 460),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        else:
            cv2.putText(img, "Tidak Ada Data Maintenance", (200, 350),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (180, 180, 180), 2)
    else:
        # Ambil data dari API dan tampilkan ke panel
        data = ambil_data_terurut()
        now = datetime.now().time()

        for row in data:
            nama, kegiatan, start, end, penanggung = row
            if isinstance(start, timedelta):
                start = (datetime.min + start).time()
            if isinstance(end, timedelta):
                end = (datetime.min + end).time()

            if start <= now <= end:
                current = (nama, kegiatan, start, end, penanggung)
            elif start > now and next_up is None:
                next_up = (nama, kegiatan, start, end, penanggung)

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


        # Panel kiri: sedang berlangsung
        if current:
            tampilkan_ke_panel(60, ["Sedang", "Berlangsung"], current)
        else:
            cv2.putText(img, "Tidak Ada Peminjaman", (60, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (180, 180, 180), 2)
            cv2.putText(img, "Silahkan Melakukan Peminjaman Melalui PENRU", (60, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (180, 180, 180), 2)

        # Panel kanan: jadwal berikutnya
        tampilkan_ke_panel(930, ["Jadwal", "Berikutnya"], next_up, font_scale=1.0, text_scale=0.5, thickness=2)


    return img



# ---------- FUNGSI UTAMA ----------
def tampilkan_wajah_dikenali(frame, nama):
    img = np.zeros((720, 1280, 3), dtype=np.uint8)
    img[:, :] = (0, 0, 0)  # Hitam

    # Resize dan masukkan wajah ke tengah
    wajah_kecil = cv2.resize(frame, (400, 400))
    x_offset = 440
    y_offset = 100
    img[y_offset:y_offset+400, x_offset:x_offset+400] = wajah_kecil

    # Nama
    cv2.putText(img, f"Nama: {nama}", (440, 600),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
    return img


# ---------- MAIN LOOP ----------
cap = cv2.VideoCapture(0)
cv2.namedWindow("Panel RTF.IV.4", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Panel RTF.IV.4", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

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
    if key == 27:
        break
    elif key == ord('k') and nama_dikenali:
        simpan_status_ke_db(nama_dikenali, "Normal")
        print(f"[INFO] Status Normal disimpan untuk {nama_dikenali}")
        nama_dikenali = None
    elif key == ord('l') and nama_dikenali:
        simpan_status_ke_db(nama_dikenali, "Maintenance")
        print(f"[INFO] Status Maintenance disimpan untuk {nama_dikenali}")
        nama_dikenali = None

cap.release()
cv2.destroyAllWindows()
