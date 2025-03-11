#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口UI实现
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# 确保能够正确导入项目中的其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.timer import FocusTimer, TimerState
from app.core.focus_monitor import FocusMonitor
from app.ui.tree_view import TreeView
from app.utils.config import get_config

class MainWindow:
    """应用程序主窗口"""
    
    def __init__(self, master):
        """
        初始化主窗口
        
        Args:
            master: tkinter主窗口
        """
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("TLabel", font=("Arial", 12))
        
        # 创建UI组件
        self._create_widgets()
        
        # 初始化计时器
        duration = get_config().get("focus_duration", 25 * 60)  # 默认25分钟
        self.timer = FocusTimer(
            duration=duration,
            on_tick=self._update_timer_display,
            on_complete=self._on_timer_complete,
            on_fail=self._on_timer_fail
        )
        
        # 初始化焦点监控
        self.focus_monitor = FocusMonitor(
            self.master,
            on_focus_lost=self._on_focus_lost
        )
        
        # 更新定时器显示
        self._update_timer_display(self.timer.remaining)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        self.title_label = ttk.Label(
            self.main_frame, 
            text="Forest", 
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(pady=(0, 20))
        
        # 树木视图
        self.tree_view = TreeView(self.main_frame)
        self.tree_view.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 计时器显示
        self.timer_frame = ttk.Frame(self.main_frame)
        self.timer_frame.pack(fill=tk.X, pady=10)
        
        self.timer_label = ttk.Label(
            self.timer_frame,
            text="25:00",
            font=("Arial", 36)
        )
        self.timer_label.pack()
        
        # 控制按钮框架
        self.controls_frame = ttk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, pady=20)
        
        # 开始按钮
        self.start_button = ttk.Button(
            self.controls_frame,
            text="Plant",
            command=self._on_start
        )
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # 放弃按钮
        self.give_up_button = ttk.Button(
            self.controls_frame,
            text="Give Up",
            command=self._on_give_up,
            state=tk.DISABLED
        )
        self.give_up_button.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
    
    def _update_timer_display(self, remaining_seconds):
        """更新计时器显示"""
        minutes = remaining_seconds // 60
        seconds = remaining_seconds % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # 根据剩余时间更新树木生长阶段
        progress = 1.0 - (remaining_seconds / self.timer.duration)
        self.tree_view.update_tree_growth(progress)
        
        # 确保在主线程中更新UI
        self.master.update_idletasks()
    
    def _on_start(self):
        """开始按钮点击处理"""
        if self.timer.state == TimerState.IDLE:
            # 开始新的专注会话
            self.timer.start()
            self.start_button.config(text="暂停", state=tk.NORMAL)
            self.give_up_button.config(state=tk.NORMAL)
            
            # 开始焦点监控
            self.focus_monitor.start_monitoring()
            
        elif self.timer.state == TimerState.RUNNING:
            # 暂停当前会话
            self.timer.pause()
            self.start_button.config(text="继续")
            
            # 暂停焦点监控
            self.focus_monitor.stop_monitoring()
            
        elif self.timer.state == TimerState.PAUSED:
            # 继续当前会话
            self.timer.resume()
            self.start_button.config(text="暂停")
            
            # 恢复焦点监控
            self.focus_monitor.start_monitoring()
    
    def _on_give_up(self):
        """放弃按钮点击处理"""
        if messagebox.askyesno("确认放弃", "确定要放弃当前的专注吗？您的树将会枯萎！"):
            self.timer.fail()
            self.tree_view.set_tree_dead()
            self._reset_ui()
    
    def _on_timer_complete(self):
        """计时器完成回调"""
        self.focus_monitor.stop_monitoring()
        messagebox.showinfo("恭喜", "专注完成！您的树已经成长完全！")
        self._reset_ui()
    
    def _on_timer_fail(self):
        """计时器失败回调"""
        self.focus_monitor.stop_monitoring()
        self._reset_ui()
    
    def _on_focus_lost(self):
        """窗口失去焦点回调"""
        if self.timer.state == TimerState.RUNNING:
            # 在这个MVP版本中，我们可以选择提醒用户或者什么都不做
            # 后续可以在这里实现更严格的控制，比如自动失败
            pass
    
    def _reset_ui(self):
        """重置UI到初始状态"""
        self.start_button.config(text="开始专注", state=tk.NORMAL)
        self.give_up_button.config(state=tk.DISABLED)
        self._update_timer_display(self.timer.duration)
    
    def _on_close(self):
        """窗口关闭处理"""
        if self.timer.state == TimerState.RUNNING:
            if messagebox.askyesno("确认退出", "专注尚未完成，确定要退出吗？"):
                self.focus_monitor.stop_monitoring()
                self.master.destroy()
        else:
            self.master.destroy()