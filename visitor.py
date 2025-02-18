import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
import datetime
import threading
import time
import cv2
import dlib
import numpy as np

# 人脸检测和识别模型初始化
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def open_camera():
    cap = None
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2]:
        cap = cv2.VideoCapture(1, backend)
        if cap.isOpened():
            break
    if not cap or not cap.isOpened():
        raise Exception("无法打开摄像头")
    return cap

def close_camera(cap):
    cap.release()
    cv2.destroyAllWindows()

def capture_face():
    cap = open_camera()
    window_name = "录入人脸"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    face_descriptor = None

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("错误", "无法接收图像流")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        if faces:
            shape = predictor(gray, faces[0])
            face_descriptor = np.array(face_rec_model.compute_face_descriptor(frame, shape), dtype=np.float32)
            cv2.rectangle(frame, (faces[0].left(), faces[0].top()), (faces[0].right(), faces[0].bottom()), (0, 255, 0), 2)

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close_camera(cap)
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow(window_name)
    return face_descriptor

def register_visitor(root):
    register_window = tk.Toplevel(root)
    register_window.title("访客注册")

    tk.Label(register_window, text="用户名:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(register_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(register_window, text="身份证号码:").grid(row=1, column=0, padx=10, pady=10)
    id_number_entry = tk.Entry(register_window)
    id_number_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(register_window, text="电话号码:").grid(row=2, column=0, padx=10, pady=10)
    phone_entry = tk.Entry(register_window)
    phone_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(register_window, text="入校日期:").grid(row=3, column=0, padx=10, pady=10)
    entry_date_entry = DateEntry(register_window, width=16, background='darkblue', foreground='white', borderwidth=2)
    entry_date_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(register_window, text="入校时间:").grid(row=4, column=0, padx=10, pady=10)
    entry_time_frame = tk.Frame(register_window)
    entry_time_frame.grid(row=4, column=1, padx=10, pady=10)

    entry_hour_spinbox = tk.Spinbox(entry_time_frame, from_=0, to=23, width=5, format="%02.0f")
    entry_hour_spinbox.grid(row=0, column=0)
    tk.Label(entry_time_frame, text=":").grid(row=0, column=1)
    entry_minute_spinbox = tk.Spinbox(entry_time_frame, from_=0, to=59, width=5, format="%02.0f")
    entry_minute_spinbox.grid(row=0, column=2)

    tk.Label(register_window, text="离校日期:").grid(row=5, column=0, padx=10, pady=10)
    exit_date_entry = DateEntry(register_window, width=16, background='darkblue', foreground='white', borderwidth=2)
    exit_date_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(register_window, text="离校时间:").grid(row=6, column=0, padx=10, pady=10)
    exit_time_frame = tk.Frame(register_window)
    exit_time_frame.grid(row=6, column=1, padx=10, pady=10)

    exit_hour_spinbox = tk.Spinbox(exit_time_frame, from_=0, to=23, width=5, format="%02.0f")
    exit_hour_spinbox.grid(row=0, column=0)
    tk.Label(exit_time_frame, text=":").grid(row=0, column=1)
    exit_minute_spinbox = tk.Spinbox(exit_time_frame, from_=0, to=59, width=5, format="%02.0f")
    exit_minute_spinbox.grid(row=0, column=2)

    def save_visitor():
        username = username_entry.get()
        id_number = id_number_entry.get()
        phone = phone_entry.get()
        entry_date = entry_date_entry.get_date().strftime("%Y-%m-%d")
        entry_time = f"{entry_hour_spinbox.get()}:{entry_minute_spinbox.get()}:00"
        exit_date = exit_date_entry.get_date().strftime("%Y-%m-%d")
        exit_time = f"{exit_hour_spinbox.get()}:{exit_minute_spinbox.get()}:00"
        entry_datetime = f"{entry_date} {entry_time}"
        exit_datetime = f"{exit_date} {exit_time}"
        visit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        face_descriptor = capture_face()
        if face_descriptor is None:
            messagebox.showerror("注册失败", "人脸录入失败")
            return

        if not username or not id_number or not phone:
            messagebox.showerror("注册失败", "所有字段都必须填写", parent=register_window)
            return

        try:
            datetime.datetime.strptime(entry_datetime, "%Y-%m-%d %H:%M:%S")
            datetime.datetime.strptime(exit_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("注册失败", "时间格式不正确", parent=register_window)
            return

        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO visitors (username, id_number, phone, entry_time, exit_time, visit_time, face_data, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (username, id_number, phone, entry_datetime, exit_datetime, visit_time, face_descriptor.tobytes()))
            conn.commit()
            conn.close()
            messagebox.showinfo("注册成功", "访客注册成功，等待管理员批准", parent=register_window)
            register_window.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("注册失败", f"数据库错误：{e}", parent=register_window)
        except sqlite3.OperationalError as e:
            messagebox.showerror("注册失败", f"数据库被锁定：{e}", parent=register_window)

    save_button = tk.Button(register_window, text="保存", command=save_visitor)
    save_button.grid(row=7, column=1, padx=10, pady=10)

def visitor_login(root):
    login_window = tk.Toplevel(root)
    login_window.title("访客登录")

    def check_login():
        cap = open_camera()
        ret, frame = cap.read()
        close_camera(cap)
        if not ret:
            messagebox.showerror("登录失败", "无法接收图像流")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        if not faces:
            messagebox.showerror("登录失败", "未检测到人脸")
            return

        shape = predictor(gray, faces[0])
        face_descriptor = np.array(face_rec_model.compute_face_descriptor(frame, shape), dtype=np.float32)

        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, entry_time, exit_time, face_data FROM visitors WHERE approved=1")
            visitors = cursor.fetchall()
            conn.close()

            for visitor in visitors:
                visitor_id, entry_time, exit_time, db_face_data = visitor
                db_face_data = np.frombuffer(db_face_data, dtype=np.float32)
                dist = np.linalg.norm(db_face_data - face_descriptor)
                if dist < 0.5:
                    if entry_time <= current_time <= exit_time:
                        messagebox.showinfo("登录成功", "访客登录成功!", parent=login_window)
                    else:
                        messagebox.showerror("登录失败", "当前时间不在允许的访问时间范围内", parent=login_window)
                    return

            messagebox.showerror("登录失败", "未匹配到访客信息", parent=login_window)
        except sqlite3.OperationalError as e:
            messagebox.showerror("登录失败", f"数据库被锁定：{e}", parent=login_window)

    login_button = tk.Button(login_window, text="登录", command=check_login)
    login_button.grid(row=1, column=1, padx=10, pady=10)

def auto_delete_expired_visitors():
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM visitors WHERE exit_time < ?", (current_time,))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"数据库被锁定：{e}")
        time.sleep(3600)

threading.Thread(target=auto_delete_expired_visitors, daemon=True).start()