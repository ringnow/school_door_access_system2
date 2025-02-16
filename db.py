import sqlite3


def init_db():
    """
    初始化数据库，创建所需的表格。
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
        visit_time TEXT NOT NULL,
        approved BOOLEAN DEFAULT 0,
        face_data BLOB NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("数据库初始化完成。")