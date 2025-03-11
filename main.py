#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Forest - Say no to distractions
"""

import os
import sys
from app.ui.main_window import MainWindow

def main():
    """应用程序入口点"""
    import tkinter as tk
    
    # 创建主应用
    root = tk.Tk()
    root.title("专注森林")
    
    # 设置应用图标
    if os.path.exists("resources/icon.ico"):
        root.iconbitmap("resources/icon.ico")
    
    # 设置窗口大小和位置
    window_width = 400
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int((screen_width - window_width) / 2)
    center_y = int((screen_height - window_height) / 2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # 创建主窗口
    app = MainWindow(root)
    
    # 启动应用
    root.mainloop()

if __name__ == "__main__":
    main()