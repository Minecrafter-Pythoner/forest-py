#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
历史记录数据管理模块
"""

import os
import json
import time
import datetime
from enum import Enum

# 历史记录文件路径
HISTORY_FILE = os.path.join(os.path.expanduser("~"), ".focus_forest_history.json")

class SessionStatus(Enum):
    """会话状态枚举"""
    COMPLETED = "completed"  # 成功完成
    FAILED = "failed"        # 中途放弃
    INTERRUPTED = "interrupted"  # 被打断（如窗口失焦）


class HistoryManager:
    """历史记录管理器"""
    
    @staticmethod
    def get_history():
        """
        获取历史记录
        
        Returns:
            list: 历史记录列表
        """
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                return history
            except Exception as e:
                print(f"Error reading history file: {e}")
                return []
        else:
            # 如果文件不存在，返回空列表
            return []
    
    @staticmethod
    def add_session(start_time, end_time, planned_duration, actual_duration, status, notes=""):
        """
        添加专注会话记录
        
        Args:
            start_time: 开始时间戳
            end_time: 结束时间戳
            planned_duration: 计划时长（秒）
            actual_duration: 实际时长（秒）
            status: 会话状态 (SessionStatus枚举)
            notes: 备注信息
        """
        # 获取当前历史记录
        history = HistoryManager.get_history()
        
        # 创建新的会话记录
        session = {
            "id": int(time.time() * 1000),  # 使用时间戳作为唯一ID
            "start_time": start_time,
            "end_time": end_time,
            "planned_duration": planned_duration,
            "actual_duration": actual_duration,
            "status": status.value if isinstance(status, SessionStatus) else status,
            "notes": notes
        }
        
        # 添加到历史记录
        history.append(session)
        
        # 保存历史记录
        HistoryManager._save_history(history)
        
        return session
    
    @staticmethod
    def delete_session(session_id):
        """
        删除指定的会话记录
        
        Args:
            session_id: 会话ID
        """
        # 获取当前历史记录
        history = HistoryManager.get_history()
        
        # 过滤掉要删除的会话
        history = [session for session in history if session.get("id") != session_id]
        
        # 保存历史记录
        HistoryManager._save_history(history)
    
    @staticmethod
    def clear_history():
        """清除所有历史记录"""
        HistoryManager._save_history([])
    
    @staticmethod
    def _save_history(history):
        """
        保存历史记录到文件
        
        Args:
            history: 历史记录列表
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history file: {e}")
    
    @staticmethod
    def get_statistics(days=30):
        """
        获取过去指定天数的统计数据
        
        Args:
            days: 要统计的天数
            
        Returns:
            dict: 包含统计信息的字典
        """
        # 获取历史记录
        history = HistoryManager.get_history()
        
        # 计算截止时间点（过去days天的起始时间）
        now = time.time()
        if days == 0:
            days = 2000*365
        cutoff_time = now - (days * 24 * 60 * 60)
        
        # 筛选时间范围内的会话记录
        recent_sessions = [s for s in history if s.get("start_time", 0) >= cutoff_time]
        
        # 计算统计数据
        total_sessions = len(recent_sessions)
        completed_sessions = len([s for s in recent_sessions if s.get("status") == SessionStatus.COMPLETED.value])
        failed_sessions = len([s for s in recent_sessions if s.get("status") == SessionStatus.FAILED.value])
        interrupted_sessions = len([s for s in recent_sessions if s.get("status") == SessionStatus.INTERRUPTED.value])
        
        # 计算总专注时间
        total_focus_time = sum(s.get("actual_duration", 0) for s in recent_sessions)
        
        # 计算完成率
        completion_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "failed_sessions": failed_sessions,
            "interrupted_sessions": interrupted_sessions,
            "total_focus_time": total_focus_time,
            "completion_rate": completion_rate,
            "days": days
        }


def format_timestamp(timestamp):
    """
    将时间戳格式化为可读日期时间
    
    Args:
        timestamp: 时间戳
        
    Returns:
        str: 格式化的日期时间字符串
    """
    dt = datetime.datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds):
    """
    将秒数格式化为可读时间
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时间字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}hours {minutes}minutes {secs}seconds"
    elif minutes > 0:
        return f"{minutes}minutes {secs}seconds"
    else:
        return f"{secs}seconds"