import cv2
import dlib
import numpy as np
import sqlite3

# 初始化dlib的面部检测器和特征提取器
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
facerec = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

def open_camera(camera_index=1):
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise Exception(f"无法打开摄像头 (编号: {camera_index})")
    return cap

def close_camera(cap):
    cap.release()
    cv2.destroyAllWindows()

def process_frame(frame):
    frame = cv2.resize(frame, (640, 480))  # 调整分辨率
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 1)  # 使用upsample_num_times=1提高检测精度
    return frame, gray, faces

def recognize_face_from_frame(frame, table_name):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 1)

    if faces:
        for face in faces:
            shape = sp(gray, face)
            face_descriptor = facerec.compute_face_descriptor(frame, shape)
            face_data = np.array(face_descriptor)

            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT username, face_data FROM {table_name}")
            results = cursor.fetchall()
            conn.close()

            for row in results:
                db_name, db_face_data = row[0], np.frombuffer(row[1], dtype=np.float64)
                dist = np.linalg.norm(face_data - db_face_data)
                if dist < 0.6:  # 设置一个阈值，通常为0.6
                    return db_name
    return None

def register_face(table_name, name, password=None):
    print("开始人脸注册...")
    try:
        cap = open_camera()
    except Exception as e:
        print(e)
        return

    registered = False  # 设置注册标志位
    window_name = "人脸注册"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法接收图像流。退出...")
            break

        frame, gray, faces = process_frame(frame)

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            shape = sp(gray, face)
            face_descriptor = facerec.compute_face_descriptor(frame, shape)
            face_data = np.array(face_descriptor)

            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()

            # 检查面部数据是否已经存在于数据库中
            cursor.execute(f"SELECT face_data FROM {table_name}")
            existing_faces = cursor.fetchall()
            for existing_face in existing_faces:
                existing_face_data = np.frombuffer(existing_face[0], dtype=np.float64)
                dist = np.linalg.norm(face_data - existing_face_data)
                if dist < 0.6:  # 设置一个阈值，通常为0.6
                    print("用户已注册！")
                    registered = True
                    break

            if registered:
                break

            if table_name == "administrators":
                cursor.execute("INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)",
                               (name, password, face_data.tobytes()))
            else:
                cursor.execute("INSERT INTO students (username, face_data) VALUES (?, ?)", (name, face_data.tobytes()))
            conn.commit()
            conn.close()
            print(f"用户 {name} 注册成功！")
            registered = True
            break

        if registered:
            break

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close_camera(cap)
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow(window_name)
    print("摄像头已关闭，窗口已销毁。")