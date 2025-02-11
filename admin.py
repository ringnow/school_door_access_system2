import cv2
import dlib
import numpy as np
import sqlite3
from face_recognition import open_camera, close_camera, process_frame, recognize_face_from_frame, register_face
from tkinter import simpledialog, messagebox, Toplevel, Label, Button, Entry, Frame

def initialize_admin():
    conn = sqlite3.connect('school_door_access_system.db')
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
        id_number TEXT NOT NULL,
        phone TEXT NOT NULL,
        visit_time TEXT NOT NULL,
        approved BOOLEAN DEFAULT 0,
        face_data BLOB NOT NULL
    )
    """)
    cursor.execute("SELECT * FROM administrators WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)",
                       ("admin", "admin123", np.zeros(128).tobytes()))
        print("初始化管理员已创建，用户名: admin, 密码: admin123")
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
        conn = sqlite3.connect('school_door_access_system.db')
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
    if not name:
        messagebox.showerror("注册失败", "用户名不能为空")
        return
    register_face("administrators", name)

def manage_students(root):
    new_window = Toplevel(root)
    new_window.title("管理学生信息")
    new_window.geometry("400x400")
    Label(new_window, text="学生信息管理界面").pack()

    def refresh_students():
        for widget in new_window.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM students")
        students = cursor.fetchall()
        conn.close()

        for student in students:
            student_frame = Frame(new_window)
            student_frame.pack(fill="x")
            Label(student_frame, text=student[0]).pack(side="left")
            Button(student_frame, text="删除", command=lambda s=student[0]: delete_student(s)).pack(side="right")
            Button(student_frame, text="修改", command=lambda s=student[0]: update_student(s)).pack(side="right")

    def delete_student(username):
        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_students()

    def add_student():
        new_student_window = Toplevel(new_window)
        new_student_window.title("添加学生")
        Label(new_student_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(new_student_window)
        username_entry.grid(row=0, column=1)

        def capture_face():
            name = username_entry.get()
            if name:
                register_face("students", name)
                refresh_students()
                new_student_window.destroy()
            else:
                messagebox.showerror("添加失败", "用户名不能为空")

        Button(new_student_window, text="录入人脸", command=capture_face).grid(row=1, column=1)

    def update_student(username):
        update_window = Toplevel(new_window)
        update_window.title("修改学生信息")
        Label(update_window, text="新用户名").grid(row=0, column=0)
        new_username_entry = Entry(update_window)
        new_username_entry.grid(row=0, column=1)

        def save_updated_student():
            new_username = new_username_entry.get()
            if new_username:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE students SET username=? WHERE username=?", (new_username, username))
                conn.commit()
                conn.close()
                refresh_students()
                update_window.destroy()
            else:
                messagebox.showerror("修改失败", "新用户名不能为空")

        Button(update_window, text="保存", command=save_updated_student).grid(row=1, column=1)

    def search_student():
        search_window = Toplevel(new_window)
        search_window.title("查找学生")
        Label(search_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(search_window)
        username_entry.grid(row=0, column=1)

        def execute_search():
            username = username_entry.get()
            if username:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM students WHERE username=?", (username,))
                student = cursor.fetchone()
                conn.close()
                if student:
                    messagebox.showinfo("查找结果", f"学生信息：{student}")
                else:
                    messagebox.showinfo("查找结果", "未找到该学生信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加学生", command=add_student).pack()
    Button(new_window, text="查找学生", command=search_student).pack()
    refresh_students()

def manage_visitors(root):
    new_window = Toplevel(root)
    new_window.title("管理访客信息")
    new_window.geometry("400x400")
    Label(new_window, text="访客信息管理界面").pack()

    def refresh_visitors():
        for widget in new_window.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM visitors")
        visitors = cursor.fetchall()
        conn.close()

        for visitor in visitors:
            visitor_frame = Frame(new_window)
            visitor_frame.pack(fill="x")
            Label(visitor_frame, text=visitor[0]).pack(side="left")
            Button(visitor_frame, text="删除", command=lambda v=visitor[0]: delete_visitor(v)).pack(side="right")
            Button(visitor_frame, text="修改", command=lambda v=visitor[0]: update_visitor(v)).pack(side="right")

    def delete_visitor(username):
        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visitors WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_visitors()

    def add_visitor():
        new_visitor_window = Toplevel(new_window)
        new_visitor_window.title("添加访客")
        Label(new_visitor_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(new_visitor_window)
        username_entry.grid(row=0, column=1)
        Label(new_visitor_window, text="身份证号码").grid(row=1, column=0)
        id_number_entry = Entry(new_visitor_window)
        id_number_entry.grid(row=1, column=1)
        Label(new_visitor_window, text="电话号码").grid(row=2, column=0)
        phone_entry = Entry(new_visitor_window)
        phone_entry.grid(row=2, column=1)
        Label(new_visitor_window, text="访问时间").grid(row=3, column=0)
        visit_time_entry = Entry(new_visitor_window)
        visit_time_entry.grid(row=3, column=1)

        def capture_face():
            name = username_entry.get()
            id_number = id_number_entry.get()
            phone = phone_entry.get()
            visit_time = visit_time_entry.get()
            if name and id_number and phone and visit_time:
                register_face("visitors", name, "", id_number, phone, visit_time)
                refresh_visitors()
                new_visitor_window.destroy()
            else:
                messagebox.showerror("添加失败", "所有字段均不能为空")

        Button(new_visitor_window, text="录入人脸", command=capture_face).grid(row=4, column=1)

    def update_visitor(username):
        update_window = Toplevel(new_window)
        update_window.title("修改访客信息")
        Label(update_window, text="新用户名").grid(row=0, column=0)
        new_username_entry = Entry(update_window)
        new_username_entry.grid(row=0, column=1)
        Label(update_window, text="身份证号码").grid(row=1, column=0)
        new_id_number_entry = Entry(update_window)
        new_id_number_entry.grid(row=1, column=1)
        Label(update_window, text="电话号码").grid(row=2, column=0)
        new_phone_entry = Entry(update_window)
        new_phone_entry.grid(row=2, column=1)
        Label(update_window, text="访问时间").grid(row=3, column=0)
        new_visit_time_entry = Entry(update_window)
        new_visit_time_entry.grid(row=3, column=1)

        def save_updated_visitor():
            new_username = new_username_entry.get()
            new_id_number = new_id_number_entry.get()
            new_phone = new_phone_entry.get()
            new_visit_time = new_visit_time_entry.get()
            if new_username and new_id_number and new_phone and new_visit_time:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE visitors 
                    SET username=?, id_number=?, phone=?, visit_time=? 
                    WHERE username=?
                """, (new_username, new_id_number, new_phone, new_visit_time, username))
                conn.commit()
                conn.close()
                refresh_visitors()
                update_window.destroy()
            else:
                messagebox.showerror("修改失败", "所有字段均不能为空")

        Button(update_window, text="保存", command=save_updated_visitor).grid(row=4, column=1)

    def search_visitor():
        search_window = Toplevel(new_window)
        search_window.title("查找访客")
        Label(search_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(search_window)
        username_entry.grid(row=0, column=1)

        def execute_search():
            username = username_entry.get()
            if username:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM visitors WHERE username=?", (username,))
                visitor = cursor.fetchone()
                conn.close()
                if visitor:
                    messagebox.showinfo("查找结果", f"访客信息：{visitor}")
                else:
                    messagebox.showinfo("查找结果", "未找到该访客信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加访客", command=add_visitor).pack()
    Button(new_window, text="查找访客", command=search_visitor).pack()
    refresh_visitors()

def manage_admins(root):
    new_window = Toplevel(root)
    new_window.title("管理管理员信息")
    new_window.geometry("400x400")

    Label(new_window, text="管理员信息管理界面").pack()

    def refresh_admins():
        for widget in new_window.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM administrators")
        admins = cursor.fetchall()
        conn.close()

        for admin in admins:
            admin_frame = Frame(new_window)
            admin_frame.pack(fill="x")
            Label(admin_frame, text=admin[0]).pack(side="left")
            Button(admin_frame, text="删除", command=lambda a=admin[0]: delete_admin(a)).pack(side="right")
            Button(admin_frame, text="修改", command=lambda a=admin[0]: update_admin(a)).pack(side="right")

    def delete_admin(username):
        if username == "admin":
            messagebox.showerror("删除失败", "不能删除初始管理员")
            return
        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM administrators WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_admins()

    def add_admin():
        new_admin_window = Toplevel(new_window)
        new_admin_window.title("添加管理员")
        Label(new_admin_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(new_admin_window)
        username_entry.grid(row=0, column=1)
        Label(new_admin_window, text="密码").grid(row=1, column=0)
        password_entry = Entry(new_admin_window, show='*')
        password_entry.grid(row=1, column=1)

        def capture_face():
            name = username_entry.get()
            password = password_entry.get()
            if name and password:
                register_face("administrators", name, password)
                refresh_admins()
                new_admin_window.destroy()
            else:
                messagebox.showerror("添加失败", "用户名或密码不能为空")

        Button(new_admin_window, text="录入人脸", command=capture_face).grid(row=2, column=1)

    def update_admin(username):
        update_window = Toplevel(new_window)
        update_window.title("修改管理员信息")
        Label(update_window, text="新用户名").grid(row=0, column=0)
        new_username_entry = Entry(update_window)
        new_username_entry.grid(row=0, column=1)
        Label(update_window, text="新密码").grid(row=1, column=0)
        new_password_entry = Entry(update_window, show='*')
        new_password_entry.grid(row=1, column=1)

        def save_updated_admin():
            new_username = new_username_entry.get()
            new_password = new_password_entry.get()
            if new_username and new_password:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE administrators SET username=?, password=? WHERE username=?", (new_username, new_password, username))
                conn.commit()
                conn.close()
                refresh_admins()
                update_window.destroy()
            else:
                messagebox.showerror("修改失败", "新用户名和新密码不能为空")

        Button(update_window, text="保存", command=save_updated_admin).grid(row=2, column=1)

    def search_admin():
        search_window = Toplevel(new_window)
        search_window.title("查找管理员")
        Label(search_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(search_window)
        username_entry.grid(row=0, column=1)

        def execute_search():
            username = username_entry.get()
            if username:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM administrators WHERE username=?", (username,))
                admin = cursor.fetchone()
                conn.close()
                if admin:
                    messagebox.showinfo("查找结果", f"管理员信息：{admin}")
                else:
                    messagebox.showinfo("查找结果", "未找到该管理员信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加管理员", command=add_admin).pack()
    Button(new_window, text="查找管理员", command=search_admin).pack()
    refresh_admins()