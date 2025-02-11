import cv2
import dlib
import numpy as np
import sqlite3
from tkinter import messagebox

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")


def open_camera():
    cap = cv2.VideoCapture(1)  # 使用外接摄像头，编号为1
    if not cap.isOpened():
        raise Exception("无法打开摄像头")
    return cap


def close_camera(cap):
    cap.release()
    cv2.destroyAllWindows()


def process_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return frame, gray, faces


def recognize_face_from_frame(frame, table):
    conn = sqlite3.connect('school_door_access_system.db')
    cursor = conn.cursor()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        return None

    shape = predictor(gray, faces[0])
    face_descriptor = face_rec_model.compute_face_descriptor(frame, shape)
    face_data = np.array(face_descriptor, dtype=np.float32).tobytes()

    cursor.execute(f"SELECT username, face_data FROM {table}")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        db_face_data = np.frombuffer(row[1], dtype=np.float32)
        dist = np.linalg.norm(db_face_data - face_descriptor)
        if dist < 0.6:
            return row[0]
    return None


def register_face(table, username, password, id_number=None, phone=None, visit_time=None):
    cap = open_camera()
    window_name = "录入人脸"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("错误", "无法接收图像流")
            break

        frame, gray, faces = process_frame(frame)

        if faces:
            shape = predictor(gray, faces[0])
            face_descriptor = face_rec_model.compute_face_descriptor(frame, shape)
            face_data = np.array(face_descriptor, dtype=np.float32)

            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()

            if table == "visitors":
                cursor.execute(
                    "INSERT INTO visitors (username, face_data, id_number, phone, visit_time) VALUES (?, ?, ?, ?, ?)",
                    (username, face_data.tobytes(), id_number, phone, visit_time))
            else:
                cursor.execute(f"INSERT INTO {table} (username, password, face_data) VALUES (?, ?, ?)",
                               (username, password, face_data.tobytes()))

            conn.commit()
            conn.close()
            messagebox.showinfo("成功", f"{username} 的人脸录入成功")
            break

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close_camera(cap)
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow(window_name)
    print("摄像头已关闭，窗口已销毁。")

