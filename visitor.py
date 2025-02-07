import sqlite3
from face_recognition import register_face
import tkinter as tk
from tkinter import simpledialog, messagebox

def register_visitor():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    name = simpledialog.askstring("输入", "请输入访客姓名:", parent=root)
    id_number = simpledialog.askstring("输入", "请输入访客身份证号:", parent=root)
    phone = simpledialog.askstring("输入", "请输入访客电话:", parent=root)
    visit_time = simpledialog.askstring("输入", "请输入访问时间 (YYYY-MM-DD HH:MM):", parent=root)

    if name and id_number and phone and visit_time:
        # 进行人脸识别注册
        print("请面对摄像头进行注册...")
        register_face("visitors", name)

        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO visitors (name, id_number, phone, visit_time) VALUES (?, ?, ?, ?)", (name, id_number, phone, visit_time))
        conn.commit()
        conn.close()
        messagebox.showinfo("成功", "访客注册成功！")

if __name__ == "__main__":
    register_visitor()