# PyFocus 设计文档

### 1. 目的和目标

#### 1.1 目的

开发一个Windows桌面应用程序，帮助用户在使用电脑时保持专注，避免被分散注意力。该应用通过视觉化的树木生长过程，激励用户完成预设的专注时间，同时提供专注历史记录和统计功能，帮助用户培养良好的工作/学习习惯。

#### 1.2 目标

提供简洁易用的专注定时功能，支持自定义时长
实现树木生长的视觉反馈，增强用户专注动力
监控用户专注状态，可选择严格模式防止分心
记录并展示用户专注历史，提供数据统计和分析
确保软件轻量化，启动迅速，不占用过多系统资源

### 2. 系统架构

#### 2.1 架构概览

应用采用MVC架构模式，分为以下主要组件：
模型层(Model): 负责数据处理和业务逻辑
视图层(View): 负责用户界面展示
控制器(Controller): 连接模型与视图，处理用户输入

#### 2.2 目录结构

```
Forest-py/
├── main.py                # 应用程序入口
├── app/
│   ├── core/              # 核心功能模块
│   │   ├── timer.py       # 定时器实现
│   │   └── focus_monitor.py # 窗口焦点监控
│   ├── docs/              # 文档
|   |   ├── demand_analysis.md # 需求分析文档
│   │   ├── design.md      # 软件设计文档
│   │   └── image/         # 实例截图
│   ├── ui/                # 用户界面模块
│   │   ├── main_window.py # 主窗口
│   │   ├── tree_view.py   # 树木视图
│   │   ├── settings_dialog.py # 设置对话框
│   │   └── history_view.py # 历史记录视图
│   └── utils/             # 工具模块
│       ├── config.py      # 配置管理
|       └── history.py     # 历史记录管理
└── resources/             # 资源文件
    └── trees/             # 树木图像资源
```

#### 2.3 模块关系图

```
                  +---------------+
                  |    main.py    |
                  +-------+-------+
                          |
                          v
                  +---------------+
                  | main_window.py|
                  +-------+-------+
                          |
          +---------------+----------------+
          |               |                |
+---------v------+ +------v-------+  +-----v--------+
|  tree_view.py  | |settings_dialog| |history_view.py|
+----------------+ +--------------+  +--------------+
          |               |               |
          v               v               v
+----------------+ +-------------+ +------------+
|   timer.py     | |  config.py  | | history.py |
+----------------+ +-------------+ +------------+
          |
          v
+----------------+
| focus_monitor.py|
+----------------+
```

### 3. 详细设计

#### 3.1 核心模块

##### 3.1.1 定时器模块 (timer.py)

职责: 管理专注倒计时功能
主要类: FocusTimer
主要方法:
start(): 开始计时
pause(): 暂停计时
resume(): 恢复计时
stop(): 停止计时
fail(): 标记专注失败
状态管理: 使用TimerState枚举表示不同状态（空闲、运行中、暂停、完成、失败）
回调机制: 提供on_tick、on_complete、on_fail等回调函数接口

##### 3.1.2 焦点监控模块 (focus_monitor.py)

职责: 监控应用窗口是否保持焦点
主要类: FocusMonitor
实现方法: 使用tkinter的焦点事件和独立线程定期检查
回调机制: 当检测到窗口失去焦点时触发on_focus_lost回调

##### 3.1.3 历史记录模块 (history.py)

职责: 管理用户专注会话的历史记录
主要类: HistoryManager
数据存储: 使用JSON文件存储历史数据
主要方法:
get_history(): 获取历史记录
add_session(): 添加会话记录
delete_session(): 删除会话记录
get_statistics(): 获取统计数据
数据结构: 每条记录包含开始时间、结束时间、计划时长、实际时长、状态等信息

#### 3.2 UI模块

##### 3.2.1 主窗口 (main_window.py)

职责: 应用的主界面
主要类: MainWindow
主要组件:

* 树木视图区域
* 计时器显示
* 控制按钮（开始、放弃）
* 工具栏（设置、历史）
* 事件处理:
* 专注会话开始/暂停/继续
* 放弃专注
* 会话结束（成功/失败）处理
* 窗口关闭处理

##### 3.2.2 树木视图 (tree_view.py)

职责: 显示树木生长过程
主要类: TreeView
实现方式: 使用tkinter的Canvas和PIL处理图像
主要方法:

* update_tree_growth(): 根据专注进度更新树木图像
* set_tree_dead(): 设置树木为枯萎状态

##### 3.2.3 设置对话框 (settings_dialog.py)

职责: 提供应用设置界面
主要类: SettingsDialog
设置项:

* 专注时间长度
* 短休息时间（后续可能增加番茄钟模式）
* 严格模式开关

##### 3.2.4 历史记录视图 (history_view.py)

职责: 显示和管理专注历史
主要类: HistoryView
主要组件:

* 历史记录表格
* 筛选选项
* 统计信息展示区
  功能:
* 查看详细记录
* 删除记录
* 查看不同时间范围的统计数据

#### 3.3 工具模块

##### 3.3.1 配置管理 (config.py)

职责: 管理应用配置
数据存储: 使用JSON文件
主要方法:

* get_config(): 获取配置
* save_config(): 保存配置

### 4. 外部依赖

#### 4.1 技术栈

Python: 3.6+，核心编程语言
tkinter: Python标准库，用于GUI开发
Pillow (PIL): 用于图像处理和显示

#### 4.2 库依赖

| 依赖库    | 用途         | 版本要求     |
| --------- | ------------ | ------------ |
| tkinter   | GUI框架      | Python标准库 |
| Pillow    | 图像处理     | 8.0.0+       |
| json      | 数据存储     | Python标准库 |
| threading | 多线程支持   | Python标准库 |
| datetime  | 时间处理     | Python标准库 |
| os        | 文件系统操作 | Python标准库 |
| time      | 时间函数     | Python标准库 |

#### 4.3 资源依赖

树木生长各阶段图片（至少5张）

### 5. 任务拆解

#### 5.1 项目初始化

 创建项目结构
 设置开发环境
 创建Git仓库

#### 5.2 核心功能开发

 实现定时器模块
 基本计时功能
 状态管理
 回调机制
 实现焦点监控模块
 窗口焦点检测
 断点检测规则

#### 5.3 数据管理开发

 实现配置管理模块
 读取/保存配置
 默认配置设置
 实现历史记录模块
 数据结构设计
 增删改查功能
 统计功能

#### 5.4 UI开发

 实现主窗口
 布局设计
 控制按钮
 事件处理
 实现树木视图
 图像加载和显示
 生长动画
 实现设置对话框
 参数配置界面
 配置保存功能
 实现历史记录视图
 表格展示
 详情查看
 统计图表

#### 5.5 测试与优化

 单元测试
 功能测试
 界面测试
 性能测试
 用户体验优化

#### 5.6 文档与发布

 需求分析文档
 设计文档
 用户手册
 打包与发布

### 6. 接口设计

#### 6.1 模块间接口

##### 6.1.1 定时器接口

```Python
class FocusTimer:
    def __init__(self, duration=25*60, on_tick=None, on_complete=None, on_fail=None):
        """初始化定时器"""

    def start(self):
        """开始计时"""

    def pause(self):
        """暂停计时"""

    def resume(self):
        """恢复计时"""

    def stop(self):
        """停止计时"""

    def fail(self):
        """标记为失败"""
```

##### 6.1.2 焦点监控接口

```Python
class FocusMonitor:
    def__init__(self, root, on_focus_lost=None, check_interval=1.0):
        """初始化焦点监控器"""

    def start_monitoring(self):
        """开始监控窗口焦点"""

    def stop_monitoring(self):
        """停止监控窗口焦点"""
```

##### 6.1.3 历史记录接口

```Python
class HistoryManager:
    @staticmethod
    def get_history():
        """获取历史记录"""

    @staticmethod
    def add_session(start_time, end_time, planned_duration, actual_duration, status, notes=""):
        """添加专注会话记录"""

    @staticmethod
    def delete_session(session_id):
        """删除指定的会话记录"""

    @staticmethod
    def get_statistics(days=30):
        """获取过去指定天数的统计数据"""
```

#### 6.2 数据接口

##### 6.2.1 会话记录结构

```JSON
{
  "id": 1647852369123,
  "start_time": 1647852300,
  "end_time": 1647853800,
  "planned_duration": 1500,
  "actual_duration": 1500,
  "status": "completed",
  "notes": "成功完成"
}
```

##### 6.2.2 配置文件结构

```JSON
{
  "focus_duration": 1500,
  "short_break": 300,
  "long_break": 900,
  "auto_start_breaks": false,
  "strict_mode": false
}
```

### 7. 时间线

#### 7.1 开发阶段

| 阶段  | 任务                 | 时间估计 | 截止日期 |
| ----- | -------------------- | -------- | -------- |
| 阶段1 | 核心模块            | 1天      | 第3周初  |
| 阶段2 | 基础UI与核心功能集成 | 2天      | 第3周中  |
| 阶段3 | 数据持久化与设置功能 | 2天      | 第3周中后  |
| 阶段4 | 历史记录与统计功能   | 2天      | 第3周末  |
| 阶段5 | 测试、优化与文档     | 1周      | 第4周末  |

### 7.2 里程碑
MVP版本完成 - 第3周中
* 基本计时功能
* 树木生长显示
* 窗口焦点监控

Alpha版本发布 - 预计第4周末
