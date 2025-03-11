#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
专注定时器实现
"""

import time
import threading
from enum import Enum

class TimerState(Enum):
    """定时器状态枚举"""
    IDLE = 0      # 空闲
    RUNNING = 1   # 运行中
    PAUSED = 2    # 暂停
    COMPLETED = 3 # 完成
    FAILED = 4    # 失败

class FocusTimer:
    """专注定时器类"""
    
    def __init__(self, duration=25*60, on_tick=None, on_complete=None, on_fail=None):
        """
        初始化定时器
        
        Args:
            duration: 专注时长（秒）
            on_tick: 每秒回调函数，参数为剩余秒数
            on_complete: 完成时的回调函数
            on_fail: 失败时的回调函数
        """
        self.duration = duration
        self.remaining = duration
        self.state = TimerState.IDLE
        self.on_tick = on_tick
        self.on_complete = on_complete
        self.on_fail = on_fail
        self.timer_thread = None
        self.stop_flag = threading.Event()
        
    def start(self):
        """开始计时"""
        if self.state == TimerState.IDLE or self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING
            self.stop_flag.clear()
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            
    def pause(self):
        """暂停计时"""
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED
            self.stop_flag.set()
    
    def resume(self):
        """恢复计时"""
        if self.state == TimerState.PAUSED:
            self.start()
    
    def stop(self):
        """停止计时"""
        self.state = TimerState.IDLE
        self.stop_flag.set()
        self.remaining = self.duration
    
    def fail(self):
        """标记为失败"""
        self.state = TimerState.FAILED
        self.stop_flag.set()
        if self.on_fail:
            self.on_fail()
    
    def _run_timer(self):
        """计时器运行线程"""
        while self.remaining > 0 and not self.stop_flag.is_set():
            if self.on_tick:
                self.on_tick(self.remaining)
            time.sleep(1)
            self.remaining -= 1
        
        if self.remaining <= 0 and not self.stop_flag.is_set():
            self.state = TimerState.COMPLETED
            if self.on_complete:
                self.on_complete()