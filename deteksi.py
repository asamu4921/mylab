import face_recognition
import cv2
import mysql.connector
from datetime import datetime

# Konfigurasi database
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Ahmadsaif899.',
    'database': 'mylab'
}

# Load dataset wajah
dataset = {
    "obama": "dataset/obama.jpg",
    "jokowi": "dataset/jokowi.jpg",
    "prabowo": "dataset/prabowo.jpg",
    "xijinping": "dataset/xijinping.jpg",
    "ahok": "dataset/ahok.jpg",
    "saif": "dataset/saif.jpg"
}

known_face_encodings = []
known_face_names = []

for name, file in dataset.items():
    image = face_recognition.load_image_file(file)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        known_face_encodings.append(encodings[0])
        known_face_names.append(name)
    else:
        print(f"Wajah tidak terdeteksi di gambar {file}")

# Fungsi untuk simpan ke DB
def insert_aktivitas_dosen(nama_dosen, status):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        sql = "INSERT INTO aktivitas_ruang_dosen (nama_dosen, datetime, status) VALUES (%s, %s, %s)"
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(sql, (nama_dosen, now, status))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"{status.title()} dicatat untuk {nama_dosen}")
    except mysql.connector.Error as err:
        print(f"Error saat menyimpan ke database: {err}")

# Webcam capture
video_capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)

print("Tekan 's' untuk scan wajah (masuk), 'k' untuk keluar, 'q' untuk keluar program.")

while True:
    ret, frame = video_capture.read()
    if not ret:
        print("Gagal mengambil gambar dari kamera.")
        break

    # Resize + ubah ke RGB untuk deteksi
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_frame = small_frame[:, :, ::-1]

    # Deteksi wajah di frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Proses semua wajah yang terdeteksi
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = face_distances.argmin() if face_distances.size > 0 else None

        name = "Tidak dikenali"
        if best_match_index is not None and matches[best_match_index]:
            name = known_face_names[best_match_index]

        # Skala kembali ke ukuran asli
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Gambar kotak hijau
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        # Gambar label
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)

    # Tampilkan video
    cv2.imshow('Video', frame)

    # Deteksi tombol
    key = cv2.waitKey(1) & 0xFF

    if key in [ord('s'), ord('k')]:
        if face_encodings:
            face_encoding = face_encodings[0]
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = face_distances.argmin()

            if matches[best_match_index]:
                nama = known_face_names[best_match_index]
                status = "masuk" if key == ord('s') else "keluar"
                insert_aktivitas_dosen(nama, status)
            else:
                print("Wajah tidak dikenali.")
        else:
            print("Tidak ada wajah terdeteksi.")

    elif key == ord('q'):
        break


# Bersihkan
video_capture.release()
cv2.destroyAllWindows()
