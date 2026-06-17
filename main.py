"""
main.py
学习任务管理系统主入口
"""

import hashlib
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from task_manage_page import TaskManagePage
from profile_page import ProfilePage


# =========================
# 全局样式配置
# =========================

BG_COLOR = "#F5F7FB"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"
SUB_TEXT_COLOR = "#6B7280"

BLUE = "#3B82F6"
BLUE_DARK = "#2563EB"
GREEN = "#22C55E"
GREEN_DARK = "#16A34A"
RED = "#EF4444"
ORANGE = "#F97316"
GRAY = "#64748B"

NAV_ACTIVE = "#FFFFFF"
NAV_NORMAL = "#FFFFFF"
NAV_ACTIVE_TEXT = "#2563EB"
NAV_NORMAL_TEXT = "#6B7280"

# =========================
# 数据库初始化
# =========================

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    title TEXT NOT NULL,
    task_date TEXT NOT NULL,
    deadline TEXT,
    priority TEXT,
    category TEXT,
    note TEXT,
    status INTEGER DEFAULT 0,
    created_at TEXT
)
""")

conn.commit()


# =========================
# 工具函数
# =========================

def encrypt_password(password):
    """
    使用 SHA256 加密密码。
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def draw_round_rect(canvas, x1, y1, x2, y2, radius, fill, outline=""):
    """
    在 Canvas 上绘制圆角矩形。
    """
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, fill=fill, outline=outline)


class RoundButton(tk.Canvas):
    """
    圆角按钮组件。
    """

    def __init__(
        self,
        parent,
        text,
        command,
        bg_color=BLUE,
        hover_color=BLUE_DARK,
        width=130,
        height=40,
        radius=14,
        font=("微软雅黑", 10, "bold")
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent["bg"],
            highlightthickness=0
        )

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color

        self.rect = draw_round_rect(
            self,
            2,
            2,
            width - 2,
            height - 2,
            radius,
            fill=bg_color
        )

        self.text_id = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill="white",
            font=font
        )

        self.bind("<Button-1>", lambda event: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor="hand2")

    def on_leave(self, event=None):
        self.itemconfig(self.rect, fill=self.bg_color)


# =========================
# 登录页面
# =========================

class LoginPage:
    """
    登录页面。
    """

    def __init__(self, root):
        self.root = root
        self.root.title("登录")
        self.root.geometry("980x640")
        self.root.minsize(760, 520)
        self.root.configure(bg=BG_COLOR)

        self.frame = tk.Frame(root, bg=BG_COLOR)
        self.frame.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        """
        创建登录页 UI。
        """
        outer = tk.Frame(self.frame, bg=BG_COLOR)
        outer.pack(fill=BOTH, expand=True)

        card = tk.Frame(outer, bg=CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor=CENTER, width=430, height=430)

        tk.Label(
            card,
            text="行知",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 24, "bold")
        ).pack(pady=(42, 8))

        tk.Label(
            card,
            text="知行合一，有始有终",
            bg=CARD_COLOR,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(pady=(0, 26))

        form = tk.Frame(card, bg=CARD_COLOR)
        form.pack(fill=X, padx=46)

        tk.Label(
            form,
            text="用户名",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 10, "bold")
        ).pack(anchor=W)

        self.username_entry = ttk.Entry(form)
        self.username_entry.pack(fill=X, pady=(6, 16))

        tk.Label(
            form,
            text="密码",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 10, "bold")
        ).pack(anchor=W)

        self.password_entry = ttk.Entry(form, show="*")
        self.password_entry.pack(fill=X, pady=(6, 22))

        RoundButton(
            form,
            text="登录",
            command=self.login,
            bg_color=GREEN,
            hover_color=GREEN_DARK,
            width=338,
            height=42
        ).pack(fill=X)

        register_label = tk.Label(
            card,
            text="创建新账户",
            fg=BLUE,
            bg=CARD_COLOR,
            cursor="hand2",
            font=("微软雅黑", 10, "underline")
        )
        register_label.pack(pady=(22, 0))
        register_label.bind("<Button-1>", self.open_register_page)

        self.root.bind("<Return>", lambda event: self.login())

    def login(self):
        """
        登录验证。
        """
        username = self.username_entry.get().strip()
        password = encrypt_password(self.password_entry.get())

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = cursor.fetchone()

        if user:
            self.root.unbind("<Return>")
            self.frame.destroy()
            HomePage(self.root, username)
        else:
            messagebox.showerror("错误", "用户名或密码错误")

    def open_register_page(self, event=None):
        """
        打开注册页。
        """
        self.root.unbind("<Return>")
        self.frame.destroy()
        RegisterPage(self.root)


# =========================
# 注册页面
# =========================

class RegisterPage:
    """
    注册页面。
    """

    def __init__(self, root):
        self.root = root
        self.root.title("行知 - 注册")
        self.root.geometry("980x640")
        self.root.minsize(760, 520)
        self.root.configure(bg=BG_COLOR)

        self.frame = tk.Frame(root, bg=BG_COLOR)
        self.frame.pack(fill=BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        """
        创建注册页 UI。
        """
        outer = tk.Frame(self.frame, bg=BG_COLOR)
        outer.pack(fill=BOTH, expand=True)

        card = tk.Frame(outer, bg=CARD_COLOR)
        card.place(relx=0.5, rely=0.5, anchor=CENTER, width=430, height=480)

        tk.Label(
            card,
            text="创建新账户",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 23, "bold")
        ).pack(pady=(38, 8))

        tk.Label(
            card,
            text="创建账户后即可长期保存学习任务",
            bg=CARD_COLOR,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(pady=(0, 24))

        form = tk.Frame(card, bg=CARD_COLOR)
        form.pack(fill=X, padx=46)

        tk.Label(form, text="用户名", bg=CARD_COLOR, fg=TEXT_COLOR, font=("微软雅黑", 10, "bold")).pack(anchor=W)
        self.username_entry = ttk.Entry(form)
        self.username_entry.pack(fill=X, pady=(6, 14))

        tk.Label(form, text="密码", bg=CARD_COLOR, fg=TEXT_COLOR, font=("微软雅黑", 10, "bold")).pack(anchor=W)
        self.password_entry = ttk.Entry(form, show="*")
        self.password_entry.pack(fill=X, pady=(6, 14))

        tk.Label(form, text="确认密码", bg=CARD_COLOR, fg=TEXT_COLOR, font=("微软雅黑", 10, "bold")).pack(anchor=W)
        self.confirm_password_entry = ttk.Entry(form, show="*")
        self.confirm_password_entry.pack(fill=X, pady=(6, 22))

        RoundButton(
            form,
            text="注册",
            command=self.register,
            bg_color=BLUE,
            hover_color=BLUE_DARK,
            width=338,
            height=42
        ).pack(fill=X)

        back_label = tk.Label(
            card,
            text="返回登录",
            fg=BLUE,
            bg=CARD_COLOR,
            cursor="hand2",
            font=("微软雅黑", 10, "underline")
        )
        back_label.pack(pady=(20, 0))
        back_label.bind("<Button-1>", self.back_to_login)

        self.root.bind("<Return>", lambda event: self.register())

    def register(self):
        """
        注册账号。
        """
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username or not password:
            messagebox.showwarning("警告", "用户名和密码不能为空")
            return

        if password != confirm_password:
            messagebox.showerror("错误", "两次密码输入不一致")
            return

        try:
            cursor.execute(
                """
                INSERT INTO users (username, password, created_at)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    encrypt_password(password),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
            )
            conn.commit()

            messagebox.showinfo("成功", "账户创建成功！")
            self.root.unbind("<Return>")
            self.frame.destroy()
            LoginPage(self.root)

        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "用户名已存在")

    def back_to_login(self, event=None):
        """
        返回登录页。
        """
        self.root.unbind("<Return>")
        self.frame.destroy()
        LoginPage(self.root)


# =========================
# 主页面
# =========================

class HomePage:
    """
    登录后的主页。
    """

    def __init__(self, root, username):
        self.root = root
        self.username = username

        self.root.title("行知 - 主页")
        self.root.geometry("1200x760")
        self.root.minsize(900, 620)
        self.root.resizable(True, True)
        self.root.configure(bg=BG_COLOR)

        self.frame = tk.Frame(root, bg=BG_COLOR)
        self.frame.pack(fill=BOTH, expand=True)

        self.content_frame = tk.Frame(self.frame, bg=BG_COLOR)
        self.content_frame.pack(fill=BOTH, expand=True)

        self.nav_frame = tk.Frame(    self.frame,bg="#FFFFFF",height=60)
        self.nav_frame.pack(    fill=X,side=BOTTOM,padx=0,pady=0)

        self.nav_buttons = {}

        self.create_nav_button("today", "今日任务", self.show_today_tasks).pack(
            side=LEFT, fill=X, expand=True, padx=5
        )
        self.create_nav_button("manage", "总任务管理", self.show_task_manage).pack(
            side=LEFT, fill=X, expand=True, padx=5
        )
        self.create_nav_button("profile", "个人中心", self.show_profile).pack(
            side=LEFT, fill=X, expand=True, padx=5
        )

        self.show_today_tasks()

    def create_nav_button(self, key, text, command):
        """
        创建底部导航按钮。
        """
        btn = tk.Label(
            self.nav_frame,
            text=text,
            bg=NAV_NORMAL,
            fg=NAV_NORMAL_TEXT,
            font=("微软雅黑", 10),
            height=2,
            cursor="hand2",
            relief="flat"
        )
        btn.bind("<Button-1>", lambda event: command())
        self.nav_buttons[key] = btn
        return btn

    def clear_content(self):
        """
        清空内容区域。
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, active_key):
        for key, button in self.nav_buttons.items():
            if key == active_key:
                button.configure(
                    bg="#FFFFFF",
                    fg="#2563EB",
                    font=("微软雅黑", 10, "bold")
                )
            else:
                button.configure(
                    bg="#FFFFFF",
                    fg="#6B7280",
                    font=("微软雅黑", 10)
                )

    def show_today_tasks(self):
        """
        今日任务页面。
        """
        self.clear_content()
        self.set_active_button("today")

        page = tk.Frame(self.content_frame, bg=BG_COLOR)
        page.pack(fill=BOTH, expand=True, padx=34, pady=28)

        # 页面标题区
        header = tk.Frame(page, bg=BG_COLOR)
        header.pack(fill=X)

        tk.Label(
            header,
            text="今日任务",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 26, "bold")
        ).pack(anchor=W)

        # 大日期显示区
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")

        date_card = tk.Frame(
            header,
            bg=CARD_COLOR,
            height=128
        )
        date_card.pack(fill=X, pady=(8, 0))
        date_card.pack_propagate(False)

        # 日期 + 时钟容器
        datetime_frame = tk.Frame(
            date_card,
            bg=CARD_COLOR
        )
        datetime_frame.pack(expand=True)
        
        # 日期
        date_label = tk.Label(
            datetime_frame,
            text=now.strftime("%Y - %m - %d"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 34, "bold")
        )
        date_label.pack(side=tk.LEFT)
        
        # 时钟
        clock_label = tk.Label(
            datetime_frame,
            bg=CARD_COLOR,
            fg="#64748B",
            font=("Consolas", 24, "bold")
        )
        clock_label.pack(side=tk.LEFT, padx=(25, 0))


        def update_clock():
            clock_label.config(
                text=datetime.now().strftime("%H:%M:%S")
            )
            clock_label.after(1000, update_clock)


        update_clock()

        date_label.pack(expand=True)

        # 查询今日任务
        self.cursor_today_tasks(current_date)

        total_count = len(self.today_tasks)
        undone_count = len([task for task in self.today_tasks if task[-1] == 0])
        done_count = total_count - undone_count

        # 统计卡片
        stat_area = tk.Frame(page, bg=BG_COLOR)
        stat_area.pack(fill=X, pady=(0, 12))

        self.create_stat_card(stat_area, "今日相关", total_count, BLUE).pack(
            side=LEFT, fill=X, expand=True, padx=(0, 10)
        )
        self.create_stat_card(stat_area, "未完成", undone_count, RED).pack(
            side=LEFT, fill=X, expand=True, padx=10
        )
        self.create_stat_card(stat_area, "已完成", done_count, GREEN).pack(
            side=LEFT, fill=X, expand=True, padx=(10, 0)
        )

        # 任务列表区
        list_card = tk.Frame(page, bg=CARD_COLOR)
        list_card.pack(fill=BOTH, expand=True, pady=(10, 0))

        tk.Label(
            list_card,
            text="今日任务列表",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 15, "bold")
        ).pack(anchor=W, padx=18, pady=(18, 6))

        list_area = tk.Frame(list_card, bg=CARD_COLOR)
        list_area.pack(fill=BOTH, expand=True, padx=18, pady=(0, 18))

        if not self.today_tasks:
            tk.Label(
                list_area,
                text="今天暂时没有相关任务。",
                bg=CARD_COLOR,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 12)
            ).pack(anchor=W, pady=18)
            return

        for task in self.today_tasks:
            self.create_today_task_card(list_area, task)

    def create_big_date_item(self, parent, number, unit, color):
        """
        创建大日期三栏中的单个日期块。
        """
        item = tk.Frame(parent, bg=CARD_COLOR)

        tk.Label(
            item,
            text=number,
            bg=CARD_COLOR,
            fg=color,
            font=("微软雅黑", 34, "bold")
        ).pack(pady=(24, 0))

        return item

    def cursor_today_tasks(self, current_date):
        """
        查询今日相关任务。
        """
        cursor.execute("""
        SELECT id, title, task_date, deadline, priority, category, note, status
        FROM tasks
        WHERE username=?
        AND (task_date=? OR deadline=?)
        ORDER BY status ASC, priority ASC, id DESC
        """, (self.username, current_date, current_date))

        self.today_tasks = cursor.fetchall()

    def create_stat_card(self, parent, title, value, color):
        """
        创建统计卡片。
        数字居中显示，使其与上方年月日三栏保持对齐。
        """
        card = tk.Frame(parent, bg=CARD_COLOR, height=86)
        card.pack_propagate(False)

        tk.Label(
            card,
            text=str(value),
            bg=CARD_COLOR,
            fg=color,
            font=("微软雅黑", 22, "bold")
        ).pack(pady=(12, 0))

        tk.Label(
            card,
            text=title,
            bg=CARD_COLOR,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(pady=(2, 0))

        return card

    def create_today_task_card(self, parent, task):
        """
        创建今日任务卡片。
        """
        task_id, title, task_date, deadline, priority, category, note, status = task

        card_bg = "#F0FDF4" if status == 1 else "#F9FAFB"
        status_text = "已完成" if status == 1 else "未完成"
        status_color = GREEN if status == 1 else RED

        priority_color = {
            "高": RED,
            "中": ORANGE,
            "低": GREEN
        }.get(priority, GRAY)

        card = tk.Frame(parent, bg=card_bg)
        card.pack(fill=X, pady=8)

        left = tk.Frame(card, bg=card_bg)
        left.pack(side=LEFT, fill=BOTH, expand=True, padx=16, pady=12)

        tk.Label(
            left,
            text=title,
            bg=card_bg,
            fg=TEXT_COLOR,
            font=("微软雅黑", 13, "bold")
        ).pack(anchor=W)

        info = f"任务日期：{task_date}    截止：{deadline}    分类：{category}"

        tk.Label(
            left,
            text=info,
            bg=card_bg,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(anchor=W, pady=(6, 0))

        if note:
            tk.Label(
                left,
                text=f"备注：{note}",
                bg=card_bg,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 10)
            ).pack(anchor=W, pady=(5, 0))

        bottom = tk.Frame(left, bg=card_bg)
        bottom.pack(anchor=W, pady=(6, 0))

        tk.Label(
            bottom,
            text=f"优先级：{priority}",
            bg=card_bg,
            fg=priority_color,
            font=("微软雅黑", 10, "bold")
        ).pack(side=LEFT, padx=(0, 16))

        tk.Label(
            bottom,
            text=status_text,
            bg=card_bg,
            fg=status_color,
            font=("微软雅黑", 10, "bold")
        ).pack(side=LEFT)

        right = tk.Frame(card, bg=card_bg)
        right.pack(side=RIGHT, padx=14)

        if status == 0:
            RoundButton(
                right,
                text="完成",
                command=lambda: self.finish_today_task(task_id),
                bg_color=GREEN,
                hover_color=GREEN_DARK,
                width=76,
                height=34
            ).pack(side=LEFT, padx=5)

    def finish_today_task(self, task_id):
        """
        标记今日任务为完成。
        """
        cursor.execute(
            "UPDATE tasks SET status=1 WHERE id=? AND username=?",
            (task_id, self.username)
        )
        conn.commit()
        self.show_today_tasks()

    def show_task_manage(self):
        """
        总任务管理页面。
        """
        self.clear_content()
        self.set_active_button("manage")

        TaskManagePage(
            parent=self.content_frame,
            username=self.username
        )

    def show_profile(self):
        """
        个人中心页面。
        """
        self.clear_content()
        self.set_active_button("profile")

        ProfilePage(
            parent=self.content_frame,
            username=self.username,
            logout_callback=self.logout
        )

    def logout(self):
        """
        退出登录。
        """
        self.frame.destroy()
        LoginPage(self.root)


# =========================
# 主程序入口
# =========================

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    LoginPage(root)
    root.mainloop()