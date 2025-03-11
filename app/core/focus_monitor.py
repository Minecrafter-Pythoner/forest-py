#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
窗口焦点监控模块
"""

import time
import threading
import tkinter as tk

class FocusMonitor:
    """
    监控应用程序是否保持焦点，
    如果用户切换到其他窗口，则触发失焦回调
    """
    
    def __init__(self, root, on_focus_lost=None, check_interval=1.0):
        """
        初始化焦点监控器
        
        Args:
            root: tkinter根窗口
            on_focus_lost: 失去焦点时的回调函数
            check_interval: 检查间隔时间（秒）
        """
        self.root = root
        self.on_focus_lost = on_focus_lost
        self.check_interval = check_interval
        self.monitoring = False
        self.monitor_thread = None
        self.stop_flag = threading.Event()
        
        # 记录最后一次焦点状态
        self.had_focus = True
        
        # 绑定焦点事件
        self.root.bind("<FocusIn>", self._on_focus_in)
        self.root.bind("<FocusOut>", self._on_focus_out)
    
    def start_monitoring(self):
        """开始监控窗口焦点"""
        if not self.monitoring:
            self.monitoring = True
            self.stop_flag.clear()
            self.monitor_thread = threading.Thread(target=self._monitor_focus)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止监控窗口焦点"""
        if self.monitoring:
            self.monitoring = False
            self.stop_flag.set()
    
    def _monitor_focus(self):
        """监控线程主函数"""
        while not self.stop_flag.is_set():
            # 检查窗口是否有焦点
            has_focus = self.root.focus_get() is not None
            
            # 如果之前有焦点，现在没有了，触发回调
            if self.had_focus and not has_focus:
                if self.on_focus_lost:
                    self.on_focus_lost()
            
            self.had_focus = has_focus
            time.sleep(self.check_interval)
    
    def _on_focus_in(self, event):
        """窗口获得焦点事件处理"""
        self.had_focus = True
    
    def _on_focus_out(self, event):
        """窗口失去焦点事件处理"""
        self.had_focus = False
        if self.monitoring and self.on_focus_lost:
            self.on_focus_lost()