import tkinter as tk
from tkinter import messagebox
from student import student_register, student_login
from admin import admin_login, manage_students, manage_visitors, admin_register, manage_admins, initialize_admin
from visitor import register_visitor, visitor_login
from face_recognition import recognize_face_from_frame
import cv2
from PIL import Image, ImageTk
import locale

locale.setlocale(locale.LC_ALL, '')

# 初始化数据库和初始管理员
initialize_admin()

# 全局变量
cap = None
admin_logged_in = False
is_initial_admin = False

# 按钮样式字典
button_style = {
    'bg': '#2980b9',
    'fg': 'white',
    'font': ('Helvetica', 12, 'bold'),
    'width': 16,
    'height': 2,
    'relief': 'raised',
    'bd': 2
}

def clear_frame(frame):
    """
    清空 frame 中所有的组件
    Args:
        frame: tkinter Frame 对象
    """
    for widget in frame.winfo_children():
        widget.destroy()

def start_face_capture(parent):
    """
    在parent中创建人脸识别窗口，并启动实时更新。
    Args:
        parent: 父窗口
    Returns:
        face_frame: 包含人脸识别窗口的 Frame 对象
    """
    face_frame = tk.Frame(parent, width=320, height=240, bg='#34495e')
    face_frame.grid_propagate(False)  # 固定大小，不随子组件大小变化
    face_label = tk.Label(face_frame)
    face_label.pack(expand=True)

    def update_frame():
        global cap
        if cap is None:
            cap = cv2.VideoCapture(1)
        ret, frame_val = cap.read()
        if ret:
            frame_val = cv2.resize(frame_val, (320, 240))
            cv2image = cv2.cvtColor(frame_val, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            face_label.imgtk = imgtk  # 保持引用
            face_label.configure(image=imgtk)
        face_label.after(10, update_frame)

    update_frame()
    return face_frame

def show_main_menu():
    """
    显示初始主菜单，包含三个选择按钮
    """
    clear_frame(main_frame)
    # 设置主frame的 grid 布局，并使唯一一列居中
    main_frame.grid_columnconfigure(0, weight=1)

    # 主菜单按钮采用 pack 布局也可，此处使用 grid 每个按钮占一行
    btn_student = tk.Button(main_frame, text="我是学生", command=show_student_ui, **button_style)
    btn_student.grid(row=0, column=0, pady=10)

    btn_visitor = tk.Button(main_frame, text="我是访客", command=show_visitor_ui, **button_style)
    btn_visitor.grid(row=1, column=0, pady=10)

    btn_admin = tk.Button(main_frame, text="我是管理员", command=show_admin_ui, **button_style)
    btn_admin.grid(row=2, column=0, pady=10)

def show_student_ui():
    """
    “我是学生”点击后显示学生界面：
      - 主界面居中显示人脸识别窗口
      - 下方显示“学生注册”和“学生登录”按钮，以及返回主菜单按钮
    """
    clear_frame(main_frame)
    main_frame.grid_columnconfigure(0, weight=1)

    # 行0：居中放置人脸识别窗口
    face = start_face_capture(main_frame)
    face.grid(row=0, column=0, pady=20)

    # 行1：按钮区
    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=10)
    btn_register = tk.Button(btn_frame, text="学生注册", command=on_student_register, **button_style)
    btn_register.grid(row=0, column=0, padx=20)
    btn_login = tk.Button(btn_frame, text="学生登录", command=on_student_login, **button_style)
    btn_login.grid(row=0, column=1, padx=20)

    # 行2：返回主菜单按钮
    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)

def show_visitor_ui():
    """
    “我是访客”点击后显示访客界面：
      - 主界面居中显示人脸识别窗口
      - 下方显示“访客注册”和“访客登录”按钮，以及返回主菜单按钮
    """
    clear_frame(main_frame)
    main_frame.grid_columnconfigure(0, weight=1)

    face = start_face_capture(main_frame)
    face.grid(row=0, column=0, pady=20)

    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=10)
    btn_register = tk.Button(btn_frame, text="访客注册", command=lambda: register_visitor(root), **button_style)
    btn_register.grid(row=0, column=0, padx=20)
    btn_login = tk.Button(btn_frame, text="访客登录", command=lambda: visitor_login(root), **button_style)
    btn_login.grid(row=0, column=1, padx=20)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)

def show_admin_ui():
    """
    “我是管理员”点击后显示管理员界面：
      - 主界面居中显示人脸识别窗口
      - 下方显示“管理员登录”按钮，以及返回主菜单按钮
    """
    clear_frame(main_frame)
    main_frame.grid_columnconfigure(0, weight=1)

    face = start_face_capture(main_frame)
    face.grid(row=0, column=0, pady=20)

    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=10)
    btn_admin_login = tk.Button(btn_frame, text="管理员登录", command=admin_login_handler, **button_style)
    btn_admin_login.grid(row=0, column=0, padx=20)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)

def admin_login_handler():
    """
    处理管理员登录，若登录成功则显示管理员操作界面
    """
    global admin_logged_in, is_initial_admin
    username, is_initial = admin_login()
    if username:
        admin_logged_in = True
        is_initial_admin = is_initial
        show_admin_buttons_ui()
    else:
        messagebox.showerror("错误", "管理员登录失败")

def show_admin_buttons_ui():
    """
    管理员登录成功后显示管理员操作界面：
      - 主界面居中显示人脸识别窗口
      - 下方排列“学生信息管理”、“访客信息管理”、“管理员注册”、“退出登录”（初始管理员额外显示“管理员信息管理”）按钮，
        以及返回主菜单按钮
    """
    clear_frame(main_frame)
    main_frame.grid_columnconfigure(0, weight=1)

    face = start_face_capture(main_frame)
    face.grid(row=0, column=0, pady=20)

    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=10)
    btn_manage_students = tk.Button(btn_frame, text="学生信息管理", command=on_manage_students, **button_style)
    btn_manage_students.grid(row=0, column=0, padx=10, pady=10)
    btn_manage_visitors = tk.Button(btn_frame, text="访客信息管理", command=on_manage_visitors, **button_style)
    btn_manage_visitors.grid(row=0, column=1, padx=10, pady=10)
    btn_admin_register = tk.Button(btn_frame, text="管理员注册", command=on_admin_register, **button_style)
    btn_admin_register.grid(row=0, column=2, padx=10, pady=10)
    btn_logout = tk.Button(btn_frame, text="退出登录", command=on_logout_handler, **button_style)
    btn_logout.grid(row=0, column=3, padx=10, pady=10)

    if is_initial_admin:
        btn_manage_admins = tk.Button(btn_frame, text="管理员信息管理", command=on_manage_admins, **button_style)
        btn_manage_admins.grid(row=0, column=4, padx=10, pady=10)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)

def on_logout_handler():
    """
    处理退出登录，并返回主界面
    """
    global admin_logged_in, is_initial_admin
    admin_logged_in = False
    is_initial_admin = False
    messagebox.showinfo("退出", "您已退出登录")
    show_main_menu()

def on_student_register():
    student_register()

def on_student_login():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(1)
    ret, frame_val = cap.read()
    if ret:
        user_id = recognize_face_from_frame(frame_val, "students")
        if user_id:
            messagebox.showinfo("登录成功", "学生登录成功")
        else:
            messagebox.showerror("登录失败", "未能识别学生")

def on_register_visitor():
    register_visitor(root)

def on_visitor_login():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(1)
    ret, frame_val = cap.read()
    if ret:
        user_id = recognize_face_from_frame(frame_val, "visitors")
        if user_id:
            messagebox.showinfo("登录成功", f"欢迎, {user_id}!")
        else:
            messagebox.showerror("登录失败", "未能识别访客")

def on_manage_students():
    manage_students(root)

def on_manage_visitors():
    manage_visitors(root)

def on_admin_register():
    admin_register()

def on_manage_admins():
    manage_admins(root)

# 主窗口设置，使用 grid 布局保证 main_frame 充满整个窗口
root = tk.Tk()
root.title("学校门禁系统")
root.geometry("800x600")
root.configure(bg='#2c3e50')
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

main_frame = tk.Frame(root, bg='#2c3e50')
main_frame.grid(row=0, column=0, sticky="nsew")

# 显示主菜单
show_main_menu()

root.mainloop()