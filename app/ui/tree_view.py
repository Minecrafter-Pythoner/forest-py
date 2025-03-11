#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
树木生长视图
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class TreeView(ttk.Frame):
    """树木生长视图组件"""
    
    def __init__(self, master):
        """
        初始化树木视图
        
        Args:
            master: 父窗口
        """
        super().__init__(master)
        
        # 创建画布用于显示树木图像
        self.canvas = tk.Canvas(self, width=300, height=300, bg="#F0F0F0")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 加载树木图像
        self.tree_images = self._load_tree_images()
        
        # 当前图像引用（防止垃圾回收）
        self.current_image = None
        
        # 显示初始树木
        self.update_tree_growth(0)
    
    def _load_tree_images(self):
        """加载不同生长阶段的树木图像"""
        images = []
        resources_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "resources", "trees"
        )
        
        # 如果资源目录不存在，创建它
        if not os.path.exists(resources_path):
            os.makedirs(resources_path)
            print(f"警告: 树木图像目录不存在，已创建 {resources_path}")
            print("请将树木图像放入该目录")
            
            # 创建示例空图像
            for i in range(1, 5):
                blank_image = Image.new('RGB', (300, 300), color='white')
                images.append(ImageTk.PhotoImage(blank_image))
                
            # 添加枯萎树的图像
            dead_image = Image.new('RGB', (300, 300), color='#CCCCCC')
            images.append(ImageTk.PhotoImage(dead_image))
            return images
        
        try:
            # 加载四个生长阶段的图像
            for i in range(1, 5):
                path = os.path.join(resources_path, f"stage{i}.png")
                if os.path.exists(path):
                    image = Image.open(path)
                    # 调整图像大小以适应画布
                    image = image.resize((300, 300), Image.LANCZOS)
                    images.append(ImageTk.PhotoImage(image))
                else:
                    # 如果图像不存在，使用空白图像
                    blank_image = Image.new('RGB', (300, 300), color='white')
                    images.append(ImageTk.PhotoImage(blank_image))
                    print(f"警告: 树木图像 stage{i}.png 不存在")
            
            # 加载枯萎的树图像
            dead_path = os.path.join(resources_path, "dead.png")
            if os.path.exists(dead_path):
                dead_image = Image.open(dead_path)
                dead_image = dead_image.resize((300, 300), Image.LANCZOS)
                images.append(ImageTk.PhotoImage(dead_image))
            else:
                blank_image = Image.new('RGB', (300, 300), color='#CCCCCC')
                images.append(ImageTk.PhotoImage(blank_image))
                print("警告: 枯萎树木图像 dead.png 不存在")
                
        except Exception as e:
            print(f"加载树木图像时出错: {e}")
            # 创建备用图像
            for i in range(5):
                blank_image = Image.new('RGB', (300, 300), color='white')
                images.append(ImageTk.PhotoImage(blank_image))
        
        return images
    
    def update_tree_growth(self, progress):
        """
        根据进度更新树木生长阶段
        
        Args:
            progress: 专注进度，0.0-1.0
        """
        if not self.tree_images:
            return
            
        # 根据进度选择对应的树木图像
        if progress < 0.25:
            image_index = 0  # 第一阶段
        elif progress < 0.5:
            image_index = 1  # 第二阶段
        elif progress < 0.75:
            image_index = 2  # 第三阶段
        else:
            image_index = 3  # 第四阶段
        
        self._display_tree(image_index)
    
    def set_tree_dead(self):
        """设置树木为枯萎状态"""
        if len(self.tree_images) >= 5:
            self._display_tree(4)  # 索引4是枯萎的树
    
    def _display_tree(self, image_index):
        """
        在画布上显示指定索引的树木图像
        
        Args:
            image_index: 图像索引
        """
        # 清除画布
        self.canvas.delete("all")
        
        # 确保索引有效
        if 0 <= image_index < len(self.tree_images):
            self.current_image = self.tree_images[image_index]
            # 获取画布尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            # 计算居中位置
            x = canvas_width // 2
            y = canvas_height // 2
            
            # 显示图像
            self.canvas.create_image(x, y, image=self.current_image)