import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
import datetime
import threading
import time

def register_visitor(root):
    """
    访客注册功能，访客信息注册后需要管理员批准方可生效。
    """
    register_window = tk.Toplevel(root)
    register_window.title("访客注册")

    tk.Label(register_window, text="用户名:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(register_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(register_window, text="身份证号码:").grid(row=1, column=0, padx=10, pady=10)
    id_number_entry = tk.Entry(register_window)
    id_number_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(register_window, text="电话号码:").grid(row=2, column=0, padx=10, pady=10)
    phone_entry = tk.Entry(register_window)
    phone_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(register_window, text="入校日期:").grid(row=3, column=0, padx=10, pady=10)
    entry_date_entry = DateEntry(register_window, width=16, background='darkblue', foreground='white', borderwidth=2)
    entry_date_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(register_window, text="入校时间:").grid(row=4, column=0, padx=10, pady=10)
    entry_time_frame = tk.Frame(register_window)
    entry_time_frame.grid(row=4, column=1, padx=10, pady=10)

    entry_hour_spinbox = tk.Spinbox(entry_time_frame, from_=0, to=23, width=5, format="%02.0f")
    entry_hour_spinbox.grid(row=0, column=0)
    tk.Label(entry_time_frame, text=":").grid(row=0, column=1)
    entry_minute_spinbox = tk.Spinbox(entry_time_frame, from_=0, to=59, width=5, format="%02.0f")
    entry_minute_spinbox.grid(row=0, column=2)

    tk.Label(register_window, text="离校日期:").grid(row=5, column=0, padx=10, pady=10)
    exit_date_entry = DateEntry(register_window, width=16, background='darkblue', foreground='white', borderwidth=2)
    exit_date_entry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(register_window, text="离校时间:").grid(row=6, column=0, padx=10, pady=10)
    exit_time_frame = tk.Frame(register_window)
    exit_time_frame.grid(row=6, column=1, padx=10, pady=10)

    exit_hour_spinbox = tk.Spinbox(exit_time_frame, from_=0, to=23, width=5, format="%02.0f")
    exit_hour_spinbox.grid(row=0, column=0)
    tk.Label(exit_time_frame, text=":").grid(row=0, column=1)
    exit_minute_spinbox = tk.Spinbox(exit_time_frame, from_=0, to=59, width=5, format="%02.0f")
    exit_minute_spinbox.grid(row=0, column=2)

    def save_visitor():
        username = username_entry.get()
        id_number = id_number_entry.get()
        phone = phone_entry.get()
        entry_date = entry_date_entry.get_date().strftime("%Y-%m-%d")
        entry_time = f"{entry_hour_spinbox.get()}:{entry_minute_spinbox.get()}:00"
        exit_date = exit_date_entry.get_date().strftime("%Y-%m-%d")
        exit_time = f"{exit_hour_spinbox.get()}:{exit_minute_spinbox.get()}:00"
        entry_datetime = f"{entry_date} {entry_time}"
        exit_datetime = f"{exit_date} {exit_time}"
        visit_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 添加visit_time字段
        face_data = "default_face_data"  # 确保face_data字段有值

        if not username or not id_number or not phone:
            messagebox.showerror("注册失败", "所有字段都必须填写", parent=register_window)
            return

        try:
            datetime.datetime.strptime(entry_datetime, "%Y-%m-%d %H:%M:%S")
            datetime.datetime.strptime(exit_datetime, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("注册失败", "时间格式不正确", parent=register_window)
            return

        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO visitors (username, id_number, phone, entry_time, exit_time, visit_time, face_data, approved)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (username, id_number, phone, entry_datetime, exit_datetime, visit_time, face_data))
            conn.commit()
            conn.close()
            messagebox.showinfo("注册成功", "访客注册成功，等待管理员批准", parent=register_window)
            register_window.destroy()
        except sqlite3.IntegrityError as e:
            messagebox.showerror("注册失败", f"数据库错误：{e}", parent=register_window)
        except sqlite3.OperationalError as e:
            messagebox.showerror("注册失败", f"数据库被锁定：{e}", parent=register_window)

    save_button = tk.Button(register_window, text="保存", command=save_visitor)
    save_button.grid(row=7, column=1, padx=10, pady=10)

def visitor_login(root):
    """
    访客登录功能，只有在管理员批准后且登录时间在入校时间和离校时间之间才能登录成功。
    """
    login_window = tk.Toplevel(root)
    login_window.title("访客登录")

    tk.Label(login_window, text="用户名:").grid(row=0, column=0, padx=10, pady=10)
    username_entry = tk.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    def check_login():
        username = username_entry.get()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, entry_time, exit_time FROM visitors WHERE username=? AND approved=1", (username,))
            result = cursor.fetchone()
            conn.close()

            if result:
                visitor_id, entry_time, exit_time = result
                if entry_time <= current_time <= exit_time:
                    messagebox.showinfo("登录成功", "访客登录成功!", parent=login_window)
                else:
                    messagebox.showerror("登录失败", "当前时间不在允许的访问时间范围内", parent=login_window)
            else:
                messagebox.showerror("登录失败", "用户名不存在或未批准", parent=login_window)
        except sqlite3.OperationalError as e:
            messagebox.showerror("登录失败", f"数据库被锁定：{e}", parent=login_window)

    login_button = tk.Button(login_window, text="登录", command=check_login)
    login_button.grid(row=1, column=1, padx=10, pady=10)

def auto_delete_expired_visitors():
    """
    自动删除超过离校时间的访客信息。
    """
    while True:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            conn = sqlite3.connect('school_door_access_system.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM visitors WHERE exit_time < ?", (current_time,))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError as e:
            print(f"数据库被锁定：{e}")
        time.sleep(3600)  # 每小时检查一次

# 在主线程启动时，启动自动删除过期访客信息的线程
threading.Thread(target=auto_delete_expired_visitors, daemon=True).start()