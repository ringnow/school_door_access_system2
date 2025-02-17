import cv2
import dlib
import numpy as np
import sqlite3
from datetime import datetime
from tkinter import simpledialog, messagebox, Toplevel, Label, Button, Entry, Frame, Checkbutton
import tkinter as tk
from face_recognition import open_camera, close_camera, process_frame, recognize_face_from_frame, register_face


def initialize_admin():
    """
    初始化数据库并创建表格（管理员、学生和访客）。
    如果没有初始管理员账户，则创建一个默认的初始管理员账户。
    如果visitors表缺少entry_time、exit_time或approved字段，通过ALTER TABLE补充这些字段。
    """
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
        approved INTEGER DEFAULT 0,
        face_data BLOB NOT NULL,
        entry_time TEXT DEFAULT '1970-01-01 00:00:00',
        exit_time TEXT DEFAULT '1970-01-01 00:00:00'
    )
    """)
    # 补充可能缺失的字段
    cursor.execute("PRAGMA table_info(visitors)")
    columns = [info[1] for info in cursor.fetchall()]
    if "entry_time" not in columns:
        cursor.execute("ALTER TABLE visitors ADD COLUMN entry_time TEXT DEFAULT '1970-01-01 00:00:00'")
    if "exit_time" not in columns:
        cursor.execute("ALTER TABLE visitors ADD COLUMN exit_time TEXT DEFAULT '1970-01-01 00:00:00'")
    if "approved" not in columns:
        cursor.execute("ALTER TABLE visitors ADD COLUMN approved INTEGER DEFAULT 0")

    cursor.execute("SELECT * FROM administrators WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO administrators (username, password, face_data) VALUES (?, ?, ?)",
                       ("admin", "admin123", np.zeros(128, dtype=np.float32).tobytes()))
        print("初始化管理员已创建，用户名: admin, 密码: admin123")
    conn.commit()
    conn.close()


def admin_login():
    """
    管理员登录功能。首先通过用户名和密码验证管理员账户。
    对于非初始管理员，还需通过人脸识别进行验证。
    Returns:
        username: 登录成功的用户名
        is_initial: 是否为初始管理员
    """
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
    """
    管理员注册功能。输入用户名和密码，通过录入人脸信息方式注册新管理员。
    """
    name = simpledialog.askstring("管理员注册", "请输入管理员用户名")
    password = simpledialog.askstring("管理员注册", "请输入管理员密码", show='*')
    if not name or not password:
        messagebox.showerror("注册失败", "用户名或密码不能为空")
        return
    register_face("administrators", name, password)


def manage_students(root):
    """
    管理学生信息的功能，包括添加、删除、修改、查找学生信息。
    """
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
        cursor.execute("SELECT id, username FROM students")
        students = cursor.fetchall()
        conn.close()

        for student in students:
            student_frame = Frame(new_window)
            student_frame.pack(fill="x", pady=5)
            info_text = f"ID: {student[0]}  用户名: {student[1]}"
            Label(student_frame, text=info_text).pack(side="left")
            Button(student_frame, text="删除", command=lambda s=student[1]: delete_student(s)).pack(side="right")
            Button(student_frame, text="修改", command=lambda s=student[1]: update_student(s)).pack(side="right")

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
                register_face("students", name, "")
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
                cursor.execute("SELECT id, username FROM students WHERE username=?", (username,))
                student = cursor.fetchone()
                conn.close()
                if student:
                    messagebox.showinfo("查找结果", f"学生信息：ID: {student[0]}, 用户名: {student[1]}")
                else:
                    messagebox.showinfo("查找结果", "未找到该学生信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加学生", command=add_student).pack()
    Button(new_window, text="查找学生", command=search_student).pack()
    refresh_students()


def manage_visitors(root):
    """
    管理访客信息的功能，包括添加、删除、修改和查找访客信息。
    访客注册后默认approved为0，只有管理员批准后才能登录。
    同时支持完整的日期和时间录入。
    """
    new_window = Toplevel(root)
    new_window.title("管理访客信息")
    new_window.geometry("550x500")
    Label(new_window, text="访客信息管理界面").pack()

    def refresh_visitors():
        for widget in new_window.winfo_children():
            if isinstance(widget, Frame):
                widget.destroy()

        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, id_number, phone, entry_time, exit_time, approved FROM visitors")
        visitors = cursor.fetchall()
        conn.close()

        for visitor in visitors:
            visitor_frame = Frame(new_window)
            visitor_frame.pack(fill="x", pady=5)
            approved_text = '已批准' if visitor[6] == 1 else '未批准'
            info_text = (f"ID: {visitor[0]}  用户名: {visitor[1]}  身份证号: {visitor[2]}  电话: {visitor[3]}  "
                         f"入校时间: {visitor[4]}  离校时间: {visitor[5]}  批准状态: {approved_text}")
            Label(visitor_frame, text=info_text).pack(side="left")
            Button(visitor_frame, text="删除", command=lambda v=visitor[1]: delete_visitor(v)).pack(side="right")
            Button(visitor_frame, text="修改", command=lambda v=visitor[1]: update_visitor(v)).pack(side="right")
            if visitor[6] == 0:  # 如果未批准，显示批准按钮
                Button(visitor_frame, text="批准", command=lambda v=visitor[1]: approve_visitor(v)).pack(side="right")

    def delete_visitor(username):
        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM visitors WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_visitors()

    def approve_visitor(username):
        conn = sqlite3.connect('school_door_access_system.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE visitors SET approved=1 WHERE username=?", (username,))
        conn.commit()
        conn.close()
        refresh_visitors()

    def add_visitor():
        new_visitor_window = Toplevel(new_window)
        new_visitor_window.title("添加访客")
        # 基本信息
        Label(new_visitor_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(new_visitor_window)
        username_entry.grid(row=0, column=1)
        Label(new_visitor_window, text="身份证号码").grid(row=1, column=0)
        id_number_entry = Entry(new_visitor_window)
        id_number_entry.grid(row=1, column=1)
        Label(new_visitor_window, text="电话号码").grid(row=2, column=0)
        phone_entry = Entry(new_visitor_window)
        phone_entry.grid(row=2, column=1)
        # 入校和离校时间（日期与时间分开录入）
        Label(new_visitor_window, text="入校日期 (YYYY-MM-DD)").grid(row=3, column=0)
        entry_date_entry = Entry(new_visitor_window)
        entry_date_entry.grid(row=3, column=1)
        Label(new_visitor_window, text="入校时间 (HH:MM:SS)").grid(row=4, column=0)
        entry_time_entry = Entry(new_visitor_window)
        entry_time_entry.grid(row=4, column=1)
        Label(new_visitor_window, text="离校日期 (YYYY-MM-DD)").grid(row=5, column=0)
        exit_date_entry = Entry(new_visitor_window)
        exit_date_entry.grid(row=5, column=1)
        Label(new_visitor_window, text="离校时间 (HH:MM:SS)").grid(row=6, column=0)
        exit_time_entry = Entry(new_visitor_window)
        exit_time_entry.grid(row=6, column=1)

        def capture_face():
            name = username_entry.get()
            id_number = id_number_entry.get()
            phone = phone_entry.get()
            entry_date = entry_date_entry.get()
            entry_time_val = entry_time_entry.get()
            exit_date = exit_date_entry.get()
            exit_time_val = exit_time_entry.get()
            if name and id_number and phone and entry_date and entry_time_val and exit_date and exit_time_val:
                entry_time_full = f"{entry_date} {entry_time_val}"
                exit_time_full = f"{exit_date} {exit_time_val}"
                # 访客注册后默认approved为0，待管理员审批
                register_face("visitors", name, "", id_number, phone, entry_time_full, exit_time_full)
                refresh_visitors()
                new_visitor_window.destroy()
            else:
                messagebox.showerror("添加失败", "所有字段均不能为空")

        Button(new_visitor_window, text="录入人脸", command=capture_face).grid(row=7, column=1)

    def update_visitor(username):
        update_window = Toplevel(new_window)
        update_window.title("修改访客信息")
        # 修改基本信息
        Label(update_window, text="新用户名").grid(row=0, column=0)
        new_username_entry = Entry(update_window)
        new_username_entry.grid(row=0, column=1)
        Label(update_window, text="新的身份证号码").grid(row=1, column=0)
        new_id_number_entry = Entry(update_window)
        new_id_number_entry.grid(row=1, column=1)
        Label(update_window, text="新的电话号码").grid(row=2, column=0)
        new_phone_entry = Entry(update_window)
        new_phone_entry.grid(row=2, column=1)
        # 修改入校和离校时间
        Label(update_window, text="新入校日期 (YYYY-MM-DD)").grid(row=3, column=0)
        new_entry_date_entry = Entry(update_window)
        new_entry_date_entry.grid(row=3, column=1)
        Label(update_window, text="新入校时间 (HH:MM:SS)").grid(row=4, column=0)
        new_entry_time_entry = Entry(update_window)
        new_entry_time_entry.grid(row=4, column=1)
        Label(update_window, text="新离校日期 (YYYY-MM-DD)").grid(row=5, column=0)
        new_exit_date_entry = Entry(update_window)
        new_exit_date_entry.grid(row=5, column=1)
        Label(update_window, text="新离校时间 (HH:MM:SS)").grid(row=6, column=0)
        new_exit_time_entry = Entry(update_window)
        new_exit_time_entry.grid(row=6, column=1)
        # 新增批准状态修改选项
        Label(update_window, text="是否批准").grid(row=7, column=0)
        approved_var = tk.BooleanVar()
        approved_check = Checkbutton(update_window, variable=approved_var)
        approved_check.grid(row=7, column=1)

        def save_updated_visitor():
            new_username = new_username_entry.get()
            new_id_number = new_id_number_entry.get()
            new_phone = new_phone_entry.get()
            new_entry_date = new_entry_date_entry.get()
            new_entry_time = new_entry_time_entry.get()
            new_exit_date = new_exit_date_entry.get()
            new_exit_time = new_exit_time_entry.get()
            if new_username and new_id_number and new_phone and new_entry_date and new_entry_time and new_exit_date and new_exit_time:
                new_entry_time_full = f"{new_entry_date} {new_entry_time}"
                new_exit_time_full = f"{new_exit_date} {new_exit_time}"
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE visitors 
                    SET username=?, id_number=?, phone=?, entry_time=?, exit_time=?, approved=?
                    WHERE username=?
                """, (new_username, new_id_number, new_phone, new_entry_time_full, new_exit_time_full,
                      1 if approved_var.get() else 0, username))
                conn.commit()
                conn.close()
                refresh_visitors()
                update_window.destroy()
            else:
                messagebox.showerror("修改失败", "所有字段均不能为空")

        Button(update_window, text="保存", command=save_updated_visitor).grid(row=8, column=1)

    def search_visitor():
        search_window = Toplevel(new_window)
        search_window.title("查找访客")
        Label(search_window, text="用户名").grid(row=0, column=0)
        username_entry = Entry(search_window)
        username_entry.grid(row=0, column=1)

        def execute_search():
            uname = username_entry.get()
            if uname:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, id_number, phone, entry_time, exit_time, approved 
                    FROM visitors WHERE username=?
                """, (uname,))
                visitor = cursor.fetchone()
                conn.close()
                if visitor:
                    approved_text = "已批准" if visitor[6] == 1 else "未批准"
                    messagebox.showinfo("查找结果",
                                        f"访客信息：ID: {visitor[0]}, 用户名: {visitor[1]}, 身份证号: {visitor[2]}, 电话: {visitor[3]}, 入校时间: {visitor[4]}, 离校时间: {visitor[5]}, 批准状态: {approved_text}")
                else:
                    messagebox.showinfo("查找结果", "未找到该访客信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加访客", command=add_visitor).pack()
    Button(new_window, text="查找访客", command=search_visitor).pack()
    refresh_visitors()


def manage_admins(root):
    """
    管理管理员信息的功能，包括添加、删除、修改和查找管理员信息。
    不允许删除初始管理员。
    """
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
        cursor.execute("SELECT id, username, password FROM administrators")
        admins = cursor.fetchall()
        conn.close()

        for admin in admins:
            admin_frame = Frame(new_window)
            admin_frame.pack(fill="x", pady=5)
            info_text = f"ID: {admin[0]}  用户名: {admin[1]}  密码: {admin[2]}"
            Label(admin_frame, text=info_text).pack(side="left")
            Button(admin_frame, text="删除", command=lambda a=admin[1]: delete_admin(a)).pack(side="right")
            Button(admin_frame, text="修改", command=lambda a=admin[1]: update_admin(a)).pack(side="right")

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
                cursor.execute("UPDATE administrators SET username=?, password=? WHERE username=?",
                               (new_username, new_password, username))
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
            uname = username_entry.get()
            if uname:
                conn = sqlite3.connect('school_door_access_system.db')
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, password FROM administrators WHERE username=?", (uname,))
                admin = cursor.fetchone()
                conn.close()
                if admin:
                    messagebox.showinfo("查找结果", f"管理员信息：ID: {admin[0]}, 用户名: {admin[1]}, 密码: {admin[2]}")
                else:
                    messagebox.showinfo("查找结果", "未找到该管理员信息")
            else:
                messagebox.showerror("查找失败", "用户名不能为空")

        Button(search_window, text="查找", command=execute_search).grid(row=1, column=1)

    Button(new_window, text="添加管理员", command=add_admin).pack()
    Button(new_window, text="查找管理员", command=search_admin).pack()
    refresh_admins()


def visitor_login():
    """
    访客登录功能：
      1. 用户输入用户名。
      2. 检查访客是否存在且已被管理员批准（approved==1）。
      3. 检查当前时间是否在入校时间与离校时间之间，支持时分秒控制。
      4. 如果当前时间超过离校时间，则自动删除该访客信息，并登录失败。
    """
    username = simpledialog.askstring("访客登录", "请输入您的用户名")
    if not username:
        return
    conn = sqlite3.connect('school_door_access_system.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, entry_time, exit_time, approved FROM visitors WHERE username=?", (username,))
    record = cursor.fetchone()
    if not record:
        messagebox.showerror("登录失败", "访客信息不存在")
        conn.close()
        return
    visitor_id, entry_time_str, exit_time_str, approved = record
    if int(approved) != 1:
        messagebox.showerror("登录失败", "管理员尚未批准您的访问")
        conn.close()
        return
    try:
        entry_datetime = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
        exit_datetime = datetime.strptime(exit_time_str, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        try:
            entry_datetime = datetime.strptime(entry_time_str, "%Y-%m-%d")
            exit_datetime = datetime.strptime(exit_time_str, "%Y-%m-%d")
        except Exception as e:
            messagebox.showerror("登录失败", "时间格式错误")
            conn.close()
            return

    now = datetime.now()
    if now < entry_datetime:
        messagebox.showerror("登录失败", "当前时间早于入校时间")
        conn.close()
        return
    if now > exit_datetime:
        cursor.execute("DELETE FROM visitors WHERE id=?", (visitor_id,))
        conn.commit()
        messagebox.showerror("登录失败", "您的离校时间已过，访客信息已被自动删除")
        conn.close()
        return
    messagebox.showinfo("登录成功", "访客登录成功！")
    conn.close()


if __name__ == "__main__":
    # 初始化管理员和数据库表
    initialize_admin()
    root = tk.Tk()
    root.title("系统管理")
    root.geometry("300x350")
    Button(root, text="管理员注册", command=admin_register).pack(pady=10)
    Button(root, text="管理学生信息", command=lambda: manage_students(root)).pack(pady=10)
    Button(root, text="管理访客信息", command=lambda: manage_visitors(root)).pack(pady=10)
    Button(root, text="管理管理员信息", command=lambda: manage_admins(root)).pack(pady=10)
    Button(root, text="访客登录", command=visitor_login).pack(pady=10)
    root.mainloop()