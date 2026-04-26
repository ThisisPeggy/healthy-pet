# healthy_pet

A desktop health reminder pet that helps you develop healthy work habits.

Current version: **0.2.3**

[中文](README.md)

---

## About the Author

Hello, I'm Peggy. This is my first GitHub project, though it wasn't built from scratch. I hope that in the near future, I'll be able to develop a project from 0 to 1.

As someone who sits at a desk for long hours, I believe most office workers are in the same boat. I really needed a tool to remind me to stand up, rest my eyes, and go to bed early. The requirements were clear, but how to implement them? Vague ideas kept popping into my head. Let me see if anyone has a similar project... and yes, there was one! It was well-made, but had many features I didn't need. My core needs were actually just three things.

So I used AI tools like Codex and Kiro to help me adapt the [DyberPet](https://github.com/ChaozhongLiu/DyberPet) project. Finally, a simple health reminder desktop pet was born. Thanks to the original project author and all contributors.

I'm proud to say that in three days, I created a product that I need and others might need too.

---

## Features

### Core Functions

- **Eye Rest Reminder**: Periodic reminders to look away and rest your eyes
- **Standing Reminder**: Reminds you to stand up and move, with countdown mode
- **Sleep Reminder**: Reminds you to rest at your set bedtime

### Interactive Features

- Drag the pet anywhere on screen
- Multiple animations: standing, walking, sleeping, angry, dragging, falling
- Bubble notifications that don't interrupt work
- Customizable reminder sounds
- Right-click menu for quick settings access

### Settings

- Start on boot (Windows / macOS / Linux)
- Customizable reminder intervals and messages
- Sound toggle for reminders
- Always on top option
- Pet scale adjustment (0.5x - 3.0x)
- Multi-language support (Chinese/English)

## How It Works

### Activity Tracking

The program monitors keyboard and mouse activity:
- Work time accumulates if active within last 5 minutes
- Timer resets if away for more than 5 minutes
- Smart reminders that don't interrupt work

### Reminder Logic

**Eye Rest**
- Triggers every 20 minutes
- 20-second countdown starts when reminder appears
- Countdown resets if you use mouse or keyboard
- Reminder disappears after 20 consecutive seconds of inactivity

**Standing Break**
- Triggers every 60 minutes
- Double-click pet to confirm standing, starts countdown (default 5 minutes)
- Does not affect eye rest timer

**Sleep Reminder**
- Triggers at set time (default 23:30)
- Reminder persists, pet stays in sleep state
- Cannot be dismissed by double-clicking
- Auto-dismisses after 60 minutes of inactivity

Priority: Sleep > Eye Rest > Standing

### Config File Location

- Windows: `%APPDATA%\healthy_pet`
- macOS: `~/Library/Application Support/healthy_pet`
- Linux: `~/.config/healthy_pet`

## Installation

### Requirements

- Python 3.9 or higher
- Windows / macOS / Linux

### Method 1: Install via pip (Recommended)

```bash
pip install healthy-pet
```

Run:

```bash
healthy-pet
```

Or:

```bash
python -m healthy_pet
```

**Note**: Different systems may require `python3` or `py` command.

### Method 2: Run from Source

```bash
git clone https://github.com/ThisisPeggy/healthy_pet.git
cd healthy_pet
pip install -r requirements.txt
python -m healthy_pet
```

**Note**: To use the auto-start feature, you need to additionally run:

```bash
pip install -e .
```

### Windows Batch Files

Double-click `install.bat` to install dependencies, double-click `start.bat` to launch.

## Usage

### Basic Operations

- Left-click drag: Move pet
- Left-click: Pat the pet (when on ground)
- Double-click: Acknowledge reminder
- Right-click: Open menu

### Menu Options

- Reset Work Timer: Reset current work time accumulation
- Settings: Open settings window
- Quit: Close program

### Auto-start on Boot

Right-click pet → Settings → Check "Start on Boot" → Save

**Windows**: Adds registry entry  
**macOS**: Creates plist file in `~/Library/LaunchAgents/`  
**Linux**: Creates desktop file in `~/.config/autostart/`

## Project Structure

```
healthy_pet/
├── healthy_pet/
│   ├── app.py              # Main application
│   ├── settings.py         # Settings management
│   ├── startup.py          # Auto-start functionality
│   ├── i18n.py             # Internationalization
│   ├── paths.py            # Path configuration
│   ├── pet/                # Pet window
│   ├── reminders/          # Reminder system
│   ├── notifications/      # Notification system
│   ├── res/                # Resources
│   └── ui/                 # User interface
├── run.py                  # Quick launch script
└── requirements.txt        # Dependencies
```

## Credits

This project was adapted from [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet).

Thanks to the original DyberPet project and its author for providing the base framework and inspiration.

## License

MIT License

## Contributing

Issues and Pull Requests are welcome.
