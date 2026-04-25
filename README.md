# healthy_pet

`healthy_pet` 是一个基于 PySide6 开发的桌面健康提醒小宠物，通过可爱的桌面宠物形象，帮助你养成健康的工作习惯。

`healthy_pet` is a desktop health reminder pet built with PySide6 that helps you develop healthy work habits through a cute desktop companion.

当前版本 / Current version: **0.2.1**

---

## 👋 关于作者 / About the Author

你好，我是 Peggy。这是我的第一个 GitHub 项目，但这个项目并不是我从 0 到 1 做起来的。我希望不久的未来，我可以从 0 到 1 开发一个项目。

因为我长期坐着办公，相信大部分打工仔跟我一样。所以，我很需要一个可以提醒我站立、休息眼睛以及早点睡觉的工具。需求很清晰了，但是怎么实现呢，模模糊糊的想法陆续出现在我脑海里，先看看有没有人有类似的项目吧，诶，还真的有，而且做得很好，但是很多内容是我不需要的，我的核心需求其实就三个。

于是我借助 Codex、Kiro 这些 AI 工具，帮我在 [DyberPet](https://github.com/ChaozhongLiu/DyberPet) 的项目上进行改造。终于，一款简单的健康提醒桌宠项目出来了。感谢原项目的作者以及原项目的各位贡献者。

我很自豪地说，三天的时间里我做出了一个自己需要，别人也可能需要的产品。

---

Hello, I'm Peggy. This is my first GitHub project, though it wasn't built from scratch. I hope that in the near future, I'll be able to develop a project from 0 to 1.

As someone who sits at a desk for long hours, I believe most office workers are in the same boat. I really needed a tool to remind me to stand up, rest my eyes, and go to bed early. The requirements were clear, but how to implement them? Vague ideas kept popping into my head. Let me see if anyone has a similar project... and yes, there was one! It was well-made, but had many features I didn't need. My core needs were actually just three things.

So I used AI tools like Codex and Kiro to help me adapt the [DyberPet](https://github.com/ChaozhongLiu/DyberPet) project. Finally, a simple health reminder desktop pet was born. Thanks to the original project author and all contributors.

I'm proud to say that in three days, I created a product that I need and others might need too.

---

## ✨ 功能特性 / Features

### 🎯 核心功能 / Core Features

- **护眼提醒** / **Eye Rest Reminder**  
  每隔一段时间提醒你看向远处，休息眼睛，避免长时间盯着屏幕导致视疲劳。
  
- **久坐提醒** / **Standing Reminder**  
  工作一段时间后提醒你站起来活动，并进入倒计时模式，鼓励你完成站立休息。
  
- **睡眠提醒** / **Sleep Reminder**  
  到了设定的睡觉时间，宠物会提醒你该休息了，避免熬夜。

### 🎨 交互特性 / Interactive Features

- **可拖拽宠物** / **Draggable Pet**  
  可以用鼠标拖动宠物到屏幕任意位置，松手后会有物理下落效果。
  
- **多种动画** / **Multiple Animations**  
  宠物有多种动作：站立、行走、睡觉、生气、拖拽、下落等，让桌面更生动。
  
- **气泡提醒** / **Bubble Notifications**  
  提醒信息通过可爱的气泡显示在宠物上方，不会打断你的工作。

- **提醒声音** / **Reminder Sounds**  
  使用猫叫声作为提醒声音，并可分别选择护眼、久坐、睡眠提醒是否播放声音。
  
- **右键菜单** / **Context Menu**  
  右键点击宠物可以打开菜单，快速访问设置、重置计时器等功能。

### ⚙️ 设置选项 / Settings

- **开机自启** / **Start on Boot** (Windows / macOS / Linux)  
  可选择是否开机自动启动，方便每天使用。支持所有主流操作系统。
  
- **自定义提醒间隔** / **Customizable Intervals**  
  可以自定义护眼、久坐、睡眠提醒的时间间隔。
  
- **自定义提醒消息** / **Custom Messages**  
  可以修改提醒时显示的文字内容。

- **提醒声音选择** / **Sound Selection**  
  可以开启或关闭全部提醒声音，也可以单独选择护眼、久坐、睡眠提醒是否有声音。
  
- **窗口置顶** / **Always on Top**  
  可选择宠物窗口是否始终保持在最前面。
  
- **宠物大小调节** / **Pet Scale**  
  可以调整宠物的显示大小（0.5x - 3.0x）。
  
- **多语言支持** / **Multi-language**  
  支持中文和英文界面切换。

## 🧠 工作原理 / How It Works

### 活动追踪 / Activity Tracking

程序会监控你的键盘和鼠标活动：
- **活动时间累计**：只要你在 5 分钟内有过活动，工作时间就会持续累计
- **空闲重置**：如果你离开电脑超过 5 分钟，计时器会重置
- **智能提醒**：提醒会在合适的时间触发，不会打断你的工作

The program monitors your keyboard and mouse activity:
- **Active time accumulation**: Work time accumulates as long as you've been active within the last 5 minutes
- **Idle reset**: Timer resets if you're away for more than 5 minutes
- **Smart reminders**: Reminders trigger at appropriate times without interrupting your work

### 提醒逻辑 / Reminder Logic

1. **护眼提醒** / **Eye Rest**
   - 每 20 分钟触发一次（独立计时）
   - 出现提醒后开始 20 秒倒计时
   - **如果期间使用鼠标或键盘，倒计时会重新从 20 秒开始**
   - 只有连续 20 秒不使用电脑，倒计时才会结束，提醒消失
   - 这样确保你真正休息了眼睛

2. **久坐提醒** / **Standing Break**
   - 每 60 分钟触发一次（独立计时）
   - **双击宠物确认你已经站立**，然后进入站立倒计时（默认 5 分钟）
   - 站立休息不会影响护眼提醒的计时

3. **睡眠提醒** / **Sleep Reminder**
   - 到达设定时间（默认 23:30）后触发
   - 提醒会持续显示，宠物保持睡觉状态
   - 双击宠物无法关闭睡眠提醒（该睡觉了！）
   - 只有离开电脑超过 60 分钟，提醒才会自动消失
   - 注：空闲自动消失时间为隐藏设置，可在用户配置文件中修改 `sleep_idle_clear_minutes` 字段

**提醒优先级：** 睡眠 > 护眼 > 久坐

### 物理效果 / Physics

- **重力系统**：拖拽宠物后松手，会有真实的下落效果
- **边界碰撞**：宠物会在屏幕边缘反弹
- **地面检测**：宠物会自动停留在屏幕底部

### 用户配置目录 / User Config Directory

程序会把设置和语言选择保存在用户配置目录，而不是项目源码目录。

The app stores settings and language preferences in the user's config directory, not in the source tree.

- Windows: `%APPDATA%\healthy_pet`
- macOS: `~/Library/Application Support/healthy_pet`
- Linux: `~/.config/healthy_pet`

主要配置文件 / Main config files:

- `healthy_settings.json`
- `language.json`

## 📦 安装使用 / Installation

### 前置要求 / Requirements

- Python 3.9 或更高版本 / Python 3.9 or higher
- Windows / macOS / Linux

### 快速开始 / Quick Start

#### 方法一：使用 pip 安装（推荐）/ Method 1: Install via pip (Recommended)

```bash
pip install healthy-pet
```

安装后直接运行 / After installation, run directly:
```bash
healthy-pet
```

或作为 Python 模块运行 / Or run as a Python module:
```bash
python -m healthy_pet
```

#### 方法二：使用批处理文件（Windows）/ Method 2: Using Batch Files (Windows)

1. 克隆项目 / Clone the repository:
   ```bash
   git clone https://github.com/ThisisPeggy/healthy_pet.git
   cd healthy_pet
   ```

2. 双击 `install.bat` 安装依赖 / Double-click `install.bat` to install dependencies

3. 双击 `start.bat` 启动程序 / Double-click `start.bat` to start the app

#### 方法三：从源码运行 / Method 3: Run from Source

1. 克隆项目 / Clone the repository:
   ```bash
   git clone https://github.com/ThisisPeggy/healthy_pet.git
   cd healthy_pet
   ```

2. 安装依赖 / Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. 启动程序 / Start the app:
   ```bash
   python -m healthy_pet
   ```
   
   或使用快捷脚本 / Or use the shortcut script:
   ```bash
   python run.py
   ```



## 🎮 使用说明 / Usage

### 基本操作 / Basic Operations

- **左键拖拽**：移动宠物位置
- **左键单击**：拍拍宠物（在地面上时）
- **左键双击**：确认提醒
- **右键点击**：打开菜单

### 菜单选项 / Menu Options

- **重置工作计时** / **Reset Work Timer**：重置当前的工作时间累计
- **提醒设置** / **Settings**：打开设置窗口
- **退出** / **Quit**：关闭程序

### 开机自启 / Auto-start

#### Windows

1. 右键点击宠物，选择"提醒设置" / Right-click the pet, select "Settings"
2. 勾选"开机自启" / Check "Start on Boot"
3. 点击"保存" / Click "Save"
4. 下次开机登录后，程序会自动启动 / The app will start automatically on next login

程序会在注册表 `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` 中添加启动项，使用 `pythonw.exe` 启动以避免弹出控制台窗口。

The app registers itself in `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` using `pythonw.exe` to avoid showing a console window.

#### macOS

1. 右键点击宠物，选择"提醒设置" / Right-click the pet, select "Settings"
2. 勾选"开机自启" / Check "Start on Boot"
3. 点击"保存" / Click "Save"

程序会在 `~/Library/LaunchAgents/` 目录创建 plist 文件来实现开机自启。

The app creates a plist file in `~/Library/LaunchAgents/` for auto-start.

#### Linux

1. 右键点击宠物，选择"提醒设置" / Right-click the pet, select "Settings"
2. 勾选"开机自启" / Check "Start on Boot"
3. 点击"保存" / Click "Save"

程序会在 `~/.config/autostart/` 目录创建 desktop 文件来实现开机自启。

The app creates a desktop file in `~/.config/autostart/` for auto-start.

## 📁 项目结构 / Project Structure

```text
healthy_pet/
├── healthy_pet/           # 应用核心代码 / Application code
│   ├── app.py            # 主应用程序 / Main application
│   ├── settings.py       # 设置管理 / Settings management
│   ├── startup.py        # 开机自启 / Auto-start functionality
│   ├── i18n.py           # 国际化 / Internationalization
│   ├── paths.py          # 路径配置 / Path configuration
│   ├── pet/              # 宠物窗口 / Pet window
│   │   └── window.py     # 宠物主窗口和动画 / Pet main window and animations
│   ├── reminders/        # 提醒系统 / Reminder system
│   │   ├── engine.py     # 提醒引擎 / Reminder engine
│   │   └── activity.py   # 活动追踪 / Activity tracking
│   ├── notifications/    # 通知系统 / Notification system
│   │   ├── bubble.py     # 气泡窗口 / Bubble window
│   │   └── notifier.py   # 系统托盘通知 / System tray notifications
│   ├── res/              # 包内资源 / Packaged resources
│   │   ├── icons/        # 图标 / Icons
│   │   ├── sounds/       # 提醒声音 / Reminder sounds
│   │   └── role/Kitty/   # 宠物动画帧 / Pet animation frames
│   └── ui/               # 用户界面 / User interface
│       └── settings_window.py  # 设置窗口 / Settings window
├── run.py                # 源码运行入口 / Source-run entry point
├── requirements.txt      # 依赖列表 / Dependencies
├── install.bat           # 安装脚本（Windows）/ Install script (Windows)
└── start.bat             # 启动脚本（Windows）/ Start script (Windows)
```

## 🙏 致谢 / Credits

本项目改编自 [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet)。

感谢原 DyberPet 项目及其作者提供的基础框架和灵感。

This project was adapted from [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet).

Thanks to the original DyberPet project and its author for providing the base framework and inspiration.

## 📝 许可 / License

MIT License

Copyright (c) 2024 ItisP

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request！

Issues and Pull Requests are welcome!
