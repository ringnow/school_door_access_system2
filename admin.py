from face_recognition import register_face, recognize_face_from_frame
import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox


def admin_register():
    username = simpledialog.askstring("输入", "请输入管理员用户名:")
    password = simpledialog.askstring("输入", "请输入管理员密码:", show='*')
    if username and password:
        register_face("administrators", username, password)


def admin_login():
    global cap
    username = simpledialog.askstring("输入", "请输入管理员用户名:")
    password = simpledialog.askstring("输入", "请输入管理员密码:", show='*')

    # 初始账号密码
    default_username = "admin"
    default_password = "123456"

    if username == default_username and password == default_password:
        messagebox.showinfo("登录成功", f"欢迎, {username}!")
        return username, True  # 返回是否为初始管理员

    if username and password:
        ret, frame = cap.read()
        if ret:
            user_id = recognize_face_from_frame(frame, "administrators")
            if user_id == username:
                messagebox.showinfo("登录成功", f"欢迎, {username}!")
                return username, False  # 返回是否为初始管理员
            else:
                messagebox.showerror("登录失败", "用户名或密码或人脸识别错误！")
    return None, False


def manage_students(root):
    manage_window = tk.Toplevel(root)
    manage_window.title("管理学生信息")
    manage_window.geometry("800x600")

    def refresh_student_list():
        for widget in student_list_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        for student in students:
            student_label = tk.Label(student_list_frame, text=f"ID: {student[0]}, 姓名: {student[1]}")
            student_label.pack(anchor="w")
        conn.close()

    def add_student():
        name = simpledialog.askstring("输入", "请输入学生姓名:", parent=manage_window)
        if name:
            register_face("students", name)
            refresh_student_list()

    def update_student():
        student_id = simpledialog.askstring("输入", "请输入要修改的学生ID:", parent=manage_window)
        new_name = simpledialog.askstring("输入", "请输入新的学生姓名:", parent=manage_window)
        if student_id and new_name:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE students SET name=? WHERE id=?", (new_name, student_id))
            conn.commit()
            conn.close()
            refresh_student_list()

    def delete_student():
        student_id = simpledialog.askstring("输入", "请输入要删除的学生ID:", parent=manage_window)
        if student_id:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            conn.commit()
            conn.close()
            refresh_student_list()

    student_list_frame = tk.Frame(manage_window)
    student_list_frame.pack(fill="both", expand=True)

    refresh_student_list()

    btn_add_student = tk.Button(manage_window, text="添加学生", command=add_student)
    btn_add_student.pack(side="left", padx=20, pady=20)

    btn_update_student = tk.Button(manage_window, text="修改学生", command=update_student)
    btn_update_student.pack(side="left", padx=20, pady=20)

    btn_delete_student = tk.Button(manage_window, text="删除学生", command=delete_student)
    btn_delete_student.pack(side="left", padx=20, pady=20)


def manage_visitors(root):
    manage_window = tk.Toplevel(root)
    manage_window.title("管理访客信息")
    manage_window.geometry("800x600")

    def refresh_visitor_list():
        for widget in visitor_list_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visitors")
        visitors = cursor.fetchall()
        for visitor in visitors:
            visitor_label = tk.Label(visitor_list_frame, text=f"ID: {visitor[0]}, 姓名: {visitor[1]}")
            visitor_label.pack(anchor="w")
        conn.close()

    def add_visitor():
        name = simpledialog.askstring("输入", "请输入访客姓名:", parent=manage_window)
        if name:
            register_face("visitors", name)
            refresh_visitor_list()

    def update_visitor():
        visitor_id = simpledialog.askstring("输入", "请输入要修改的访客ID:", parent=manage_window)
        new_name = simpledialog.askstring("输入", "请输入新的访客姓名:", parent=manage_window)
        if visitor_id and new_name:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE visitors SET name=? WHERE id=?", (new_name, visitor_id))
            conn.commit()
            conn.close()
            refresh_visitor_list()

    def delete_visitor():
        visitor_id = simpledialog.askstring("输入", "请输入要删除的访客ID:", parent=manage_window)
        if visitor_id:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM visitors WHERE id=?", (visitor_id,))
            conn.commit()
            conn.close()
            refresh_visitor_list()

    visitor_list_frame = tk.Frame(manage_window)
    visitor_list_frame.pack(fill="both", expand=True)

    refresh_visitor_list()

    btn_add_visitor = tk.Button(manage_window, text="添加访客", command=add_visitor)
    btn_add_visitor.pack(side="left", padx=20, pady=20)

    btn_update_visitor = tk.Button(manage_window, text="修改访客", command=update_visitor)
    btn_update_visitor.pack(side="left", padx=20, pady=20)

    btn_delete_visitor = tk.Button(manage_window, text="删除访客", command=delete_visitor)
    btn_delete_visitor.pack(side="left", padx=20, pady=20)


def manage_admins(root):
    manage_window = tk.Toplevel(root)
    manage_window.title("管理管理员信息")
    manage_window.geometry("800x600")

    def refresh_admin_list():
        for widget in admin_list_frame.winfo_children():
            widget.destroy()
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM administrators")
        admins = cursor.fetchall()
        for admin in admins:
            admin_label = tk.Label(admin_list_frame, text=f"ID: {admin[0]}, 用户名: {admin[1]}")
            admin_label.pack(anchor="w")
        conn.close()

    def add_admin():
        username = simpledialog.askstring("输入", "请输入管理员用户名:", parent=manage_window)
        password = simpledialog.askstring("输入", "请输入管理员密码:", show='*', parent=manage_window)
        if username and password:
            register_face("administrators", username, password)
            refresh_admin_list()

    def update_admin():
        admin_id = simpledialog.askstring("输入", "请输入要修改的管理员ID:", parent=manage_window)
        new_username = simpledialog.askstring("输入", "请输入新的管理员用户名:", parent=manage_window)
        if admin_id and new_username:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE administrators SET username=? WHERE id=?", (new_username, admin_id))
            conn.commit()
            conn.close()
            refresh_admin_list()

    def delete_admin():
        admin_id = simpledialog.askstring("输入", "请输入要删除的管理员ID:", parent=manage_window)
        if admin_id:
            conn = sqlite3.connect('school_door.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM administrators WHERE id=?", (admin_id,))
            conn.commit()
            conn.close()
            refresh_admin_list()

    admin_list_frame = tk.Frame(manage_window)
    admin_list_frame.pack(fill="both", expand=True)

    refresh_admin_list()

    btn_add_admin = tk.Button(manage_window, text="添加管理员", command=add_admin)
    btn_add_admin.pack(side="left", padx=20, pady=20)

    btn_update_admin = tk.Button(manage_window, text="修改管理员", command=update_admin)
    btn_update_admin.pack(side="left", padx=20, pady=20)

    btn_delete_admin = tk.Button(manage_window, text="删除管理员", command=delete_admin)
    btn_delete_admin.pack(side="left", padx=20, pady=20)