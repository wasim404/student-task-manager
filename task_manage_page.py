"""
task_manage_page.py
总任务管理页面模块

功能：
- 白色现代化 UI
- 圆角卡片布局
- 单击日期查看任务
- 双击日期快速添加任务
- 保存任务
- 查看任务
- 标记完成
- 删除任务
- 搜索任务
"""

import calendar
import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


# =========================
# 颜色配置
# =========================

BG_COLOR = "#F5F7FB"
CARD_COLOR = "#FFFFFF"
BORDER_COLOR = "#E5E7EB"
TEXT_COLOR = "#1F2937"
SUB_TEXT_COLOR = "#6B7280"

GREEN = "#22C55E"
GREEN_DARK = "#16A34A"
RED = "#EF4444"
RED_DARK = "#DC2626"
BLUE = "#3B82F6"
BLUE_DARK = "#2563EB"


# =========================
# 圆角矩形工具
# =========================

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

    return canvas.create_polygon(
        points,
        smooth=True,
        fill=fill,
        outline=outline
    )


class RoundButton(tk.Canvas):
    """
    圆角按钮。
    用 Canvas 实现，避免 ttk 按钮在不同主题下显示不统一。
    """

    def __init__(self, parent, text, command, bg_color=BLUE, hover_color=BLUE_DARK, width=120, height=38):
        # 按钮 Canvas 背景自动跟随父容器，避免出现灰色或白色方块底
        try:
            parent_bg = parent.cget("bg")
        except tk.TclError:
            parent_bg = BG_COLOR

        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent_bg,
            highlightthickness=0
        )

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.width = width
        self.height = height

        self.rect = draw_round_rect(
            self,
            2,
            2,
            width - 2,
            height - 2,
            14,
            fill=bg_color
        )

        self.text_id = self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill="white",
            font=("微软雅黑", 10, "bold")
        )

        self.bind("<Button-1>", lambda event: self.command())
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.itemconfig(self.rect, fill=self.hover_color)
        self.config(cursor="hand2")

    def on_leave(self, event):
        self.itemconfig(self.rect, fill=self.bg_color)


class TaskManagePage:
    """
    总任务管理页面。
    """

    def __init__(self, parent, username):
        self.parent = parent
        self.username = username
        self.today = datetime.now()
        self.current_year = self.today.year
        self.current_month = self.today.month
        self.selected_date = self.today.strftime("%Y-%m-%d")

        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
        self.create_task_table()

        self.frame = tk.Frame(self.parent, bg=BG_COLOR)
        self.frame.pack(fill=BOTH, expand=True)

        # 小窗口适配：用 Canvas 做可滚动页面，避免窗口变小时内容被底部导航栏遮住
        self.canvas = tk.Canvas(
            self.frame,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.v_scrollbar = ttk.Scrollbar(
            self.frame,
            orient=VERTICAL,
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.v_scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.update_canvas_width)
        self.bind_mousewheel()

        self.create_widgets()

    # 更新滚动区域
    def update_scroll_region(self, event=None):
        """
        当页面内容高度变化时，自动更新 Canvas 的滚动范围。
        """
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # 让内部页面宽度跟随窗口变化
    def update_canvas_width(self, event):
        """
        保证小窗口和全屏时内容宽度都能自适应。
        """
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    # 绑定鼠标滚轮
    def bind_mousewheel(self):
        """
        支持鼠标滚轮上下滚动页面。
        """
        self.canvas.bind_all(
            "<MouseWheel>",
            lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        )

    # 创建任务表
    def create_task_table(self):
        self.cursor.execute("""
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
        self.conn.commit()

    # 创建页面
    def create_widgets(self):
        container = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
        container.pack(fill=BOTH, expand=True, padx=28, pady=24)

        # 标题
        tk.Label(
            container,
            text="总任务管理",
            bg=BG_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 26, "bold")
        ).pack(anchor=W)

        tk.Label(
            container,
            text="单击日期查看当天相关任务，双击日期可以快速添加任务。",
            bg=BG_COLOR,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 11)
        ).pack(anchor=W, pady=(6, 18))

        # 顶部操作栏
        action_card = tk.Frame(container, bg=CARD_COLOR)
        action_card.pack(fill=X, pady=(0, 18))

        action_inner = tk.Frame(action_card, bg=CARD_COLOR)
        action_inner.pack(fill=X, padx=18, pady=14)

        RoundButton(
            action_inner,
            text="添加任务",
            command=lambda: self.open_add_task_window(self.selected_date),
            bg_color=GREEN,
            hover_color=GREEN_DARK,
            width=120
        ).pack(side=LEFT, padx=(0, 14))

        self.search_entry = ttk.Entry(action_inner, width=26)
        self.search_entry.pack(side=LEFT, padx=(8, 10))

        RoundButton(
            action_inner,
            text="搜索",
            command=self.search_tasks,
            bg_color=BLUE,
            hover_color=BLUE_DARK,
            width=90
        ).pack(side=LEFT, padx=(0, 10))

        RoundButton(
            action_inner,
            text="刷新",
            command=lambda: self.load_tasks_by_date(self.selected_date),
            bg_color="#64748B",
            hover_color="#475569",
            width=90
        ).pack(side=LEFT)

        # 日历卡片
        calendar_card = tk.Frame(container, bg=CARD_COLOR)
        calendar_card.pack(fill=X, pady=(0, 18))

        # 月份切换栏：用户可以选择任意年份和月份
        month_bar = tk.Frame(calendar_card, bg=CARD_COLOR)
        month_bar.pack(fill=X, padx=18, pady=(16, 8))

        self.calendar_title_label = tk.Label(
            month_bar,
            text=f"{self.current_year} 年 {self.current_month} 月任务日历",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 14, "bold")
        )
        self.calendar_title_label.pack(anchor=W)

        # 控制区单独换一行显示，避免小窗口时按钮被挤到右侧看不见
        control_area = tk.Frame(month_bar, bg=CARD_COLOR)
        control_area.pack(anchor="center", pady=(12, 0))

        RoundButton(
            control_area,
            text="上个月",
            command=self.prev_month,
            bg_color="#64748B",
            hover_color="#475569",
            width=82,
            height=34
        ).pack(side=LEFT, padx=(0, 8))

        self.year_box = ttk.Combobox(
            control_area,
            width=8,
            state="readonly",
            values=[str(year) for year in range(2000, 2101)]
        )
        self.year_box.set(str(self.current_year))
        self.year_box.pack(side=LEFT, padx=(0, 6))

        tk.Label(
            control_area,
            text="年",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(side=LEFT, padx=(0, 8))

        self.month_box = ttk.Combobox(
            control_area,
            width=5,
            state="readonly",
            values=[str(month) for month in range(1, 13)]
        )
        self.month_box.set(str(self.current_month))
        self.month_box.pack(side=LEFT, padx=(0, 6))

        tk.Label(
            control_area,
            text="月",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(side=LEFT, padx=(0, 8))

        RoundButton(
            control_area,
            text="跳转",
            command=self.jump_to_month,
            bg_color=BLUE,
            hover_color=BLUE_DARK,
            width=70,
            height=34
        ).pack(side=LEFT, padx=(0, 8))

        RoundButton(
            control_area,
            text="下个月",
            command=self.next_month,
            bg_color="#64748B",
            hover_color="#475569",
            width=82,
            height=34
        ).pack(side=LEFT)

        self.calendar_frame = tk.Frame(calendar_card, bg=CARD_COLOR)
        self.calendar_frame.pack(fill=X, padx=18, pady=(0, 18))

        self.create_calendar(self.calendar_frame)

        # 任务列表卡片
        self.task_list_box = tk.Frame(container, bg=CARD_COLOR)
        self.task_list_box.pack(fill=BOTH, expand=True)

        self.load_tasks_by_date(self.selected_date)

    # 创建日历
    def create_calendar(self, parent):
        days = ["一", "二", "三", "四", "五", "六", "日"]

        for col, day in enumerate(days):
            tk.Label(
                parent,
                text=day,
                bg=CARD_COLOR,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 11, "bold")
            ).grid(row=0, column=col, sticky=NSEW, padx=5, pady=6)

        month_matrix = calendar.monthcalendar(self.current_year, self.current_month)

        for row_index, week in enumerate(month_matrix, start=1):
            for col_index, day in enumerate(week):
                if day == 0:
                    tk.Label(parent, text="", bg=CARD_COLOR).grid(
                        row=row_index,
                        column=col_index,
                        sticky=NSEW,
                        padx=5,
                        pady=5
                    )
                    continue

                selected_date = f"{self.current_year}-{self.current_month:02d}-{day:02d}"

                if selected_date == self.selected_date:
                    bg = BLUE
                    fg = "white"
                elif (
                    self.current_year == self.today.year
                    and self.current_month == self.today.month
                    and day == self.today.day
                ):
                    bg = GREEN
                    fg = "white"
                else:
                    bg = "#EEF2F7"
                    fg = TEXT_COLOR

                btn = tk.Label(
                    parent,
                    text=str(day),
                    bg=bg,
                    fg=fg,
                    height=2,
                    font=("微软雅黑", 10, "bold"),
                    cursor="hand2"
                )
                btn.grid(row=row_index, column=col_index, sticky=NSEW, padx=5, pady=5)
                btn.bind("<Button-1>", lambda event, d=selected_date: self.on_day_click(d))
                btn.bind("<Double-Button-1>", lambda event, d=selected_date: self.on_day_double_click(d))

        for col in range(7):
            parent.columnconfigure(col, weight=1)

    # 跳转到指定年月
    def jump_to_month(self):
        """
        根据年份下拉框和月份下拉框刷新日历。
        """
        self.current_year = int(self.year_box.get())
        self.current_month = int(self.month_box.get())
        self.selected_date = f"{self.current_year}-{self.current_month:02d}-01"
        self.update_calendar_month()
        self.load_tasks_by_date(self.selected_date)

    # 切换到上个月
    def prev_month(self):
        """
        当前日历月份向前切换一个月。
        """
        if self.current_month == 1:
            self.current_year -= 1
            self.current_month = 12
        else:
            self.current_month -= 1

        self.selected_date = f"{self.current_year}-{self.current_month:02d}-01"
        self.update_calendar_month()
        self.load_tasks_by_date(self.selected_date)

    # 切换到下个月
    def next_month(self):
        """
        当前日历月份向后切换一个月。
        """
        if self.current_month == 12:
            self.current_year += 1
            self.current_month = 1
        else:
            self.current_month += 1

        self.selected_date = f"{self.current_year}-{self.current_month:02d}-01"
        self.update_calendar_month()
        self.load_tasks_by_date(self.selected_date)

    # 更新日历月份显示
    def update_calendar_month(self):
        """
        同步标题、下拉框和日历主体。
        """
        self.year_box.set(str(self.current_year))
        self.month_box.set(str(self.current_month))
        self.calendar_title_label.config(
            text=f"{self.current_year} 年 {self.current_month} 月任务日历"
        )
        self.refresh_calendar()

    # 日期单击：只查看当天相关任务
    def on_day_click(self, selected_date):
        """
        单击日期时只切换选中日期并查看任务，不弹出添加窗口。
        任务列表会显示：
        1. 任务日期等于当前日期的任务；
        2. 截止日期等于当前日期的任务。
        """
        self.selected_date = selected_date
        self.load_tasks_by_date(selected_date)

    # 日期双击：快速添加任务
    def on_day_double_click(self, selected_date):
        """
        双击日期时打开添加任务窗口。
        """
        self.selected_date = selected_date
        self.refresh_calendar()
        self.load_tasks_by_date(selected_date)
        self.open_add_task_window(selected_date)

    # 刷新日历颜色
    def refresh_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.create_calendar(self.calendar_frame)

    # 添加任务窗口
    def open_add_task_window(self, selected_date):
        """
        打开添加任务窗口。
        本版本重点修复：
        - 底部“保存任务”按钮固定显示；
        - 优先级只使用普通文字“高 / 中 / 低”；
        - 去掉表单里的大块白色卡片底，窗口整体保持干净白底；
        - 控件间距保持统一，避免窗口内容被挤压。
        """
        add_window = ttk.Toplevel(self.frame)
        add_window.title(f"添加任务 - {selected_date}")
        add_window.geometry("500x720")
        add_window.minsize(500, 720)
        add_window.resizable(False, False)
        add_window.configure(bg=CARD_COLOR)
        add_window.transient(self.frame.winfo_toplevel())
        add_window.grab_set()

        # =========================
        # 底部固定按钮区
        # 说明：先 pack 到 BOTTOM，再 pack 表单主体，确保按钮不会被表单挤掉。
        # =========================
        button_area = tk.Frame(add_window, bg=CARD_COLOR)
        button_area.pack(side=BOTTOM, fill=X, padx=34, pady=(12, 24))

        # =========================
        # 顶部标题区
        # =========================
        header = tk.Frame(add_window, bg=CARD_COLOR)
        header.pack(side=TOP, fill=X, padx=34, pady=(28, 20))

        tk.Label(
            header,
            text="新建学习任务",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 21, "bold")
        ).pack(anchor="center")

        tk.Label(
            header,
            text=selected_date,
            bg=CARD_COLOR,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(anchor="center", pady=(6, 0))

        # =========================
        # 表单主体区
        # =========================
        form_frame = tk.Frame(add_window, bg=CARD_COLOR)
        form_frame.pack(side=TOP, fill=BOTH, expand=True, padx=34, pady=(0, 6))

        def create_field_label(text):
            """
            创建统一样式的表单标签。
            """
            tk.Label(
                form_frame,
                text=text,
                bg=CARD_COLOR,
                fg=TEXT_COLOR,
                font=("微软雅黑", 10, "bold")
            ).pack(anchor=W)

        create_field_label("任务名称")
        title_entry = ttk.Entry(
            form_frame,
            bootstyle="primary"
        )
        title_entry.pack(fill=X, pady=(7, 17), ipady=6)
        title_entry.focus_set()

        create_field_label("优先级")
        priority_box = ttk.Combobox(
            form_frame,
            values=["高", "中", "低"],
            state="readonly",
            bootstyle="primary"
        )
        priority_box.set("中")
        priority_box.pack(fill=X, pady=(7, 17), ipady=4)

        create_field_label("分类")
        category_entry = ttk.Entry(
            form_frame,
            bootstyle="primary"
        )
        category_entry.insert(0, "课程学习")
        category_entry.pack(fill=X, pady=(7, 17), ipady=6)

        create_field_label("截止日期")
        deadline_entry = ttk.Entry(
            form_frame,
            bootstyle="primary"
        )
        deadline_entry.insert(0, selected_date)
        deadline_entry.pack(fill=X, pady=(7, 17), ipady=6)

        create_field_label("备注")
        note_text = tk.Text(
            form_frame,
            height=5,
            bg="#FAFAFA",
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BLUE,
            font=("微软雅黑", 10),
            padx=10,
            pady=8,
            wrap="word"
        )
        note_text.pack(fill=X, pady=(7, 0))

        # =========================
        # 保存任务逻辑
        # =========================
        def save_task():
            """
            读取表单数据并写入 SQLite 数据库。
            """
            title = title_entry.get().strip()
            priority = priority_box.get().strip()
            category = category_entry.get().strip()
            deadline = deadline_entry.get().strip()
            note = note_text.get("1.0", "end").strip()

            if not title:
                messagebox.showwarning("提示", "任务名称不能为空")
                return

            self.cursor.execute("""
            INSERT INTO tasks
            (username, title, task_date, deadline, priority, category, note, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.username,
                title,
                selected_date,
                deadline,
                priority,
                category,
                note,
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            self.conn.commit()
            messagebox.showinfo("成功", "任务添加成功")
            add_window.destroy()
            self.selected_date = selected_date
            self.refresh_calendar()
            self.load_tasks_by_date(selected_date)

        # Ctrl + Enter 快速保存
        add_window.bind("<Control-Return>", lambda event: save_task())

        RoundButton(
            button_area,
            text="保存任务",
            command=save_task,
            bg_color=GREEN,
            hover_color=GREEN_DARK,
            width=430,
            height=46
        ).pack(anchor="center")

    # 加载任务
    def load_tasks_by_date(self, selected_date):
        self.selected_date = selected_date

        for widget in self.task_list_box.winfo_children():
            widget.destroy()

        header = tk.Frame(self.task_list_box, bg=CARD_COLOR)
        header.pack(fill=X, padx=18, pady=(16, 8))

        tk.Label(
            header,
            text=f"{selected_date} 的任务",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 15, "bold")
        ).pack(side=LEFT)

        self.cursor.execute("""
        SELECT id, title, priority, deadline, category, note, status, task_date
        FROM tasks
        WHERE username=?
        AND (task_date=? OR deadline=?)
        ORDER BY status ASC, deadline ASC, id DESC
        """, (self.username, selected_date, selected_date))

        tasks = self.cursor.fetchall()

        list_area = tk.Frame(self.task_list_box, bg=CARD_COLOR)
        list_area.pack(fill=BOTH, expand=True, padx=18, pady=(0, 18))

        if not tasks:
            tk.Label(
                list_area,
                text="这一天还没有相关任务，双击日历日期即可添加。",
                bg=CARD_COLOR,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 11)
            ).pack(anchor=W, pady=12)
            return

        for task in tasks:
            self.create_task_card(list_area, task)

    # 任务卡片
    def create_task_card(self, parent, task):
        """
        创建单条任务卡片。
        兼容两种查询结果：
        - 普通日期查询：包含 task_date，用于显示任务日期与截止日期；
        - 搜索查询：不包含 task_date。
        """
        if len(task) == 8:
            task_id, title, priority, deadline, category, note, status, task_date = task
        else:
            task_id, title, priority, deadline, category, note, status = task
            task_date = None

        card_bg = "#F0FDF4" if status == 1 else "#F9FAFB"
        status_text = "已完成" if status == 1 else "未完成"
        status_color = GREEN if status == 1 else RED

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

        if task_date:
            info = f"任务日期：{task_date}    截止：{deadline}    优先级：{priority}    分类：{category}"
        else:
            info = f"优先级：{priority}    分类：{category}    截止：{deadline}"

        tk.Label(
            left,
            text=info,
            bg=card_bg,
            fg=SUB_TEXT_COLOR,
            font=("微软雅黑", 10)
        ).pack(anchor=W, pady=(5, 0))

        if note:
            tk.Label(
                left,
                text=f"备注：{note}",
                bg=card_bg,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 10)
            ).pack(anchor=W, pady=(5, 0))

        tk.Label(
            left,
            text=status_text,
            bg=card_bg,
            fg=status_color,
            font=("微软雅黑", 10, "bold")
        ).pack(anchor=W, pady=(5, 0))

        right = tk.Frame(card, bg=card_bg)
        right.pack(side=RIGHT, padx=14)

        if status == 0:
            RoundButton(
                right,
                text="完成",
                command=lambda: self.finish_task(task_id),
                bg_color=GREEN,
                hover_color=GREEN_DARK,
                width=78,
                height=34
            ).pack(side=LEFT, padx=5)

        RoundButton(
            right,
            text="删除",
            command=lambda: self.delete_task(task_id),
            bg_color=RED,
            hover_color=RED_DARK,
            width=78,
            height=34
        ).pack(side=LEFT, padx=5)

    # 完成任务
    def finish_task(self, task_id):
        self.cursor.execute(
            "UPDATE tasks SET status=1 WHERE id=? AND username=?",
            (task_id, self.username)
        )
        self.conn.commit()
        self.load_tasks_by_date(self.selected_date)

    # 删除任务
    def delete_task(self, task_id):
        if not messagebox.askyesno("确认删除", "确定要删除这个任务吗？"):
            return

        self.cursor.execute(
            "DELETE FROM tasks WHERE id=? AND username=?",
            (task_id, self.username)
        )
        self.conn.commit()
        self.load_tasks_by_date(self.selected_date)

    # 搜索任务
    def search_tasks(self):
        keyword = self.search_entry.get().strip()

        if not keyword:
            self.load_tasks_by_date(self.selected_date)
            return

        for widget in self.task_list_box.winfo_children():
            widget.destroy()

        header = tk.Frame(self.task_list_box, bg=CARD_COLOR)
        header.pack(fill=X, padx=18, pady=(16, 8))

        tk.Label(
            header,
            text=f"搜索结果：{keyword}",
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            font=("微软雅黑", 15, "bold")
        ).pack(anchor=W)

        list_area = tk.Frame(self.task_list_box, bg=CARD_COLOR)
        list_area.pack(fill=BOTH, expand=True, padx=18, pady=(0, 18))

        like_keyword = f"%{keyword}%"

        self.cursor.execute("""
        SELECT id, title, priority, deadline, category, note, status
        FROM tasks
        WHERE username=?
        AND (title LIKE ? OR category LIKE ? OR note LIKE ?)
        ORDER BY task_date DESC, status ASC, id DESC
        """, (
            self.username,
            like_keyword,
            like_keyword,
            like_keyword
        ))

        tasks = self.cursor.fetchall()

        if not tasks:
            tk.Label(
                list_area,
                text="没有找到相关任务。",
                bg=CARD_COLOR,
                fg=SUB_TEXT_COLOR,
                font=("微软雅黑", 11)
            ).pack(anchor=W, pady=12)
            return

        for task in tasks:
            self.create_task_card(list_area, task)