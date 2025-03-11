#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
设置对话框
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# 确保能够正确导入项目中的其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.utils.config import get_config, save_config

class SettingsDialog(tk.Toplevel):
    """设置对话框，允许用户修改应用设置"""
    
    def __init__(self, parent):
        """
        初始化设置对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        self.title("Settings")
        self.transient(parent)  # 设置为父窗口的临时窗口
        self.grab_set()  # 模态窗口
        
        # 窗口大小和位置
        window_width = 350
        window_height = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        center_x = int(parent.winfo_x() + (parent.winfo_width() - window_width) / 2)
        center_y = int(parent.winfo_y() + (parent.winfo_height() - window_height) / 2)
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # 设置不可调整大小
        self.resizable(False, False)
        
        # 加载当前配置
        self.config = get_config()
        
        # 创建界面
        self._create_widgets()
        
        # 初始化值
        self._set_initial_values()
        
        # 等待窗口关闭
        self.wait_window()
    
    def _create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 专注时间设置
        ttk.Label(self.main_frame, text="Focus Time (Minutes):", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # 创建专注时间选择框
        self.focus_duration_var = tk.IntVar()
        self.focus_duration_spinbox = ttk.Spinbox(
            self.main_frame,
            from_=1,
            to=120,  # 最长120分钟
            textvariable=self.focus_duration_var,
            width=5,
            font=("Arial", 12)
        )
        self.focus_duration_spinbox.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # 短休息时间设置
        ttk.Label(self.main_frame, text="Short Break Time (Minutes):", font=("Arial", 12)).grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        self.short_break_var = tk.IntVar()
        self.short_break_spinbox = ttk.Spinbox(
            self.main_frame,
            from_=1,
            to=30,  # 最长30分钟
            textvariable=self.short_break_var,
            width=5,
            font=("Arial", 12)
        )
        self.short_break_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # 严格模式设置
        self.strict_mode_var = tk.BooleanVar()
        self.strict_mode_check = ttk.Checkbutton(
            self.main_frame,
            text="Strict Mode (Fail on leaving window)",
            variable=self.strict_mode_var,
            onvalue=True,
            offvalue=False
        )
        self.strict_mode_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 20))
        
        # 按钮框架
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        # 保存按钮
        self.save_button = ttk.Button(
            self.button_frame,
            text="Save",
            command=self._save_settings
        )
        self.save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 取消按钮
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="Cancel",
            command=self.destroy
        )
        self.cancel_button.pack(side=tk.LEFT)
    
    def _set_initial_values(self):
        """设置控件的初始值"""
        # 设置专注时间 (从秒转为分钟)
        focus_duration_min = self.config.get("focus_duration", 25 * 60) // 60
        self.focus_duration_var.set(focus_duration_min)
        
        # 设置短休息时间 (从秒转为分钟)
        short_break_min = self.config.get("short_break", 5 * 60) // 60
        self.short_break_var.set(short_break_min)
        
        # 设置严格模式
        strict_mode = self.config.get("strict_mode", False)
        self.strict_mode_var.set(strict_mode)
    
    def _save_settings(self):
        """保存设置并关闭对话框"""
        # 获取专注时间 (从分钟转为秒)
        focus_duration_sec = self.focus_duration_var.get() * 60
        
        # 获取短休息时间 (从分钟转为秒)
        short_break_sec = self.short_break_var.get() * 60
        
        # 获取严格模式设置
        strict_mode = self.strict_mode_var.get()
        
        # 更新配置
        self.config["focus_duration"] = focus_duration_sec
        self.config["short_break"] = short_break_sec
        self.config["strict_mode"] = strict_mode
        
        # 保存配置
        save_config(self.config)
        
        # 设置结果标志，让父窗口知道设置已更改
        self.result = True
        
        # 关闭对话框
        self.destroy()