import tkinter as tk
from tkinter import messagebox
from student import student_register, student_login
from admin import admin_register, admin_login, manage_students
from visitor import register_visitor

# 设置中文支持
import locale
locale.setlocale(locale.LC_ALL, '')

# 创建主窗口
root = tk.Tk()
root.title("学校门禁系统")
root.geometry("800x600")  # 设置窗口大小为800x600

# 定义按钮点击事件
def on_student_register():
    student_register()

def on_student_login():
    student_login()

def on_admin_register():
    admin_register()

def on_admin_login():
    admin_login()

def on_manage_students():
    manage_students()

def on_register_visitor():
    register_visitor()

# 创建按钮并布局
btn_student_register = tk.Button(root, text="学生注册", command=on_student_register, width=20, height=2)
btn_student_register.grid(row=0, column=0, padx=20, pady=20)

btn_student_login = tk.Button(root, text="学生登录", command=on_student_login, width=20, height=2)
btn_student_login.grid(row=0, column=1, padx=20, pady=20)

btn_admin_register = tk.Button(root, text="管理员注册", command=on_admin_register, width=20, height=2)
btn_admin_register.grid(row=1, column=0, padx=20, pady=20)

btn_admin_login = tk.Button(root, text="管理员登录", command=on_admin_login, width=20, height=2)
btn_admin_login.grid(row=1, column=1, padx=20, pady=20)

btn_manage_students = tk.Button(root, text="管理学生信息", command=on_manage_students, width=20, height=2)
btn_manage_students.grid(row=2, column=0, padx=20, pady=20)

btn_register_visitor = tk.Button(root, text="校外人员预约", command=on_register_visitor, width=20, height=2)
btn_register_visitor.grid(row=2, column=1, padx=20, pady=20)

# 运行主循环
root.mainloop()