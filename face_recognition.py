import cv2
import dlib
import numpy as np
import sqlite3
from tkinter import messagebox
from datetime import datetime
import tkinter as tk

# 初始化人脸检测和识别模型
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# 定义人脸匹配阈值（阈值越低要求匹配越严格）
FACE_MATCH_THRESHOLD = 0.5

def open_camera():
    """
    打开摄像头，尝试使用不同的后端API
    Returns:
        cap: 摄像头对象
    """
    cap = None
    # 尝试使用不同的摄像头后端
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_V4L2]:
        cap = cv2.VideoCapture(1, backend)  # 使用外接摄像头，编号为1
        if cap.isOpened():
            break
    if not cap or not cap.isOpened():
        raise Exception("无法打开摄像头")
    return cap

def close_camera(cap):
    """
    关闭摄像头
    Args:
        cap: 摄像头对象
    """
    cap.release()
    cv2.destroyAllWindows()

def process_frame(frame):
    """
    处理视频帧，进行灰度转换和人脸检测
    Args:
        frame: 视频帧
    Returns:
        frame: 原始视频帧
        gray: 灰度图像
        faces: 检测到的人脸列表
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    return frame, gray, faces

def recognize_face_from_frame(frame, table):
    """
    从视频帧中识别人脸，并在数据库中查找匹配的用户
    Args:
        frame: 视频帧
        table: 数据库表名
    Returns:
        username: 匹配的用户名，如果没有匹配则返回None
    """
    conn = sqlite3.connect('school_door_access_system.db', timeout=10)
    cursor = conn.cursor()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        conn.close()
        return None

    shape = predictor(gray, faces[0])
    face_descriptor = np.array(face_rec_model.compute_face_descriptor(frame, shape), dtype=np.float32)
    cursor.execute(f"SELECT username, face_data FROM {table}")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        db_face_data = np.frombuffer(row[1], dtype=np.float32)
        # 如果存储的人脸数据维度为256而当前描述为128，则只取前128维
        if db_face_data.shape[0] == 256 and face_descriptor.shape[0] == 128:
            db_face_data = db_face_data[:128]
        dist = np.linalg.norm(db_face_data - face_descriptor)
        if dist < FACE_MATCH_THRESHOLD:
            return row[0]
    return None

def is_face_registered(face_descriptor, table):
    """
    判断给定的人脸描述是否已在指定表中注册
    Args:
        face_descriptor: 人脸描述向量
        table: 数据库表名
    Returns:
        bool: 是否已注册
    """
    conn = sqlite3.connect('school_door_access_system.db', timeout=10)
    cursor = conn.cursor()
    cursor.execute(f"SELECT face_data FROM {table}")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        db_face_data = np.frombuffer(row[0], dtype=np.float32)
        if db_face_data.shape[0] == 256 and face_descriptor.shape[0] == 128:
            db_face_data = db_face_data[:128]
        dist = np.linalg.norm(db_face_data - face_descriptor)
        if dist < FACE_MATCH_THRESHOLD:
            return True
    return False

def capture_face_descriptor():
    """
    打开摄像头捕获访客人脸并返回人脸描述向量
    Returns:
        face_descriptor: 人脸描述向量，如果失败则返回 None
    """
    try:
        cap = open_camera()
    except Exception as e:
        messagebox.showerror("错误", str(e))
        return None

    window_name = "录入人脸"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    face_descriptor = None
    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("错误", "无法接收图像流")
            break

        frame, gray, faces = process_frame(frame)
        # 如果检测到人脸，捕获人脸描述
        if faces:
            shape = predictor(gray, faces[0])
            face_descriptor = np.array(face_rec_model.compute_face_descriptor(frame, shape), dtype=np.float32)
            cv2.putText(frame, "人脸捕获成功", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow(window_name, frame)
            # 等待1秒显示提示
            cv2.waitKey(1000)
            break

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close_camera(cap)
    return face_descriptor

def register_face(table, username, password="", id_number=None, phone=None, entry_time=None, exit_time=None):
    """
    注册人脸：
    - 对于管理员，调用时传入参数: register_face("administrators", username, password)
      插入数据时使用 (username, password, face_data)
    - 对于访客，调用时传入参数: register_face("visitors", username, id_number, phone, entry_time, exit_time)
      插入数据时使用:
          如果 visitors 表存在 visit_time 列，则插入 (username, face_data, id_number, phone, visit_time)
          否则插入 (username, face_data, id_number, phone, entry_time, exit_time)
    - 对于其他表，调用时传入: register_face(table, username)
      插入数据时使用 (username, face_data)
    Args:
        table: 数据库表名
        username: 用户名
        password: 密码（可选）
        id_number: 身份证号（可选）
        phone: 电话号码（可选）
        entry_time: 入校时间（可选）
        exit_time: 离校时间（可选）
    """
    root = tk._get_default_root()
    if root is None:
        root = tk.Tk()
        root.withdraw()

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
            face_descriptor = np.array(face_rec_model.compute_face_descriptor(frame, shape), dtype=np.float32)
            # 判断当前人脸是否已被注册
            if is_face_registered(face_descriptor, table):
                messagebox.showerror("错误", "该人脸已注册，请勿重复注册")
                break

            face_data = face_descriptor
            conn = sqlite3.connect('school_door_access_system.db', timeout=10)
            cursor = conn.cursor()

            if table == "administrators":
                cursor.execute(
                    "INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)",
                    (username, password, face_data.tobytes()))
            elif table == "visitors":
                cursor.execute("PRAGMA table_info(visitors)")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]
                if "visit_time" in columns:
                    if not entry_time or not str(entry_time).strip():
                        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "INSERT INTO visitors (username, face_data, id_number, phone, visit_time, approved) VALUES (?, ?, ?, ?, ?, 0)",
                        (username, face_data.tobytes(), id_number, phone, entry_time))
                else:
                    if not entry_time or not str(entry_time).strip():
                        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if not exit_time or not str(exit_time).strip():
                        exit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        "INSERT INTO visitors (username, face_data, id_number, phone, entry_time, exit_time, approved) VALUES (?, ?, ?, ?, ?, ?, 0)",
                        (username, face_data.tobytes(), id_number, phone, entry_time, exit_time))
            else:
                cursor.execute(f"INSERT INTO {table} (username, face_data) VALUES (?, ?)",
                               (username, face_data.tobytes()))
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