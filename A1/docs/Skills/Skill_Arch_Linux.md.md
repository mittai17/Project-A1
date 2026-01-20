---
tags: [skill, linux, arch, system-control, complete]
---

# 🐧 Skill: Complete Arch Linux Control

**40+ voice commands** for complete control of your Arch Linux system. This is the most comprehensive system control skill in A1.

---

## ⚡ Power Management

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Shutdown" | Power off | `systemctl poweroff` |
| "Reboot" | Restart system | `systemctl reboot` |
| "Suspend" / "Sleep" | Sleep mode | `systemctl suspend` |
| "Lock screen" | Lock display | hyprlock/swaylock/i3lock |

---

## 🔊 Audio Control

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Volume up" / "Louder" | Increase volume 5% | `pactl` / `wpctl` |
| "Volume down" / "Quieter" | Decrease volume 5% | `pactl` / `wpctl` |
| "Mute" / "Unmute" | Toggle mute | `pactl` / `wpctl` |

---

## 💡 Display Control

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Brightness up" / "Brighter" | Increase brightness 10% | `brightnessctl` |
| "Brightness down" / "Dimmer" | Decrease brightness 10% | `brightnessctl` |
| "Night mode on" | Enable warm screen (4500K) | `gammastep` / `redshift` |
| "Night mode off" | Disable warm screen | `gammastep -x` |

---

## 📶 Network Control

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "WiFi on" | Enable WiFi | `nmcli radio wifi on` |
| "WiFi off" | Disable WiFi | `nmcli radio wifi off` |
| "WiFi status" | Check connection | `nmcli dev wifi` |

---

## 📱 Bluetooth Control

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Bluetooth on" | Enable Bluetooth | `bluetoothctl power on` |
| "Bluetooth off" | Disable Bluetooth | `bluetoothctl power off` |
| "Bluetooth status" | Check connections | `bluetoothctl show` |

---

## 📸 Screenshots

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Take a screenshot" | Capture full screen | grimblast/grim/scrot |
| "Screenshot area" | Select region | grimblast area/scrot -s |

> Screenshots saved to `~/Pictures/screenshot_[timestamp].png`

---

## 🎵 Media Controls (MPRIS)

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Play" / "Pause" / "Play pause" | Toggle playback | `playerctl play-pause` |
| "Next song" / "Skip" | Next track | `playerctl next` |
| "Previous song" | Previous track | `playerctl previous` |
| "Stop music" | Stop playback | `playerctl stop` |

---

## 📦 Package Management

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Update system" | Full system update | `yay -Syu` |
| "Install [package]" | Install package | `yay -S [pkg]` |
| "Uninstall [package]" | Remove package | `yay -Rs [pkg]` |

### Smart Package Resolution
- "Install vscode" → `visual-studio-code-bin`
- "Install spotify" → `spotify` (prefers `-bin` variants)

---

## 🧹 System Cleanup

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Clean cache" | Clear package cache | `paccache -r` |
| "Remove orphans" | Remove orphaned packages | `pacman -Rns $(pacman -Qdtq)` |
| "Clear logs" | Clear old journal logs | `journalctl --vacuum-time=3d` |
| "Empty trash" | Empty trash folder | File system |

---

## 🔕 Notifications

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Do not disturb" | Pause notifications | `dunstctl` / `makoctl` |
| "Do not disturb off" | Resume notifications | `dunstctl` / `makoctl` |

---

## 📋 Clipboard

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Clear clipboard" | Empty clipboard | `wl-copy --clear` / `xclip` |
| "Read clipboard" | Get clipboard content | `wl-paste` / `xclip -o` |

---

## 🗂️ File Manager

| Voice Command | Function |
| :--- | :--- |
| "Open file manager" | Open home folder |
| "Open downloads" | Open ~/Downloads |
| "Open documents" | Open ~/Documents |

> Supports: Nautilus, Dolphin, Thunar, PCManFM, Nemo

---

## ⏱️ Timer

| Voice Command | Function |
| :--- | :--- |
| "Set timer for 5 minutes" | Desktop notification + sound after 5 min |
| "Timer 10 min" | Desktop notification after 10 min |

---

## ⚙️ Process Control

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Kill [app]" | Terminate process | `pkill -f [app]` |
| "Force kill [app]" | Force terminate | `pkill -9 -f [app]` |

---

## 🔋 Power Profiles

| Voice Command | Function | Backend |
| :--- | :--- | :--- |
| "Performance mode" | Max performance | `powerprofilesctl set performance` |
| "Power saver" | Battery saving | `powerprofilesctl set power-saver` |
| "Balanced mode" | Balanced | `powerprofilesctl set balanced` |

---

## 📊 System Info

| Voice Command | Function |
| :--- | :--- |
| "System status" | Full status (CPU, RAM, Disk, Battery, Network) |
| "Check RAM" / "CPU usage" | Quick stats |
| "Uptime" | How long system running |
| "What time is it" | Current time and date |

### Example System Status Output
```
System Status:
• CPU: 2.5%
• RAM: 33.9% (5.0/15.0 GB)
• Disk: 15.0% (70/474 GB)
• Network: Connected
• Battery: 100.0% (charging)
```

---

## 🔧 Required Dependencies

| Tool | Purpose | Install |
| :--- | :--- | :--- |
| `pactl` | Audio control | `pulseaudio` or `pipewire-pulse` |
| `brightnessctl` | Brightness | `yay -S brightnessctl` |
| `nmcli` | WiFi control | `yay -S networkmanager` |
| `bluetoothctl` | Bluetooth | `yay -S bluez bluez-utils` |
| `gammastep` | Night mode | `yay -S gammastep` |
| `playerctl` | Media control | `yay -S playerctl` |
| `dunst` | Notifications | `yay -S dunst` |
| `grim`/`slurp` | Screenshots (Wayland) | `yay -S grim slurp` |
| `paccache` | Cache cleanup | `yay -S pacman-contrib` |

---

## 🕸️ Connections
- [[Core/Core_Router|Intent Router]]
- [[Skills/Skill_Weather.md|Weather Skill]]
- [[Operations/Runbook|Voice Commands Reference]]
- [[00_Index|🔙 Return to Index]]
