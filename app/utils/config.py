#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
import json

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".focus_forest_config.json")

# 默认配置
DEFAULT_CONFIG = {
    "focus_duration": 25 * 60,  # 25分钟，单位：秒
    "short_break": 5 * 60,      # 5分钟，单位：秒
    "long_break": 15 * 60,      # 15分钟，单位：秒
    "auto_start_breaks": False, # 自动开始休息
    "strict_mode": False,       # 严格模式（窗口失焦则失败）
}

def get_config():
    """
    获取应用配置，如果配置文件不存在则创建
    
    Returns:
        dict: 配置字典
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 确保所有默认配置项存在
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            
            return config
        except Exception as e:
            print(f"读取配置文件出错: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        # 创建默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"保存配置文件出错: {e}")