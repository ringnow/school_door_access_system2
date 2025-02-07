from face_recognition import register_face, recognize_face
import sqlite3
import tkinter as tk
from tkinter import simpledialog, messagebox

def admin_register():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    username = simpledialog.askstring("输入", "请输入管理员用户名:", parent=root)
    password = simpledialog.askstring("输入", "请输入管理员密码:", parent=root, show='*')
    if username and password:
        register_face("administrators", username, password)

def admin_login():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    username = simpledialog.askstring("输入", "请输入管理员用户名:", parent=root)
    password = simpledialog.askstring("输入", "请输入管理员密码:", parent=root, show='*')
    if username and password:
        user_id = recognize_face("administrators")
        if user_id == username:
            messagebox.showinfo("登录成功", f"欢迎, {user_id}!")
            return user_id
        else:
            messagebox.showerror("登录失败", "用户名或密码错误！")
    return None

def manage_students():
    admin_id = admin_login()
    if admin_id:
        conn = sqlite3.connect('school_door.db')
        cursor = conn.cursor()
        while True:
            print("1. 查询学生信息")
            print("2. 修改学生信息")
            print("3. 删除学生信息")
            print("4. 退出")
            choice = simpledialog.askstring("输入", "请输入您的选择 (1-4):", parent=root)
            if choice == '1':
                cursor.execute("SELECT * FROM students")
                students = cursor.fetchall()
                for student in students:
                    messagebox.showinfo("学生信息", f"ID: {student[0]}, 姓名: {student[1]}")
            elif choice == '2':
                student_id = simpledialog.askstring("输入", "请输入要修改的学生ID:", parent=root)
                new_name = simpledialog.askstring("输入", "请输入新的学生姓名:", parent=root)
                cursor.execute("UPDATE students SET name=? WHERE id=?", (new_name, student_id))
                conn.commit()
                messagebox.showinfo("成功", "学生信息已更新！")
            elif choice == '3':
                student_id = simpledialog.askstring("输入", "请输入要删除的学生ID:", parent=root)
                cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
                conn.commit()
                messagebox.showinfo("成功", "学生信息已删除！")
            elif choice == '4':
                break
            else:
                messagebox.showerror("错误", "无效的选择！")
        conn.close()