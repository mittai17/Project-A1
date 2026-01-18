---
tags: [guide, obsidian, plugins]
---

# 🎨 Obsidian Setup & Plugin Recommendations

To get the most out of this **Knowledge Base**, I recommend installing the following Community Plugins in Obsidian.

## 🚀 Essential Plugins

### 1. **Dataview** (Highly Recommended)
*   **Why**: Your dashboard (`00_Index`) and `Roadmap` can use SQL-like queries to dynamically list files.
*   **Use Case**: "Show me all files tagged `#daily`" or "List all Modules where Status = 'In Progress'".
*   **Code Example**:
    ```dataview
    TABLE status, tech_stack
    FROM "Modules"
    ```

### 2. **Excalidraw**
*   **Why**: Mermaid is great for code flow, but Excalidraw is better for "Whiteboard" style architecture diagrams.
*   **Use Case**: Drawing the high-level system overview with hand-drawn visual style.

### 3. **Advanced Tables**
*   **Why**: Editing the Markdown tables (like the Command Cheatsheet in [[Operations/Runbook]]) is painful in raw text.
*   **Feature**: Auto-formatting, sorting, and easier column navigation.

### 4. **Obsidian Git**
*   **Why**: This documentation lives inside your Git repository.
*   **Feature**: Auto-commits your changes to GitHub every X minutes. Keeps your docs in sync with your code.

---

## 💅 Visual Enhancements

### 5. **Minimal Theme + Style Settings**
*   **Why**: To make the interface look cleaner and more "Technical".
*   **Config**: Use "True Black" mode and colorful headings to match the `> [!CALLOUTS]` used in this vault.

### 6. **Iconize** (formerly Icons)
*   **Why**: Adds icons to folders and files in the file explorer.
*   **Use Case**: Add a 🧠 icon for the `Core/` folder and a 🚀 icon for `Operations/`.

---

## 🧠 Functional Tools

### 7. **OmniSearch**
*   **Why**: Standard search is okay, but OmniSearch is fuzzy and faster. It helps find "Tanglish" terms even if you typo them.

### 8. **Templater**
*   **Why**: To automate the Daily Logs.
*   **Config**: Point it to `Daily_Logs/00_Template.md` so that pressing `Ctrl+N` automatically creates a pre-filled log for the day.

---

## 🕸️ Recommended Folder Structure (Virtual)

If you use **Iconize**, set up these icons:
- `00_Index`: 🏠
- `Core/`: 🧠
- `Operations/`: ⚙️
- `Daily_Logs/`: 📅
- `Skills/`: ⚡
