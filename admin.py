import cv2
import dlib
import numpy as np
import sqlite3
from face_recognition import open_camera, close_camera, process_frame, recognize_face_from_frame
from tkinter import simpledialog, messagebox, Toplevel, Label, Button, Entry

def initialize_admin():
    conn = sqlite3.connect('school_door.db')
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS administrators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        face_data BLOB NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        face_data BLOB NOT NULL
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS visitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        face_data BLOB NOT NULL
    )
    """)
    cursor.execute("SELECT * FROM administrators WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)",
                       ("admin", "admin123", np.zeros(128).tobytes()))
        print("初始管理员已创建，用户名: admin, 密码: admin123")
    conn.commit()
    conn.close()

def admin_login():
    print("管理员登录...")
    username = simpledialog.askstring("管理员登录", "请输入用户名")
    password = simpledialog.askstring("管理员登录", "请输入密码", show='*')

    if not username or not password:
        messagebox.showerror("登录失败", "用户名或密码不能为空")
        return None, False

    try:
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM administrators WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result is None or result[0] != password:
            messagebox.showerror("登录失败", "用户名或密码错误")
            return None, False
    except Exception as e:
        print(e)
        return None, False

    if username == "admin":
        print(f"初始管理员 {username} 登录成功！")
        return username, True

    try:
        cap = open_camera()
    except Exception as e:
        print(e)
        return None, False

    window_name = "管理员登录"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法接收图像流。退出...")
            break

        frame, gray, faces = process_frame(frame)

        if faces:
            user_id = recognize_face_from_frame(frame, "administrators")
            if user_id == username:
                print(f"管理员 {user_id} 登录成功！")
                close_camera(cap)
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
                    cv2.destroyWindow(window_name)
                return user_id, False

        cv2.imshow(window_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    close_camera(cap)
    if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
        cv2.destroyWindow(window_name)
    print("摄像头已关闭，窗口已销毁。")
    return None, False

def admin_register():
    name = simpledialog.askstring("管理员注册", "请输入管理员用户名")
    password = simpledialog.askstring("管理员注册", "请输入管理员密码", show='*')
    if not name or not password:
        messagebox.showerror("注册失败", "用户名或密码不能为空")
        return
    register_face("administrators", name, password)

def manage_students(root):
    new_window = Toplevel(root)
    new_window.title("管理学生信息")
    new_window.geometry("400x300")
    Label(new_window, text="学生信息管理界面").pack()

    def refresh_students():
        for widget in new_window.winfo_children():
            widget.destroy()
        Label(new_window, text="学生信息管理界面").pack()

        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM students")
        students = cursor.fetchall()
        conn.close()

        for student in students:
            Label(new_window, text=student[0]).pack()
            Button(new_window, text="删除", command=lambda s=student[0]: delete_student(s)).pack()

    def delete_student(username):
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_students()

    refresh_students()

def manage_visitors(root):
    new_window = Toplevel(root)
    new_window.title("管理访客信息")
    new_window.geometry("400x300")
    Label(new_window, text="访客信息管理界面").pack()

    def refresh_visitors():
        for widget in new_window.winfo_children():
            widget.destroy()
        Label(new_window, text="访客信息管理界面").pack()

        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM visitors")
        visitors = cursor.fetchall()
        conn.close()

        for visitor in visitors:
            Label(new_window, text=visitor[0]).pack()
            Button(new_window, text="删除", command=lambda v=visitor[0]: delete_visitor(v)).pack()

    def delete_visitor(username):
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visitors WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_visitors()

    refresh_visitors()

def manage_admins(root):
    new_window = Toplevel(root)
    new_window.title("管理管理员信息")
    new_window.geometry("400x300")

    Label(new_window, text="管理员信息管理界面").pack()

    def refresh_admins():
        for widget in new_window.winfo_children():
            widget.destroy()
        Label(new_window, text="管理员信息管理界面").pack()

        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM administrators")
        admins = cursor.fetchall()
        conn.close()

        for admin in admins:
            Label(new_window, text=admin[0]).pack()
            Button(new_window, text="删除", command=lambda a=admin[0]: delete_admin(a)).pack()

    def delete_admin(username):
        if username == "admin":
            messagebox.showerror("删除失败", "不能删除初始管理员")
            return
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM administrators WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_admins()

    def add_admin():
        new_admin = Toplevel(new_window)
        new_admin.title("添加管理员")
        Label(new_admin, text="用户名").grid(row=0, column=0)
        username_entry = Entry(new_admin)
        username_entry.grid(row=0, column=1)
        Label(new_admin, text="密码").grid(row=1, column=0)
        password_entry = Entry(new_admin, show='*')
        password_entry.grid(row=1, column=1)

        def register_new_admin():
            username = username_entry.get()
            password = password_entry.get()
            if username and password:
                register_face("administrators", username, password)
                new_admin.destroy()
                refresh_admins()
            else:
                messagebox.showerror("注册失败", "用户名或密码不能为空")

        Button(new_admin, text="注册", command=register_new_admin).grid(row=2, column=1)

    Button(new_window, text="添加管理员", command=add_admin).pack()
    refresh_admins()