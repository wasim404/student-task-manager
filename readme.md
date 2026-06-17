# 📚 StudyFlow - 个人学习任务管理系统

> 基于 Python + Tkinter + SQLite 开发的桌面学习任务管理软件

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue" />
<img src="https://img.shields.io/badge/Tkinter-GUI-green" />
<img src="https://img.shields.io/badge/SQLite-Database-orange" />
<img src="https://img.shields.io/badge/License-MIT-red" />

</p>

---

## 项目简介

StudyFlow 是一个学习任务管理系统。

项目采用 Python 开发，结合 Tkinter 图形界面与 SQLite 数据库，实现任务的长期保存与管理，帮助用户规划学习安排，提高学习效率。

---

## 功能特性

### 用户管理

* 用户注册
* 用户登录
* 密码加密存储（SHA256）
* 退出登录

### 今日任务

* 查看今日待完成任务
* 查看任务优先级
* 快速了解当天学习安排

### 任务管理

* 添加任务
* 修改任务
* 删除任务
* 标记完成状态
* 设置截止日期
* 设置优先级
* 搜索任务

### 日历视图

* 月历展示
* 单击查看任务
* 双击快速添加任务
* 自定义年份与月份切换

### 数据统计

* 总任务数量统计
* 已完成任务统计
* 未完成任务统计
* 完成率统计
* 饼图可视化展示

### 个人中心

* 用户信息展示
* 账号创建时间展示
* 任务完成情况统计
* 数据可视化分析

---

## 项目结构

```text
StudyFlow/

├── main.py
│
├── profile_page.py
│
├── task_manage_page.py
│
├── today_tasks_page.py
│
├── database.db
│
├── README.md
│
└──
```

---

## 安装依赖

```bash
pip install ttkbootstrap
pip install matplotlib
pip install tkcalendar
```

---

## 运行项目

进入项目目录：

```bash
python main.py
```

启动后即可进入登录界面。

---

## 项目亮点

* 现代化 GUI 界面
* SQLite 本地持久化存储
* 日历任务管理
* 数据统计分析
* 饼图可视化
* 模块化开发结构
* 面向大学生学习场景设计

---


## 作者

姚万鑫（Wasim）

华中师范大学 · 信息安全专业

2026 Python课程期末项目

---

## License

本项目仅用于学习交流与课程实践，不用于商业用途。
