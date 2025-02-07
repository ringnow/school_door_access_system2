import db
import gui

if __name__ == "__main__":
    db.init_db()  # 初始化数据库
    gui.root.mainloop()  # 启动图形用户界面