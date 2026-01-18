---
tags: [skill, linux, arch]
---

# 🐧 Skill: Arch Linux System Control

This skill allows A1 to manage an **Arch Linux** system using `pacman` and `yay`.

## 🛠️ Commands Implemented

### 1. System Update
- **Trigger**: "Update system", "System update pannu"
- **Command**:
  ```python
  subprocess.Popen(["alacritty", "-e", "bash", "-c", "yay -Syu; read -p 'Done'"])
  ```
- **Behavior**: Launches a visible Alacritty terminal windows so the user can enter their `sudo` password safely. **A1 never handles user passwords.**

### 2. Package Installation
- **Trigger**: "Install [package]"
- **Logic**:
    1.  Searches for package: `yay -Ss [query]`
    2.  If exact match found: `yay -S [package]`
    3.  If ambiguous: "I found multiple packages..."

### 3. System Stats
- **Trigger**: "Check RAM", "Cpu status"
- **Command**: Uses `psutil` python library.
    -   **RAM**: `psutil.virtual_memory().percent`
    -   **CPU**: `psutil.cpu_percent()`

> [!WARNING] Distro Compatibility
> This skill is hardcoded for **Arch/Pacman**. Debian/Ubuntu users must modify `skills/arch.py` to use `apt` instead.
