#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史记录查看窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta

# 确保能够正确导入项目中的其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.history import HistoryManager, SessionStatus, format_timestamp, format_duration

class HistoryView(tk.Toplevel):
    """历史记录查看窗口"""
    
    def __init__(self, parent):
        """
        初始化历史记录窗口
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.title("Focus History")
        self.transient(parent)
        self.detached_list = []
        
        # 窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(parent.winfo_x() + (parent.winfo_width() - window_width) / 2)
        center_y = int(parent.winfo_y() + (parent.winfo_height() - window_height) / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 允许调整大小
        self.minsize(600, 400)
        
        # 创建界面
        self._create_widgets()
        
        # 加载历史记录
        self._load_history()
        
        # 加载统计数据
        self._load_statistics()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 创建界面框架
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 历史记录选项卡
        self.history_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.history_tab, text="History")
        
        # 统计信息选项卡
        self.stats_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.stats_tab, text="Statistics")
        
        # 设置历史记录选项卡内容
        self._setup_history_tab()
        
        # 设置统计信息选项卡内容
        self._setup_stats_tab()
        
    def _setup_history_tab(self):
        """设置历史记录选项卡内容"""
        # 创建工具栏
        toolbar = ttk.Frame(self.history_tab)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 筛选选项
        ttk.Label(toolbar, text="View:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 筛选条件
        self.filter_var = tk.StringVar(value="all")
        filter_all = ttk.Radiobutton(toolbar, text="All", variable=self.filter_var, value="all", command=self._apply_filter)
        filter_all.pack(side=tk.LEFT, padx=5)
        
        filter_completed = ttk.Radiobutton(toolbar, text="Completed", variable=self.filter_var, value="completed", command=self._apply_filter)
        filter_completed.pack(side=tk.LEFT, padx=5)
        
        filter_failed = ttk.Radiobutton(toolbar, text="Failed", variable=self.filter_var, value="failed", command=self._apply_filter)
        filter_failed.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(toolbar, text="Refresh", command=self._load_history)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # 清空历史记录按钮
        clear_btn = ttk.Button(toolbar, text="Clear History", command=self._clear_history)
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # 创建表格
        columns = ("Date", "Start Time", "Duration", "Planned Duration", "Status")
        self.tree = ttk.Treeview(self.history_tab, columns=columns, show="headings")
        
        # 设置表头
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # 调整各列宽度
        self.tree.column("Date", width=120)
        self.tree.column("Start Time", width=120)
        self.tree.column("Duration", width=150)
        self.tree.column("Planned Duration", width=150)
        self.tree.column("Status", width=100)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(self.history_tab, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # 布局表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定双击事件，显示详细信息
        self.tree.bind("<Double-1>", self._show_session_details)
        
        # 绑定右键菜单
        self._setup_context_menu()
        
    def _setup_context_menu(self):
        """设置右键菜单"""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="View Details", command=self._show_selected_details)
        self.context_menu.add_command(label="Delete Records", command=self._delete_selected)
        
        # 绑定右键点击事件
        self.tree.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event):
        """显示右键菜单"""
        # 获取当前选中项
        item = self.tree.identify_row(event.y)
        if item:
            # 选中右键点击的项
            self.tree.selection_set(item)
            # 显示菜单
            self.context_menu.post(event.x_root, event.y_root)
        
    def _setup_stats_tab(self):
        """设置统计信息选项卡内容"""
        # 时间范围选择
        range_frame = ttk.Frame(self.stats_tab)
        range_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(range_frame, text="Time Range:").pack(side=tk.LEFT, padx=(0, 5))
        
        # 时间范围选择
        self.stats_range_var = tk.StringVar(value="30")
        
        range_7 = ttk.Radiobutton(range_frame, text="Last 7 days", variable=self.stats_range_var, value="7", command=self._load_statistics)
        range_7.pack(side=tk.LEFT, padx=5)
        
        range_30 = ttk.Radiobutton(range_frame, text="Last 30 days", variable=self.stats_range_var, value="30", command=self._load_statistics)
        range_30.pack(side=tk.LEFT, padx=5)
        
        range_90 = ttk.Radiobutton(range_frame, text="Last 90 days", variable=self.stats_range_var, value="90", command=self._load_statistics)
        range_90.pack(side=tk.LEFT, padx=5)
        
        range_all = ttk.Radiobutton(range_frame, text="All", variable=self.stats_range_var, value="0", command=self._load_statistics)
        range_all.pack(side=tk.LEFT, padx=5)
        
        # 统计信息展示区域
        self.stats_frame = ttk.LabelFrame(self.stats_tab, text="Statistics", padding=10)
        self.stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 总会话数
        self.total_sessions_var = tk.StringVar(value="All Sessions: 0")
        ttk.Label(self.stats_frame, textvariable=self.total_sessions_var, font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # 完成会话数
        self.completed_sessions_var = tk.StringVar(value="Completed: 0")
        ttk.Label(self.stats_frame, textvariable=self.completed_sessions_var, font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # 放弃会话数
        self.failed_sessions_var = tk.StringVar(value="Failed: 0")
        ttk.Label(self.stats_frame, textvariable=self.failed_sessions_var, font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # 被打断会话数
        self.interrupted_sessions_var = tk.StringVar(value="Interrupted: 0")
        ttk.Label(self.stats_frame, textvariable=self.interrupted_sessions_var, font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # 总专注时间
        self.total_focus_time_var = tk.StringVar(value="Total focus time: 0min")
        ttk.Label(self.stats_frame, textvariable=self.total_focus_time_var, font=("Arial", 12)).pack(anchor=tk.W, pady=5)
        
        # 完成率
        self.completion_rate_var = tk.StringVar(value="Completion rate: 0%")
        ttk.Label(self.stats_frame, textvariable=self.completion_rate_var, font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
    def _load_history(self):
        """加载历史记录数据"""
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 获取历史记录
        history = HistoryManager.get_history()
        
        # 按时间倒序排序
        history.sort(key=lambda x: x.get("start_time", 0), reverse=True)
        
        # 将记录添加到表格
        for session in history:
            # 获取数据
            start_time = session.get("start_time", 0)
            date_str = format_timestamp(start_time).split()[0]
            time_str = format_timestamp(start_time).split()[1]
            actual_duration = session.get("actual_duration", 0)
            planned_duration = session.get("planned_duration", 0)
            status = session.get("status", "")
            
            # 格式化持续时间
            actual_duration_str = format_duration(actual_duration)
            planned_duration_str = format_duration(planned_duration)
            
            # 格式化状态
            if status == SessionStatus.COMPLETED.value:
                status_str = "Completed ✓"
            elif status == SessionStatus.FAILED.value:
                status_str = "Failed ✗"
            elif status == SessionStatus.INTERRUPTED.value:
                status_str = "Interrupted !"
            else:
                status_str = status
            
            # 将数据添加到表格
            self.tree.insert("", tk.END, values=(date_str, time_str, actual_duration_str, planned_duration_str, status_str), tags=(status,))
            
            # 为不同状态设置不同颜色
            self.tree.tag_configure(SessionStatus.COMPLETED.value, foreground="green")
            self.tree.tag_configure(SessionStatus.FAILED.value, foreground="red")
            self.tree.tag_configure(SessionStatus.INTERRUPTED.value, foreground="orange")
        
        # 应用筛选
        self._apply_filter()
    
    def _apply_filter(self):
        """应用筛选条件"""
        # 获取筛选条件
        filter_value = self.filter_var.get()
        
        # 先显示所有记录
        for item in self.tree.get_children():
            self.tree.item(item, tags=self.tree.item(item, "tags"))
            self.tree.item(item, open=True)
            
        # 如果选择了筛选条件
        if filter_value != "all":
            for item in self.tree.get_children():
                status = self.tree.item(item, "values")[-1]
                
                # 根据状态筛选
                if filter_value == "completed" and "Completed" not in status:
                    self.tree.detach(item)  # 不删除，只是暂时不显示
                    self.detached_list.append(item)
                elif filter_value == "failed" and "Failed" not in status:
                    self.tree.detach(item)
                    self.detached_list.append(item)
        else:
            # 显示所有被隐藏的条目
            for item in self.detached_list:
                self.tree.reattach(item, "", 0)
                self.detached_list.remove(item)
    
    def _load_statistics(self):
        """加载统计信息"""
        # 获取时间范围
        days = int(self.stats_range_var.get())
        
        # 获取统计数据
        stats = HistoryManager.get_statistics(days)
        
        # 更新统计信息显示
        self.total_sessions_var.set(f"Total sessions: {stats['total_sessions']}")
        self.completed_sessions_var.set(f"Completed: {stats['completed_sessions']}")
        self.failed_sessions_var.set(f"Failed: {stats['failed_sessions']}")
        self.interrupted_sessions_var.set(f"Interrupted: {stats['interrupted_sessions']}")
        
        # 格式化总专注时间
        total_focus_time_str = format_duration(stats['total_focus_time'])
        self.total_focus_time_var.set(f"Total focus time: {total_focus_time_str}")
        
        # 格式化完成率，保留一位小数
        completion_rate = round(stats['completion_rate'], 1)
        self.completion_rate_var.set(f"Completion rate: {completion_rate}%")
    
    def _show_session_details(self, event):
        """显示会话详细信息"""
        # 获取选中的项
        selection = self.tree.selection()
        if not selection:
            return
            
        self._show_selected_details()
    
    def _show_selected_details(self):
        """显示选中会话的详细信息"""
        # 获取选中的项
        selection = self.tree.selection()
        if not selection:
            return
        
        # 获取选中项的值
        selected_item = selection[0]
        date_str = self.tree.item(selected_item, "values")[0]
        time_str = self.tree.item(selected_item, "values")[1]
        
        # 查找对应的会话记录
        history = HistoryManager.get_history()
        selected_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        selected_timestamp = selected_dt.timestamp()
        
        # 在历史记录中查找匹配的会话
        for session in history:
            start_time = session.get("start_time", 0)
            # 允许1秒的误差
            if abs(start_time - selected_timestamp) < 1:
                self._display_session_details(session)
                break
    
    def _display_session_details(self, session):
        """显示会话详细信息对话框"""
        details_window = tk.Toplevel(self)
        details_window.title("Session Details")
        details_window.transient(self)
        details_window.grab_set()
        
        # 设置窗口大小和位置
        window_width = 400
        window_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(self.winfo_x() + (self.winfo_width() - window_width) / 2)
        center_y = int(self.winfo_y() + (self.winfo_height() - window_height) / 2)
        details_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 创建内容框架
        content_frame = ttk.Frame(details_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 提取会话信息
        start_time = format_timestamp(session.get("start_time", 0))
        end_time = format_timestamp(session.get("end_time", 0))
        planned_duration = format_duration(session.get("planned_duration", 0))
        actual_duration = format_duration(session.get("actual_duration", 0))
        status = session.get("status", "")
        notes = session.get("notes", "")
        
        # 格式化状态
        if status == SessionStatus.COMPLETED.value:
            status_str = "Completed ✓"
        elif status == SessionStatus.FAILED.value:
            status_str = "Failed ✗"
        elif status == SessionStatus.INTERRUPTED.value:
            status_str = "Interrupted !"
        else:
            status_str = status
        
        # 显示详细信息
        ttk.Label(content_frame, text="Start Time:", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(content_frame, text=start_time, font=("Arial", 11)).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(content_frame, text="End Time:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(content_frame, text=end_time, font=("Arial", 11)).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(content_frame, text="Planned Duration:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(content_frame, text=planned_duration, font=("Arial", 11)).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(content_frame, text="Actual Duration:", font=("Arial", 11)).grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(content_frame, text=actual_duration, font=("Arial", 11)).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(content_frame, text="Status:", font=("Arial", 11)).grid(row=4, column=0, sticky=tk.W, pady=5)
        status_label = ttk.Label(content_frame, text=status_str, font=("Arial", 11))
        status_label.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # 根据状态设置标签颜色
        if status == SessionStatus.COMPLETED.value:
            status_label.configure(foreground="green")
        elif status == SessionStatus.FAILED.value:
            status_label.configure(foreground="red")
        elif status == SessionStatus.INTERRUPTED.value:
            status_label.configure(foreground="orange")
        
        # 添加备注信息
        ttk.Label(content_frame, text="Notes:", font=("Arial", 11)).grid(row=5, column=0, sticky=tk.NW, pady=5)
        
        notes_text = tk.Text(content_frame, wrap=tk.WORD, height=4, width=30)
        notes_text.grid(row=5, column=1, sticky=tk.W, pady=5)
        notes_text.insert(tk.END, notes)
        notes_text.configure(state="disabled")  # 禁止编辑
        
        # 关闭按钮
        close_button = ttk.Button(content_frame, text="关闭", command=details_window.destroy)
        close_button.grid(row=6, column=0, columnspan=2, pady=(20, 0))
        
    def _delete_selected(self):
        """删除选中的会话记录"""
        # 获取选中的项
        selection = self.tree.selection()
        if not selection:
            return
            
        # 确认是否删除
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected session(s)?"):
            return
        
        # 获取选中项的值
        selected_item = selection[0]
        date_str = self.tree.item(selected_item, "values")[0]
        time_str = self.tree.item(selected_item, "values")[1]
        
        # 查找对应的会话记录
        history = HistoryManager.get_history()
        selected_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        selected_timestamp = selected_dt.timestamp()
        
        # 在历史记录中查找匹配的会话
        for session in history:
            start_time = session.get("start_time", 0)
            # 允许1秒的误差
            if abs(start_time - selected_timestamp) < 1:
                # 删除会话
                HistoryManager.delete_session(session.get("id"))
                break
        
        # 重新加载历史记录
        self._load_history()
        
        # 重新加载统计数据
        self._load_statistics()
    
    def _clear_history(self):
        """清空历史记录"""
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all sessions? This action cannot be undone!"):
            HistoryManager.clear_history()
            self._load_history()
            self._load_statistics()  # 也更新统计数据