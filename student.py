from face_recognition import register_face, recognize_face
import tkinter as tk
from tkinter import simpledialog

def student_register():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    name = simpledialog.askstring("输入", "请输入学生姓名:", parent=root)
    if name:
        register_face("students", name)

def student_login():
    print("学生登录...")
    recognize_face("students")

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