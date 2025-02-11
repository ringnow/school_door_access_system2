import sqlite3
from face_recognition import register_face, recognize_face_from_frame, open_camera
import tkinter as tk
from tkinter import simpledialog, messagebox

cap = None

def register_visitor():
    name = simpledialog.askstring("输入", "请输入访客姓名:")
    id_number = simpledialog.askstring("输入", "请输入访客身份证号:")
    phone = simpledialog.askstring("输入", "请输入访客电话:")
    visit_time = simpledialog.askstring("输入", "请输入访问时间 (YYYY-MM-DD HH:MM):")

    if name and id_number and phone and visit_time:
        # 进行人脸识别注册
        print("请面对摄像头进行注册...")
        register_face("visitors", name, id_number, phone, visit_time)

def visitor_login():
    global cap
    if cap is None:
        cap = open_camera()
    ret, frame = cap.read()
    if ret:
        visitor_id = recognize_face_from_frame(frame, "visitors")
        if visitor_id:
            messagebox.showinfo("登录成功", f"欢迎, {visitor_id}!")
        else:
            messagebox.showerror("登录失败", "未能识别访客!")