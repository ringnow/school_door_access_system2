import cv2
import dlib
import numpy as np
import sqlite3
import threading
from tkinter import simpledialog
import tkinter as tk

# 初始化dlib的人脸检测器和特征提取器
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def register_face(table_name, name, password=None):
    print("开始人脸注册...")
    cap = cv2.VideoCapture(1)  # 使用外接摄像头
    registered = False  # 设置注册标志位
    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法接收图像流。退出...")
            break

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # 降低分辨率以提高处理速度
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 1)  # 使用upsample_num_times=1提高检测精度

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            shape = sp(gray, face)
            face_descriptor = facerec.compute_face_descriptor(frame, shape)
            face_data = np.array(face_descriptor)

            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE name=?", (name,))
            if cursor.fetchone():
                print("用户已注册！")
                registered = True
                break

            if table_name == "administrators":
                cursor.execute("INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)", (name, password, face_data.tobytes()))
            else:
                cursor.execute("INSERT INTO students (name, face_data) VALUES (?, ?)", (name, face_data.tobytes()))
            conn.commit()
            conn.close()
            print(f"用户 {name} 注册成功！")
            registered = True
            break

        if registered:
            break

        cv2.imshow('人脸注册', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


def recognize_face(table_name):
    print("开始人脸识别...")
    cap = cv2.VideoCapture(1)  # 使用外接摄像头
    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法接收图像流。退出...")
            break

        frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # 降低分辨率以提高处理速度
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 1)  # 使用upsample_num_times=1提高检测精度

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            shape = sp(gray, face)
            face_descriptor = facerec.compute_face_descriptor(frame, shape)
            face_data = np.array(face_descriptor)

            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT name, face_data FROM {table_name}")
            results = cursor.fetchall()
            conn.close()

            match = None
            for row in results:
                db_name, db_face_data = row[0], np.frombuffer(row[1], dtype=np.float64)
                dist = np.linalg.norm(face_data - db_face_data)
                if dist < 0.6:  # 设置一个阈值，通常0.6比较合适
                    match = db_name
                    break

            if match:
                cv2.putText(frame, f"ID: {match}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
                print(f"欢迎, {match}!")
            else:
                cv2.putText(frame, "未知", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                print("未知用户！")

        cv2.imshow('人脸识别', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# 示例：使用tkinter弹出窗口获取用户输入
def get_user_input():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    name = simpledialog.askstring("输入", "请输入用户姓名:", parent=root)
    return name

# 示例：调用注册和识别功能
if __name__ == "__main__":
    user_name = get_user_input()
    if user_name:
        register_face("students", user_name)
        recognize_face("students")