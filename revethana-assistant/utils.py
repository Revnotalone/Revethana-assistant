"""
utils.py - Terminal UI, Colors, Typing Animation
Revethana Assistant
"""

import sys
import time
import os
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows
init(autoreset=True)

# ─── Color Palette ───────────────────────────────────────────────
C_CYAN    = Fore.CYAN + Style.BRIGHT
C_GREEN   = Fore.GREEN + Style.BRIGHT
C_YELLOW  = Fore.YELLOW + Style.BRIGHT
C_RED     = Fore.RED + Style.BRIGHT
C_MAGENTA = Fore.MAGENTA + Style.BRIGHT
C_WHITE   = Fore.WHITE + Style.BRIGHT
C_BLUE    = Fore.BLUE + Style.BRIGHT
C_RESET   = Style.RESET_ALL
C_DIM     = Style.DIM

# ─── Status Line Control ─────────────────────────────────────────
_status_active = False

def clear_status():
    """Hapus status line saat ini."""
    global _status_active
    if _status_active:
        sys.stdout.write('\r' + ' ' * 60 + '\r')
        sys.stdout.flush()
        _status_active = False

def print_status(status: str):
    """Tampilkan status indicator real-time."""
    global _status_active
    icons = {
        "LISTENING...": f"{C_GREEN}◉{C_RESET}",
        "THINKING...":  f"{C_YELLOW}◌{C_RESET}",
        "SPEAKING...":  f"{C_MAGENTA}◈{C_RESET}",
        "LOADING...":   f"{C_CYAN}◎{C_RESET}",
    }
    icon = icons.get(status, f"{C_WHITE}◎{C_RESET}")
    line = f"\r  {icon}  {C_DIM}{status}{C_RESET}   "
    sys.stdout.write(line)
    sys.stdout.flush()
    _status_active = True

def print_banner():
    """Tampilkan banner startup Revethana."""
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""
{C_CYAN}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   {C_WHITE}██████╗ ███████╗██╗   ██╗███████╗████████╗██╗  ██╗{C_CYAN}      ║
║   {C_WHITE}██╔══██╗██╔════╝██║   ██║██╔════╝╚══██╔══╝██║  ██║{C_CYAN}      ║
║   {C_WHITE}██████╔╝█████╗  ██║   ██║█████╗     ██║   ███████║{C_CYAN}      ║
║   {C_WHITE}██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝     ██║   ██╔══██║{C_CYAN}      ║
║   {C_WHITE}██║  ██║███████╗ ╚████╔╝ ███████╗   ██║   ██║  ██║{C_CYAN}      ║
║   {C_WHITE}╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝   ╚═╝   ╚═╝  ╚═╝{C_CYAN}      ║
║                                                          ║
║   {C_MAGENTA}A N A  A S S I S T A N T{C_CYAN}                                 ║
║   {C_DIM}Powered by Gemini 2.5 Flash  ·  v1.0.0{C_CYAN}                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝{C_RESET}
"""
    print(banner)
    print(f"  {C_DIM}──────────────────────────────────────────────────────{C_RESET}")
    print(f"  {C_CYAN}TIPS:{C_RESET} Bicara dengan natural. Dukung Bahasa Indonesia & Inggris.")
    print(f"  {C_CYAN}EXIT:{C_RESET} Katakan {C_YELLOW}'exit'{C_RESET} atau {C_YELLOW}'matikan'{C_RESET} untuk berhenti.")
    print(f"  {C_DIM}──────────────────────────────────────────────────────{C_RESET}\n")

def print_user(text: str):
    """Print pesan dari user."""
    clear_status()
    print(f"\n  {C_CYAN}┌─ YOU ─────────────────────────────────────────────┐{C_RESET}")
    print(f"  {C_CYAN}│{C_RESET}  {C_WHITE}{text}{C_RESET}")
    print(f"  {C_CYAN}└────────────────────────────────────────────────────{C_RESET}")

def print_ai(text: str, typing: bool = True):
    """Print respons AI dengan typing animation."""
    clear_status()
    print(f"\n  {C_MAGENTA}┌─ REVETHANA ────────────────────────────────────────┐{C_RESET}")
    sys.stdout.write(f"  {C_MAGENTA}│{C_RESET}  {C_WHITE}")
    sys.stdout.flush()
    
    if typing and len(text) <= 300:
        # Typing animation untuk teks pendek
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.018)
    else:
        # Langsung print untuk teks panjang
        sys.stdout.write(text)
        sys.stdout.flush()
    
    print(C_RESET)
    print(f"  {C_MAGENTA}└────────────────────────────────────────────────────{C_RESET}\n")

def print_info(text: str):
    """Print info message."""
    clear_status()
    print(f"  {C_BLUE}ℹ  {C_DIM}{text}{C_RESET}")

def print_error(text: str):
    """Print error message."""
    clear_status()
    print(f"  {C_RED}✗  {text}{C_RESET}")

def print_success(text: str):
    """Print success message."""
    clear_status()
    print(f"  {C_GREEN}✓  {text}{C_RESET}")

def print_divider():
    """Print divider line."""
    print(f"  {C_DIM}──────────────────────────────────────────────────────{C_RESET}")

def format_time(seconds: float) -> str:
    """Format seconds ke string yang readable."""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    return f"{seconds:.1f}s"
