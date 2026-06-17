"""
profile_page.py
个人中心页面模块

功能说明：
1. 展示当前登录用户的账号信息；
2. 统计当前用户的总任务、已完成任务、未完成任务；
3. 使用 Matplotlib 饼图展示已完成与未完成任务占比；
4. 解决 Matplotlib 饼图中文乱码问题；
5. 页面内容支持上下滚动，小窗口和全屏都能完整查看；
6. 支持修改密码、刷新信息、退出登录；
7. 支持自动刷新：任务状态变化后，个人中心统计数字和饼图会自动更新。
"""

import hashlib
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import matplotlib
matplotlib.use("TkAgg")

from matplotlib import rcParams
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# =========================
# Matplotlib 中文字体配置
# =========================

rcParams["font.sans-serif"] = [
    "Microsoft YaHei",
    "SimHei",
    "SimSun",
    "KaiTi",
    "Arial Unicode MS"
]
rcParams["axes.unicode_minus"] = False


# =========================
# 密码加密函数
# =========================

def encrypt_password(password: str) -> str:
    """
    使用 SHA256 对用户密码进行加密。
    """
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class ProfilePage:
    """
    个人中心页面。
    """

    def __init__(self, parent, username, logout_callback=None, db_path="database.db"):
        """
        初始化个人中心页面。
        """
        self.parent = parent
        self.username = username
        self.logout_callback = logout_callback
        self.db_path = db_path

        # 页面颜色
        self.bg_color = "#ffffff"
        self.text_color = "#1f2d3d"
        self.sub_text_color = "#7f8c8d"
        self.success_color = "#22c55e"
        self.danger_color = "#ef4444"
        self.primary_color = "#2c3e50"

        # 自动刷新任务 ID
        self.auto_refresh_job = None

        # 当前登录时间
        self.login_time_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 饼图对象
        self.chart_canvas = None
        self.chart_figure = None
        self.chart_ax = None

        # 页面外层容器
        self.frame = tk.Frame(self.parent, bg=self.bg_color)
        self.frame.pack(fill=BOTH, expand=True)

        # 创建可滚动页面
        self.create_scrollable_area()

        # 查询用户信息并创建页面组件
        self.user_info = self.get_user_info()
        self.create_widgets()

        # 启动自动刷新
        self.start_auto_refresh()

    # =========================
    # 可滚动区域
    # =========================

    def create_scrollable_area(self):
        """
        创建可滚动内容区域。

        作用：
        1. 小窗口下可以上下滚动查看完整个人中心内容；
        2. 全屏时内容正常展开；
        3. 不影响 main.py 里的底部导航栏固定显示。
        """
        self.canvas = tk.Canvas(
            self.frame,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(
            self.frame,
            orient=VERTICAL,
            command=self.canvas.yview
        )
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.container = tk.Frame(self.canvas, bg=self.bg_color)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.container,
            anchor="nw"
        )

        self.container.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.update_canvas_width
        )

        self.canvas.bind(
            "<Enter>",
            self.bind_mousewheel
        )

        self.canvas.bind(
            "<Leave>",
            self.unbind_mousewheel
        )

    def update_scroll_region(self, event=None):
        """
        更新滚动区域大小。
        """
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def update_canvas_width(self, event):
        """
        让内部内容宽度跟随窗口宽度变化。
        """
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    def bind_mousewheel(self, event=None):
        """
        鼠标进入个人中心区域后启用滚轮。
        """
        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

    def unbind_mousewheel(self, event=None):
        """
        鼠标离开个人中心区域后取消滚轮绑定。
        """
        self.canvas.unbind_all("<MouseWheel>")

    def on_mousewheel(self, event):
        """
        鼠标滚轮滚动页面。
        """
        self.canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    # =========================
    # 数据库相关方法
    # =========================

    def get_connection(self):
        """
        获取数据库连接。
        """
        return sqlite3.connect(self.db_path)

    def get_user_info(self):
        """
        查询当前用户基本信息。
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE username=?",
            (self.username,)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                "id": user[0],
                "username": user[1],
                "created_at": user[2]
            }

        return {
            "id": "未知",
            "username": self.username,
            "created_at": "未知"
        }

    def get_task_statistics(self):
        """
        查询当前用户任务统计数据。

        兼容字段：
        1. 用户字段：username 或 user_id；
        2. 完成字段：status / is_completed / completed；
        3. status 值兼容：已完成、完成、completed、done、1、true。
        """
        default_data = {
            "total": 0,
            "completed": 0,
            "unfinished": 0
        }

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='tasks'
                """
            )

            if not cursor.fetchone():
                conn.close()
                return default_data

            cursor.execute("PRAGMA table_info(tasks)")
            columns = [item[1] for item in cursor.fetchall()]

            if "username" in columns:
                user_filter = "username=?"
                user_value = self.username
            elif "user_id" in columns and isinstance(self.user_info.get("id"), int):
                user_filter = "user_id=?"
                user_value = self.user_info["id"]
            else:
                conn.close()
                return default_data

            cursor.execute(
                f"SELECT COUNT(*) FROM tasks WHERE {user_filter}",
                (user_value,)
            )
            total = cursor.fetchone()[0]

            status_column = None

            for column in ["is_completed", "completed", "status"]:
                if column in columns:
                    status_column = column
                    break

            completed = 0

            if status_column in ["is_completed", "completed"]:
                cursor.execute(
                    f"""
                    SELECT COUNT(*) FROM tasks
                    WHERE {user_filter}
                    AND {status_column}=1
                    """,
                    (user_value,)
                )
                completed = cursor.fetchone()[0]

            elif status_column == "status":
                completed_status_values = (
                    "已完成",
                    "完成",
                    "completed",
                    "done",
                    "1",
                    "true",
                    "True"
                )

                placeholders = ",".join(["?"] * len(completed_status_values))

                cursor.execute(
                    f"""
                    SELECT COUNT(*) FROM tasks
                    WHERE {user_filter}
                    AND TRIM(status) IN ({placeholders})
                    """,
                    (user_value, *completed_status_values)
                )
                completed = cursor.fetchone()[0]

            conn.close()

            unfinished = total - completed

            if unfinished < 0:
                unfinished = 0

            return {
                "total": total,
                "completed": completed,
                "unfinished": unfinished
            }

        except sqlite3.Error:
            return default_data

    # =========================
    # 页面 UI 创建
    # =========================

    def create_widgets(self):
        """
        创建个人中心页面 UI。
        """
        stats = self.get_task_statistics()

        page_content = tk.Frame(
            self.container,
            bg=self.bg_color
        )
        page_content.pack(
            fill=BOTH,
            expand=True,
            padx=34,
            pady=28
        )

        # 顶部标题
        header_frame = tk.Frame(
            page_content,
            bg=self.bg_color
        )
        header_frame.pack(fill=X, pady=(0, 36))

        tk.Label(
            header_frame,
            text="个人中心",
            font=("微软雅黑", 26, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        ).pack(anchor=W)

        tk.Label(
            header_frame,
            text="管理账户信息、学习数据与系统设置",
            font=("微软雅黑", 10),
            fg=self.sub_text_color,
            bg=self.bg_color
        ).pack(anchor=W, pady=(8, 0))

        # 账号信息
        account_frame = tk.Frame(
            page_content,
            bg=self.bg_color
        )
        account_frame.pack(fill=X, pady=(0, 42))

        tk.Label(
            account_frame,
            text=str(self.user_info["username"]),
            font=("微软雅黑", 22, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        ).pack(anchor=W)

        self.created_time_label = tk.Label(
            account_frame,
            text=f"注册时间：{self.user_info['created_at']}",
            font=("微软雅黑", 11),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.created_time_label.pack(anchor=W, pady=(10, 0))

        self.current_login_label = tk.Label(
            account_frame,
            text=f"当前登录：{self.login_time_text}",
            font=("微软雅黑", 11),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.current_login_label.pack(anchor=W, pady=(8, 0))

        # 统计数字
        stats_frame = tk.Frame(
            page_content,
            bg=self.bg_color
        )
        stats_frame.pack(fill=X, pady=(0, 28))

        self.total_value_label = None
        self.completed_value_label = None
        self.unfinished_value_label = None

        total_card = self.create_stat_card(
            stats_frame,
            title="总任务",
            value=stats["total"],
            color=self.primary_color
        )
        total_card.pack(side=LEFT, fill=BOTH, expand=True)

        completed_card = self.create_stat_card(
            stats_frame,
            title="已完成",
            value=stats["completed"],
            color=self.success_color
        )
        completed_card.pack(side=LEFT, fill=BOTH, expand=True)

        unfinished_card = self.create_stat_card(
            stats_frame,
            title="未完成",
            value=stats["unfinished"],
            color=self.danger_color
        )
        unfinished_card.pack(side=LEFT, fill=BOTH, expand=True)

        # 饼图
        self.chart_frame = tk.Frame(
            page_content,
            bg=self.bg_color
        )
        self.chart_frame.pack(fill=X, pady=(0, 28))

        self.create_pie_chart(
            self.chart_frame,
            stats
        )

        # 操作按钮
        action_frame = tk.Frame(
            page_content,
            bg=self.bg_color
        )
        action_frame.pack(fill=X, pady=(0, 40))

        ttk.Button(
            action_frame,
            text="修改密码",
            bootstyle="primary-outline",
            width=16,
            command=self.open_change_password_window
        ).pack(side=LEFT, padx=(0, 18))

        ttk.Button(
            action_frame,
            text="刷新信息",
            bootstyle="info-outline",
            width=16,
            command=self.refresh_info
        ).pack(side=LEFT, padx=(0, 18))

        ttk.Button(
            action_frame,
            text="退出登录",
            bootstyle="danger-outline",
            width=16,
            command=self.logout
        ).pack(side=LEFT)

    def create_stat_card(self, parent, title, value, color):
        """
        创建统计数字展示区域。
        """
        card = tk.Frame(parent, bg=self.bg_color)

        value_label = tk.Label(
            card,
            text=str(value),
            font=("微软雅黑", 30, "bold"),
            fg=color,
            bg=self.bg_color
        )
        value_label.pack(anchor=CENTER)

        tk.Label(
            card,
            text=title,
            font=("微软雅黑", 10),
            fg=self.sub_text_color,
            bg=self.bg_color
        ).pack(anchor=CENTER, pady=(8, 0))

        if title == "总任务":
            self.total_value_label = value_label
        elif title == "已完成":
            self.completed_value_label = value_label
        elif title == "未完成":
            self.unfinished_value_label = value_label

        return card

    def create_pie_chart(self, parent, stats):
        """
        创建 Matplotlib 饼图。
        """
        chart_container = tk.Frame(
            parent,
            bg=self.bg_color
        )
        chart_container.pack(fill=X)

        tk.Label(
            chart_container,
            text="任务完成情况",
            font=("微软雅黑", 14, "bold"),
            fg=self.text_color,
            bg=self.bg_color
        ).pack(anchor=CENTER, pady=(0, 6))

        self.chart_figure = Figure(
            figsize=(5.2, 3.2),
            dpi=100
        )
        self.chart_figure.patch.set_facecolor(self.bg_color)

        self.chart_ax = self.chart_figure.add_subplot(111)

        self.chart_canvas = FigureCanvasTkAgg(
            self.chart_figure,
            master=chart_container
        )

        self.chart_canvas.get_tk_widget().pack(anchor=CENTER)

        self.update_pie_chart(stats)

    def update_pie_chart(self, stats):
        """
        更新 Matplotlib 饼图内容。
        """
        if not self.chart_ax or not self.chart_canvas:
            return

        completed = int(stats.get("completed", 0))
        unfinished = int(stats.get("unfinished", 0))
        total = int(stats.get("total", 0))

        self.chart_ax.clear()
        self.chart_ax.set_facecolor(self.bg_color)

        if total <= 0:
            self.chart_ax.text(
                0.5,
                0.5,
                "暂无任务数据",
                ha="center",
                va="center",
                fontsize=12,
                color=self.sub_text_color
            )
            self.chart_ax.axis("off")
            self.chart_canvas.draw_idle()
            return

        values = [completed, unfinished]
        labels = ["已完成", "未完成"]
        colors = [self.success_color, self.danger_color]

        def show_percent(percent):
            """
            只显示大于 0 的百分比。
            """
            if percent <= 0:
                return ""
            return f"{percent:.1f}%"

        self.chart_ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct=show_percent,
            startangle=90,
            counterclock=False,
            textprops={
                "fontsize": 10,
                "color": self.text_color,
                "fontfamily": "Microsoft YaHei"
            },
            wedgeprops={
                "linewidth": 1,
                "edgecolor": self.bg_color
            }
        )

        self.chart_ax.axis("equal")
        self.chart_figure.tight_layout()
        self.chart_canvas.draw_idle()

    # =========================
    # 刷新方法
    # =========================

    def refresh_info(self):
        """
        刷新个人中心统计数据和饼图。
        """
        self.user_info = self.get_user_info()
        stats = self.get_task_statistics()

        if self.created_time_label:
            self.created_time_label.config(
                text=f"注册时间：{self.user_info['created_at']}"
            )

        if self.total_value_label:
            self.total_value_label.config(
                text=str(stats["total"])
            )

        if self.completed_value_label:
            self.completed_value_label.config(
                text=str(stats["completed"])
            )

        if self.unfinished_value_label:
            self.unfinished_value_label.config(
                text=str(stats["unfinished"])
            )

        self.update_pie_chart(stats)
        self.update_scroll_region()

    def start_auto_refresh(self):
        """
        每 1 秒自动刷新统计数据。
        """
        if not self.frame.winfo_exists():
            return

        self.refresh_info()

        self.auto_refresh_job = self.frame.after(
            1000,
            self.start_auto_refresh
        )

    def stop_auto_refresh(self):
        """
        停止自动刷新。
        """
        if self.auto_refresh_job:
            try:
                self.frame.after_cancel(self.auto_refresh_job)
            except tk.TclError:
                pass

            self.auto_refresh_job = None

    # =========================
    # 修改密码
    # =========================

    def open_change_password_window(self):
        """
        打开修改密码窗口。
        """
        self.password_window = ttk.Toplevel(self.frame)
        self.password_window.title("修改密码")
        self.password_window.geometry("420x330")
        self.password_window.resizable(False, False)

        container = ttk.Frame(
            self.password_window,
            padding=24
        )
        container.pack(fill=BOTH, expand=True)

        ttk.Label(
            container,
            text="修改账户密码",
            font=("微软雅黑", 18, "bold"),
            bootstyle=PRIMARY
        ).pack(anchor=W, pady=(0, 18))

        ttk.Label(container, text="旧密码").pack(anchor=W, pady=(0, 4))

        self.old_password_entry = ttk.Entry(
            container,
            show="*"
        )
        self.old_password_entry.pack(fill=X, pady=(0, 12))

        ttk.Label(container, text="新密码").pack(anchor=W, pady=(0, 4))

        self.new_password_entry = ttk.Entry(
            container,
            show="*"
        )
        self.new_password_entry.pack(fill=X, pady=(0, 12))

        ttk.Label(container, text="确认新密码").pack(anchor=W, pady=(0, 4))

        self.confirm_password_entry = ttk.Entry(
            container,
            show="*"
        )
        self.confirm_password_entry.pack(fill=X, pady=(0, 18))

        ttk.Button(
            container,
            text="确认修改",
            bootstyle=SUCCESS,
            command=self.change_password
        ).pack(fill=X)

    def change_password(self):
        """
        修改当前用户密码。
        """
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not old_password or not new_password or not confirm_password:
            messagebox.showwarning("提示", "所有密码输入框都不能为空")
            return

        if len(new_password) < 6:
            messagebox.showwarning("提示", "新密码长度不能少于 6 位")
            return

        if new_password != confirm_password:
            messagebox.showerror("错误", "两次新密码输入不一致")
            return

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT password FROM users WHERE username=?",
            (self.username,)
        )

        result = cursor.fetchone()

        if not result:
            conn.close()
            messagebox.showerror("错误", "当前用户不存在")
            return

        if encrypt_password(old_password) != result[0]:
            conn.close()
            messagebox.showerror("错误", "旧密码错误")
            return

        cursor.execute(
            "UPDATE users SET password=? WHERE username=?",
            (encrypt_password(new_password), self.username)
        )

        conn.commit()
        conn.close()

        messagebox.showinfo(
            "成功",
            "密码修改成功，请牢记新密码"
        )

        self.password_window.destroy()

    # =========================
    # 页面销毁与退出
    # =========================

    def refresh_page(self):
        """
        兼容旧接口。
        """
        self.refresh_info()

    def destroy(self):
        """
        销毁个人中心页面。
        """
        self.stop_auto_refresh()
        self.unbind_mousewheel()

        if self.frame.winfo_exists():
            self.frame.destroy()

    def logout(self):
        """
        退出当前账号。
        """
        confirm = messagebox.askyesno(
            "退出登录",
            "确定要退出当前账号吗？"
        )

        if not confirm:
            return

        self.stop_auto_refresh()
        self.unbind_mousewheel()

        if self.frame.winfo_exists():
            self.frame.destroy()

        if self.logout_callback:
            self.logout_callback()