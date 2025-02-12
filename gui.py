import tkinter as tk
from tkinter import messagebox, simpledialog
from student import student_register, student_login
from admin import admin_login, manage_students, manage_visitors, admin_register, manage_admins, initialize_admin
from visitor import register_visitor, visitor_login
from face_recognition import recognize_face_from_frame
import cv2
from PIL import Image, ImageTk
import locale

locale.setlocale(locale.LC_ALL, '')

# Initialize the database and initial administrator
initialize_admin()

# Global variables
cap = None
admin_logged_in = False
is_initial_admin = False

# Button style dictionary (applied to most buttons)
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
    """Remove all widgets from the given frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def start_face_capture(parent):
    """
    Create the face recognition window inside the parent and start updating the frame.
    Returns the frame that holds the face recognition window.
    """
    face_frame = tk.Frame(parent, width=320, height=240, bg='#34495e')
    face_frame.grid(row=0, column=0, columnspan=3, pady=20)
    face_frame.grid_propagate(False)
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
            face_label.imgtk = imgtk  # keep a reference
            face_label.configure(image=imgtk)
        face_label.after(10, update_frame)

    update_frame()

    return face_frame


def show_main_menu():
    """
    Show the initial main menu with the three selection buttons.
    """
    clear_frame(main_frame)
    # Create three buttons: "我是学生", "我是访客", "我是管理员"
    btn_student = tk.Button(main_frame, text="我是学生", command=show_student_ui, **button_style)
    btn_student.pack(pady=20)

    btn_visitor = tk.Button(main_frame, text="我是访客", command=show_visitor_ui, **button_style)
    btn_visitor.pack(pady=20)

    btn_admin = tk.Button(main_frame, text="我是管理员", command=show_admin_ui, **button_style)
    btn_admin.pack(pady=20)


def show_student_ui():
    """
    When "我是学生" is clicked, show the student UI:
    - Centered face recognition window
    - Two buttons: "学生注册" and "学生登录"
    - A back button to return to main menu.
    """
    clear_frame(main_frame)
    # Use grid layout
    face = start_face_capture(main_frame)
    # Place the buttons frame underneath
    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=20)

    btn_register = tk.Button(btn_frame, text="学生注册", command=on_student_register, **button_style)
    btn_register.grid(row=0, column=0, padx=20)

    btn_login = tk.Button(btn_frame, text="学生登录", command=on_student_login, **button_style)
    btn_login.grid(row=0, column=1, padx=20)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)


def show_visitor_ui():
    """
    When "我是访客" is clicked, show the visitor UI:
    - Centered face recognition window
    - Two buttons: "访客注册" and "访客登录"
    - A back button to return to main menu.
    """
    clear_frame(main_frame)
    face = start_face_capture(main_frame)
    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=20)

    btn_register = tk.Button(btn_frame, text="访客注册", command=on_register_visitor, **button_style)
    btn_register.grid(row=0, column=0, padx=20)

    btn_login = tk.Button(btn_frame, text="访客登录", command=on_visitor_login, **button_style)
    btn_login.grid(row=0, column=1, padx=20)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)


def show_admin_ui():
    """
    When "我是管理员" is clicked, show the admin UI:
    - Centered face recognition window
    - A button "管理员登录" to perform admin login
    - A back button to return to main menu.
    """
    clear_frame(main_frame)
    face = start_face_capture(main_frame)
    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=20)

    btn_admin_login = tk.Button(btn_frame, text="管理员登录", command=admin_login_handler, **button_style)
    btn_admin_login.grid(row=0, column=0, padx=20)

    back_btn = tk.Button(main_frame, text="返回主菜单", command=show_main_menu, **button_style)
    back_btn.grid(row=2, column=0, pady=20)


def admin_login_handler():
    """
    Handle administrator login. If successful, show the admin operation UI.
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
    After successful admin login, show the admin operations:
    - Centered face recognition window
    - Buttons: "学生信息管理", "访客信息管理", "管理员注册", "退出登录"
      If the logged in admin is an initial administrator, also show "管理员信息管理".
    - A back button to return to the main menu.
    """
    clear_frame(main_frame)
    face = start_face_capture(main_frame)
    btn_frame = tk.Frame(main_frame, bg='#2c3e50')
    btn_frame.grid(row=1, column=0, pady=20)

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
    Handle logout and return to the main menu.
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
    register_visitor()


def on_visitor_login():
    global cap
    if cap is None:
        cap = cv2.VideoCapture(1)
    ret, frame_val = cap.read()
    if ret:
        user_id = recognize_face_from_frame(frame_val, "visitors")
        if user_id:
            messagebox.showinfo("登录成功", "访客登录成功")
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


# Create main window and a main frame to hold UI content
root = tk.Tk()
root.title("学校门禁系统")
root.geometry("800x600")
root.configure(bg='#2c3e50')

main_frame = tk.Frame(root, bg='#2c3e50')
main_frame.pack(fill=tk.BOTH, expand=True)

# Start with the main menu
show_main_menu()

root.mainloop()