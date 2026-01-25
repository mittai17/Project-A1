from mcp.server.fastmcp import FastMCP
from skills import arch, weather, personal_assistant
import datetime

# Initialize FastMCP Server
mcp = FastMCP("A1 Local Tools")

@mcp.tool()
def get_system_status() -> str:
    """Get CPU, GPU, RAM, and Network stats."""
    return arch.get_full_system_status()

@mcp.tool()
def get_weather(location: str = "Chennai") -> str:
    """Get current weather for a location."""
    return weather.get_weather(location)

@mcp.tool()
def take_note(content: str) -> str:
    """Save a secure note to the user's log."""
    return personal_assistant.take_note(content)

@mcp.tool()
def read_notes() -> str:
    """Read the user's recent notes."""
    return personal_assistant.read_notes()

from skills import automation

@mcp.tool()
def type_string(text: str) -> str:
    """Type a string into the currently focused window."""
    return automation.type_text(text)

@mcp.tool()
def press_key(key: str) -> str:
    """Press a key (e.g. 'Enter', 'ctrl+c')."""
    return automation.press_key(key)

@mcp.tool()
def click_mouse() -> str:
    """Click the left mouse button."""
    return automation.mouse_click()

@mcp.tool()
def lock_system() -> str:
    """Locks the screen immediately."""
    return arch.lock_screen()

@mcp.tool()
def get_gpu_stats() -> str:
    """Get detailed Nvidia GPU statistics."""
    # We reuse the logic from get_system_stats or call nvidia-smi directly
    import subprocess
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total', '--format=csv,noheader'], capture_output=True, text=True)
        if result.returncode == 0:
            return f"GPU Status: {result.stdout.strip()}"
    except:
        pass
    return "GPU stats unavailable."

if __name__ == "__main__":
    mcp.run()
