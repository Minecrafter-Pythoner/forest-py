#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主窗口UI实现
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time

# 确保能够正确导入项目中的其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.timer import FocusTimer, TimerState
from app.core.focus_monitor import FocusMonitor
from app.ui.tree_view import TreeView
from app.ui.settings_dialog import SettingsDialog
from app.ui.history_view import HistoryView
from app.utils.config import get_config
from app.utils.history import HistoryManager, SessionStatus

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
        
        # 获取配置
        self.config = get_config()
        
        # 初始化计时器
        self._initialize_timer()
        
        # 初始化焦点监控
        self.focus_monitor = FocusMonitor(
            self.master,
            on_focus_lost=self._on_focus_lost
        )
        
        # 会话开始时间
        self.session_start_time = None
        self.focus_lost_flag = None
        
        # 更新定时器显示
        self._update_timer_display(self.timer.remaining)
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self.master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 标题
        self.title_label = ttk.Label(
            self.toolbar, 
            text="Forest", 
            font=("Arial", 20, "bold")
        )
        self.title_label.pack(side=tk.LEFT, pady=(0, 10))
        
        # 历史记录按钮
        self.history_button = ttk.Button(
            self.toolbar,
            text="📊 History",
            command=self._open_history
        )
        self.history_button.pack(side=tk.RIGHT, pady=(5, 10), padx=(0, 10))
        
        # 设置按钮
        self.settings_button = ttk.Button(
            self.toolbar,
            text="⚙️ Settings",
            command=self._open_settings
        )
        self.settings_button.pack(side=tk.RIGHT, pady=(5, 10))
        
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
    
    def _initialize_timer(self):
        """初始化计时器"""
        duration = self.config.get("focus_duration", 25 * 60)  # 默认25分钟
        self.timer = FocusTimer(
            duration=duration,
            on_tick=self._update_timer_display,
            on_complete=self._on_timer_complete,
            on_fail=self._on_timer_fail
        )
    
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
    
    def _open_settings(self):
        """打开设置对话框"""
        # 如果定时器正在运行，不允许更改设置
        if self.timer.state == TimerState.RUNNING or self.timer.state == TimerState.PAUSED:
            messagebox.showwarning("Settings", "You can change settings when you are NOT in a focus session.")
            return
        
        # 打开设置对话框
        dialog = SettingsDialog(self.master)
        
        # 如果设置已更改，重新加载配置和初始化计时器
        if hasattr(dialog, 'result') and dialog.result:
            self.config = get_config()
            self._initialize_timer()
            self._update_timer_display(self.timer.remaining)
    
    def _open_history(self):
        """打开历史记录窗口"""
        HistoryView(self.master)
    
    def _on_start(self):
        """开始按钮点击处理"""
        if self.timer.state == TimerState.IDLE:
            # 记录会话开始时间
            self.session_start_time = time.time()
            
            # 开始新的专注会话
            self.timer.start()
            self.start_button.config(text="Pause", state=tk.NORMAL)
            self.give_up_button.config(state=tk.NORMAL)
            self.settings_button.config(state=tk.DISABLED)  # 禁用设置按钮
            self.history_button.config(state=tk.DISABLED)   # 禁用历史按钮
            
            # 开始焦点监控
            if self.config.get("strict_mode", False):
                self.focus_monitor.start_monitoring()
            
        elif self.timer.state == TimerState.RUNNING:
            # 暂停当前会话
            self.timer.pause()
            self.start_button.config(text="Resume")
            
            # 暂停焦点监控
            self.focus_monitor.stop_monitoring()
            
        elif self.timer.state == TimerState.PAUSED:
            # 继续当前会话
            self.timer.resume()
            self.start_button.config(text="Pause")
            
            # 恢复焦点监控
            if self.config.get("strict_mode", False):
                self.focus_monitor.start_monitoring()
    
    def _on_give_up(self):
        """放弃按钮点击处理"""
        if messagebox.askyesno("Confirm Give Up", "Are you sure you want to give up? Your tree will wither!"):
            # 记录会话
            if self.session_start_time is not None:
                end_time = time.time()
                actual_duration = int(end_time - self.session_start_time)
                
                # 添加到历史记录
                HistoryManager.add_session(
                    start_time=self.session_start_time,
                    end_time=end_time,
                    planned_duration=self.timer.duration,
                    actual_duration=actual_duration,
                    status=SessionStatus.FAILED,
                    notes="Ended by user"
                )
            
            self.timer.fail()
            self.tree_view.set_tree_dead()
            self._reset_ui()
    
    def _on_timer_complete(self):
        """计时器完成回调"""
        self.focus_monitor.stop_monitoring()
        
        # 记录成功完成的会话
        if self.session_start_time is not None:
            end_time = time.time()
            actual_duration = int(end_time - self.session_start_time)
            
            # 添加到历史记录
            HistoryManager.add_session(
                start_time=self.session_start_time,
                end_time=end_time,
                planned_duration=self.timer.duration,
                actual_duration=actual_duration,
                status=SessionStatus.COMPLETED,
                notes="Success"
            )
        
        messagebox.showinfo("Congratulations!", "Focus session ended. You planted a tree!")
        self._reset_ui()
    
    def _on_timer_fail(self):
        """计时器失败回调"""
        self.focus_monitor.stop_monitoring()
        
        # 如果是外部原因导致的失败，记录会话
        if self.session_start_time is not None and self.timer.state == TimerState.FAILED:
            end_time = time.time()
            actual_duration = int(end_time - self.session_start_time)
            
            # 添加到历史记录
            HistoryManager.add_session(
                start_time=self.session_start_time,
                end_time=end_time,
                planned_duration=self.timer.duration,
                actual_duration=actual_duration,
                status=SessionStatus.INTERRUPTED,
                notes="Session interrupted"
            )
        
        self._reset_ui()
    
    def _on_focus_lost(self):
        """窗口失去焦点回调"""
        if self.timer.state == TimerState.RUNNING and self.config.get("strict_mode", False) and not self.focus_lost_flag:
            self.focus_lost_flag = True
            messagebox.showwarning("Focus Session Interrupted", "You have left this window and failed!")
            self.timer.fail()
            self.tree_view.set_tree_dead()
            self._reset_ui()
            self.focus_lost_flag = None
    
    def _reset_ui(self):
        """重置UI到初始状态"""
        self.start_button.config(text="Plant", state=tk.NORMAL)
        self.give_up_button.config(state=tk.DISABLED)
        self.settings_button.config(state=tk.NORMAL)  # 恢复设置按钮
        self.history_button.config(state=tk.NORMAL)   # 恢复历史按钮
        self._update_timer_display(self.timer.duration)
        
        # 重置会话开始时间
        self.session_start_time = None
    
    def _on_close(self):
        """窗口关闭处理"""
        if self.timer.state == TimerState.RUNNING or self.timer.state == TimerState.PAUSED:
            if messagebox.askyesno("Confirm Exit", "The focus session is in progress. Are you sure you want to exit?"):
                # 如果正在进行中的会话被终止，记录为中断
                if self.session_start_time is not None:
                    end_time = time.time()
                    actual_duration = int(end_time - self.session_start_time)
                    
                    # 添加到历史记录
                    HistoryManager.add_session(
                        start_time=self.session_start_time,
                        end_time=end_time,
                        planned_duration=self.timer.duration,
                        actual_duration=actual_duration,
                        status=SessionStatus.INTERRUPTED,
                        notes="User exited the app and the session was interrupted"
                    )
                
                self.focus_monitor.stop_monitoring()
                self.master.destroy()
        else:
            self.master.destroy()