import tkinter as tk
from tkinter import messagebox
from student import student_register, student_login
from admin import admin_login, manage_students, manage_visitors, admin_register
from visitor import register_visitor, visitor_login
from face_recognition import recognize_face
import cv2
from PIL import Image, ImageTk

# 设置中文支持
import locale
locale.setlocale(locale.LC_ALL, '')

# 创建主窗口
root = tk.Tk()
root.title("学校门禁系统")
root.geometry("800x600")  # 设置窗口大小为800x600

# 初始化全局变量
admin_logged_in = False

# 定义按钮点击事件
def on_student_register():
    student_register()

def on_student_login():
    if recognize_face("students"):
        messagebox.showinfo("登录成功", "学生登录成功")
    else:
        messagebox.showerror("登录失败", "未能识别学生")

def on_admin_register():
    admin_register()

def on_admin_login():
    global admin_logged_in
    admin_id = admin_login()
    if admin_id:
        admin_logged_in = True
        btn_manage_students.grid(row=3, column=0, padx=20, pady=20)
        btn_manage_visitors.grid(row=3, column=1, padx=20, pady=20)
        btn_admin_register.grid(row=3, column=2, padx=20, pady=20)
        btn_logout.grid(row=4, column=1, padx=20, pady=20)

def on_logout():
    global admin_logged_in
    admin_logged_in = False
    btn_manage_students.grid_forget()
    btn_manage_visitors.grid_forget()
    btn_admin_register.grid_forget()
    btn_logout.grid_forget()

def on_manage_students():
    manage_students(root)

def on_register_visitor():
    register_visitor()

def on_visitor_login():
    if recognize_face("visitors"):
        messagebox.showinfo("登录成功", "访客登录成功")
    else:
        messagebox.showerror("登录失败", "未能识别访客")

def on_manage_visitors():
    manage_visitors(root)

# 创建按钮并布局
btn_student_register = tk.Button(root, text="学生注册", command=on_student_register, width=20, height=2)
btn_student_register.grid(row=0, column=0, padx=20, pady=20)

btn_student_login = tk.Button(root, text="学生登录", command=on_student_login, width=20, height=2)
btn_student_login.grid(row=0, column=1, padx=20, pady=20)

btn_admin_login = tk.Button(root, text="管理员登录", command=on_admin_login, width=20, height=2)
btn_admin_login.grid(row=1, column=1, padx=20, pady=20)

btn_visitor_login = tk.Button(root, text="访客登录", command=on_visitor_login, width=20, height=2)
btn_visitor_login.grid(row=2, column=0, padx=20, pady=20)

btn_register_visitor = tk.Button(root, text="访客注册", command=on_register_visitor, width=20, height=2)
btn_register_visitor.grid(row=2, column=1, padx=20, pady=20)

btn_manage_students = tk.Button(root, text="管理学生信息", command=on_manage_students, width=20, height=2)
btn_manage_visitors = tk.Button(root, text="管理访客信息", command=on_manage_visitors, width=20, height=2)
btn_admin_register = tk.Button(root, text="管理员注册", command=on_admin_register, width=20, height=2)
btn_logout = tk.Button(root, text="退出登录", command=on_logout, width=20, height=2)

# 创建人脸识别窗口
face_frame = tk.Frame(root, width=320, height=240)
face_frame.grid(row=0, column=2, rowspan=3, padx=20, pady=20)
face_label = tk.Label(face_frame)
face_label.pack()

def update_frame():
    ret, frame = cap.read()
    if ret:
        frame = cv2.resize(frame, (320, 240))
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        face_label.imgtk = imgtk
        face_label.configure(image=imgtk)
    face_label.after(10, update_frame)

cap = cv2.VideoCapture(1)
update_frame()

# 运行主循环
root.mainloop()