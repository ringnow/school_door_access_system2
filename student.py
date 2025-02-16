from face_recognition import register_face, recognize_face_from_frame
import tkinter as tk
from tkinter import simpledialog

def student_register():
    """
    学生注册功能，通过输入学生姓名并录入人脸数据。
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    name = simpledialog.askstring("输入", "请输入学生姓名:", parent=root)
    if name:
        register_face("students", name)

def student_login():
    """
    学生登录功能，通过摄像头捕捉人脸并识别。
    """
    print("学生登录...")
    global cap
    ret, frame = cap.read()
    if ret:
        user_id = recognize_face_from_frame(frame, "students")
        if user_id:
            print(f"学生 {user_id} 登录成功")
        else:
            print("未能识别学生")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    print("1. 学生注册")
    print("2. 学生登录")
    choice = simpledialog.askstring("输入", "请输入您的选择 (1 或 2):", parent=root)
    if choice == '1':
        student_register()
    elif choice == '2':
        student_login()
    else:
        print("无效的选择！")