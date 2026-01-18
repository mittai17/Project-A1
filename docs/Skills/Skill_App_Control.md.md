---
tags: [skill, app, linux]
---

# 🖥️ Skill: App Control

A1 uses a heuristic approach to find and launch applications.

## 📂 Launch Strategy

When you say "Open [App Name]":

1.  **Exact Match**: Checks if `[App Name]` exists in `/usr/bin/`.
2.  **Desktop Files**: Scans `/usr/share/applications/*.desktop` for `Name=[App Name]`.
    -   *Example*: "Open Code" -> Matches `code.desktop` or `visual-studio-code.desktop`.
3.  **Fuzzy Match**: If no exact match, finds the closest installed binary.

## 🪟 Window Management

A1 can control *running* windows.

- **Focus**: "Focus Firefox" -> Uses `wmctrl -a firefox` or `hyprctl dispatch focuswindow firefox` (depending on DE).
- **Close**: "Close Terminal" -> Uses `pkill -f [name]` (Cautious!) or `wmctrl -c`.

> [!NOTE] Wayland Support
> On Wayland (Hyprland), A1 uses `hyprctl` commands. On X11, it uses `wmctrl`.

## ⚙️ Tanglish Handling
The skill receives the "Action" and "Target" from the Router, regardless of word order.
- "Firefox open" -> `action=open`, `target=firefox`
- "Open Firefox" -> `action=open`, `target=firefox`
The skill logic is identical for both languages.

---
## 🕸️ Connections
- Triggered by [[Core/Core_Router|Reflex Router]].
- Related to [[Skills/Skill_Arch_Linux|System Skills]].

[[00_Index|🔙 Return to Index]]
