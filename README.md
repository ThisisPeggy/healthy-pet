# healthy_pet

一个桌面健康提醒小宠物，帮助你养成健康的工作习惯。

当前版本：**0.2.7**

[English](README_EN.md)

---

## 关于作者

你好，我是 Peggy。这是我的第一个 GitHub 项目，但这个项目并不是我从 0 到 1 做起来的。我希望不久的未来，我可以从 0 到 1 开发一个项目。

因为我长期坐着办公，相信大部分打工仔跟我一样。所以，我很需要一个可以提醒我站立、休息眼睛以及早点睡觉的工具。需求很清晰了，但是怎么实现呢，模模糊糊的想法陆续出现在我脑海里，先看看有没有人有类似的项目吧，诶，还真的有，而且做得很好，但是很多内容是我不需要的，我的核心需求其实就三个。

于是我借助 Codex、Kiro 这些 AI 工具，帮我在 [DyberPet](https://github.com/ChaozhongLiu/DyberPet) 的项目上进行改造。终于，一款简单的健康提醒桌宠项目出来了。感谢原项目的作者以及原项目的各位贡献者。

我很自豪地说，三天的时间里我做出了一个自己需要，别人也可能需要的产品。

---

## 功能特性

### 核心功能

- **护眼提醒**：定时提醒你看向远处，休息眼睛
- **久坐提醒**：提醒你站起来活动，并进入倒计时模式
- **睡眠提醒**：到了设定的睡觉时间提醒你休息

### 交互特性

- 可拖拽宠物到屏幕任意位置
- 多种动画：站立、行走、睡觉、生气、拖拽、下落
- 气泡提醒，不打断工作
- 双击宠物或提醒气泡确认提醒
- 可自定义提醒声音
- 右键菜单快速访问设置

### 设置选项

- 开机自启（支持 Windows / macOS / Linux）
- 自定义提醒间隔和消息
- 提醒声音开关
- 窗口置顶
- 宠物大小调节（0.5x - 3.0x）
- 多语言支持（中文/英文）

### 窗口置顶说明

开启“窗口置顶”后，宠物会尽量保持在其他窗口上方：

- **macOS**：支持显示在全屏 App 的 Space 中，并使用更高窗口层级减少被覆盖
- **Windows**：使用系统 topmost 窗口，普通窗口、最大化窗口和多数普通全屏窗口上方可保持显示
- **Linux X11**：使用 `_NET_WM_STATE_ABOVE` 请求置顶，并提供 `xdotool` fallback
- **Linux Wayland / 独占全屏游戏 / 系统安全桌面**：受系统限制，无法保证覆盖

## 工作原理

### 活动追踪

程序监控键盘和鼠标活动：
- 5 分钟内有活动，工作时间持续累计
- 离开电脑超过 5 分钟，计时器重置
- 智能提醒，不打断工作

### 提醒逻辑

**护眼提醒**
- 每 20 分钟触发一次
- 出现提醒后开始 20 秒倒计时
- 期间使用鼠标或键盘，倒计时重新开始
- 连续 20 秒不使用电脑，提醒消失

**久坐提醒**
- 每 60 分钟触发一次
- 双击宠物确认站立，进入倒计时（默认 5 分钟）
- 不影响护眼提醒计时

**睡眠提醒**
- 到达设定时间（默认 23:30）触发
- 提醒持续显示，宠物保持睡觉状态
- 双击无法关闭
- 离开电脑超过 60 分钟自动消失

提醒优先级：睡眠 > 护眼 > 久坐

### 配置文件位置

- Windows: `%APPDATA%\healthy_pet`
- macOS: `~/Library/Application Support/healthy_pet`
- Linux: `~/.config/healthy_pet`

## 安装使用

### 系统要求

- Python 3.9 或更高版本
- Windows / macOS / Linux

### 方法一：使用 pip 安装（推荐）

```bash
pip install healthy-pet
```

运行：

```bash
healthy-pet
```

如需关闭终端后仍保持运行，使用后台启动命令：

```bash
healthy-pet-start
```

或：

```bash
python -m healthy_pet
```

**注意**：不同系统可能需要使用 `python3` 或 `py` 命令。

### 方法二：从源码运行

```bash
git clone https://github.com/ThisisPeggy/healthy_pet.git
cd healthy_pet
pip install -r requirements.txt
python -m healthy_pet
```

如果希望启动后关闭终端也不影响宠物运行，先执行 `pip install -e .`，然后运行：

```bash
healthy-pet-start
```

**注意**：如需使用开机自启功能，需额外执行：

```bash
pip install -e .
```

### Windows 批处理文件

双击 `install.bat` 安装依赖，双击 `start.bat` 启动程序。

## 使用说明

### 基本操作

- 左键拖拽：移动宠物
- 左键单击：拍拍宠物（在地面上时）
- 左键双击：确认提醒
- 右键点击：打开菜单

### 菜单选项

- 重置工作计时：重置当前工作时间累计
- 提醒设置：打开设置窗口
- 退出：关闭程序

### 开机自启

右键点击宠物 → 提醒设置 → 勾选"开机自启" → 保存

**Windows**：在注册表添加启动项  
**macOS**：在 `~/Library/LaunchAgents/` 创建 plist 文件  
**Linux**：在 `~/.config/autostart/` 创建 desktop 文件

## 项目结构

```
healthy_pet/
├── healthy_pet/
│   ├── app.py              # 主应用程序
│   ├── settings.py         # 设置管理
│   ├── startup.py          # 开机自启
│   ├── i18n.py             # 国际化
│   ├── paths.py            # 路径配置
│   ├── pet/                # 宠物窗口、动画、拖拽物理、平台置顶
│   ├── reminders/          # 提醒系统
│   ├── notifications/      # 通知系统
│   ├── res/                # 资源文件
│   └── ui/                 # 用户界面
├── run.py                  # 快捷启动脚本
└── requirements.txt        # 依赖列表
```

`healthy_pet/pet/` 中的主要模块：

- `window.py`：Qt 桌宠窗口和交互事件
- `animation.py`：动画状态和走路方向
- `motion.py`：拖拽、下落、反弹等物理状态
- `native_window.py`：Windows / macOS / Linux 原生置顶处理
- `sprites.py`：图片帧加载和缩放

## 致谢

本项目改编自 [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet)。

感谢原 DyberPet 项目及其作者提供的基础框架和灵感。

## 许可

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
