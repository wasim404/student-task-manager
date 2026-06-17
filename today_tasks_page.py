"""
today_tasks_page.py
今日任务页面模块

说明：
- 本文件专门负责“今日任务”页面的 UI 展示。
- 当前使用演示数据，后续可以改为从 SQLite 的 tasks 表读取今日未完成任务。
- 建议与 main.py 放在同一级目录。
"""

from datetime import datetime

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class TodayTasksPage:
    """
    今日任务页面。

    参数说明：
    - parent：页面显示到哪个父容器，一般传 main.py 的 content_frame。
    - username：当前登录用户名。
    """

    def __init__(self, parent, username):
        self.parent = parent
        self.username = username

        # 页面主容器
        self.frame = ttk.Frame(self.parent, padding=24)
        self.frame.pack(fill=BOTH, expand=True)

        # 构建页面内容
        self.create_widgets()

    def create_widgets(self):
        """
        创建今日任务页面组件。
        当前包括：标题、欢迎信息、日期、任务卡片列表。
        """
        # 页面标题区
        header_frame = ttk.Frame(self.frame)
        header_frame.pack(fill=X, pady=(0, 18))

        ttk.Label(
            header_frame,
            text="今日任务",
            font=("微软雅黑", 24, "bold"),
            bootstyle=PRIMARY
        ).pack(anchor=W)

        ttk.Label(
            header_frame,
            text=f"欢迎回来，{self.username}，下面是你今天需要关注的学习任务。",
            font=("微软雅黑", 10),
            bootstyle=SECONDARY
        ).pack(anchor=W, pady=(6, 0))

        # 今日概览卡片
        overview_frame = ttk.Labelframe(
            self.frame,
            text="今日概览",
            padding=18,
            bootstyle=INFO
        )
        overview_frame.pack(fill=X, pady=(0, 18))

        current_date = datetime.now().strftime("%Y-%m-%d")

        ttk.Label(
            overview_frame,
            text=f"日期：{current_date}",
            font=("微软雅黑", 12, "bold")
        ).pack(anchor=W)

        ttk.Label(
            overview_frame,
            text="未完成任务：3 个    高优先级：1 个    已完成：0 个",
            font=("微软雅黑", 11),
            bootstyle=SECONDARY
        ).pack(anchor=W, pady=(8, 0))

        # 任务列表区域
        list_frame = ttk.Labelframe(
            self.frame,
            text="待完成任务",
            padding=18,
            bootstyle=PRIMARY
        )
        list_frame.pack(fill=BOTH, expand=True)

        # 临时演示任务，后续替换为数据库读取
        demo_tasks = [
            {
                "title": "完成 Python 课程项目主页设计",
                "priority": "高",
                "deadline": "今天 22:00",
                "description": "优先保证主界面、导航栏和页面切换稳定。"
            },
            {
                "title": "复习 SQLite 数据库操作",
                "priority": "中",
                "deadline": "今天 20:00",
                "description": "重点看增删改查、表结构设计和参数化查询。"
            },
            {
                "title": "整理明天的学习计划",
                "priority": "低",
                "deadline": "今晚睡前",
                "description": "列出明天课程任务和项目开发任务。"
            }
        ]

        for task in demo_tasks:
            self.create_task_card(list_frame, task)

    def create_task_card(self, parent, task):
        """
        创建单个任务卡片。
        task 参数是一个字典，包含 title、priority、deadline、description。
        """
        card = ttk.Frame(parent, padding=14, bootstyle=SECONDARY)
        card.pack(fill=X, pady=8)

        top_frame = ttk.Frame(card)
        top_frame.pack(fill=X)

        ttk.Label(
            top_frame,
            text=task["title"],
            font=("微软雅黑", 13, "bold")
        ).pack(side=LEFT, anchor=W)

        ttk.Label(
            top_frame,
            text=f"优先级：{task['priority']}",
            font=("微软雅黑", 10),
            bootstyle=WARNING
        ).pack(side=RIGHT, anchor=E)

        ttk.Label(
            card,
            text=f"截止时间：{task['deadline']}",
            font=("微软雅黑", 10),
            bootstyle=SECONDARY
        ).pack(anchor=W, pady=(8, 0))

        ttk.Label(
            card,
            text=task["description"],
            font=("微软雅黑", 10),
            bootstyle=SECONDARY
        ).pack(anchor=W, pady=(4, 0))
