"""
system_control.py - Windows System & Desktop Controller
Revethana Assistant

Mengontrol aplikasi, file, browser, volume, screenshot, dan sistem Windows.
"""

import os
import subprocess
import webbrowser
import psutil
import pyautogui
import datetime
import platform
from typing import Optional, Tuple
from utils import print_info, print_error, print_success

# ─── Disable pyautogui failsafe warning ──────────────────────────
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# ─── App Registry ─────────────────────────────────────────────────
# Format: "keyword": [("executable_name", "common_path_1"), ...]
APP_REGISTRY = {
    "discord": [
        ("Discord", os.path.expanduser(r"~\AppData\Local\Discord\Update.exe"), "--processStart Discord.exe"),
        ("Discord.exe", None, None),
    ],
    "vscode": [
        ("code", None, None),
    ],
    "visual studio code": [
        ("code", None, None),
    ],
    "steam": [
        ("steam.exe", r"C:\Program Files (x86)\Steam\Steam.exe", None),
        ("steam", None, None),
    ],
    "spotify": [
        ("Spotify.exe", os.path.expanduser(r"~\AppData\Roaming\Spotify\Spotify.exe"), None),
        ("spotify", None, None),
    ],
    "minecraft": [
        ("MinecraftLauncher.exe", os.path.expanduser(r"~\AppData\Roaming\.minecraft\launcher\MinecraftLauncher.exe"), None),
        ("minecraft launcher", None, None),
    ],
    "calculator": [("calc", None, None)],
    "kalkulator":  [("calc", None, None)],
    "task manager": [("taskmgr", None, None)],
    "chrome": [
        ("chrome", None, None),
        ("google chrome", r"C:\Program Files\Google\Chrome\Application\chrome.exe", None),
        ("chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", None),
    ],
    "firefox": [("firefox", None, None)],
    "notepad": [("notepad", None, None)],
    "word":    [("winword", None, None)],
    "excel":   [("excel",   None, None)],
    "powerpoint": [("powerpnt", None, None)],
    "file explorer": [("explorer", None, None)],
    "explorer": [("explorer", None, None)],
    "cmd":     [("cmd",  None, None)],
    "terminal": [("wt", None, None)],  # Windows Terminal
    "powershell": [("powershell", None, None)],
    "paint":   [("mspaint", None, None)],
    "vlc":     [("vlc", None, None)],
    "obs":     [("obs64", None, None)],
    "telegram": [
        ("Telegram.exe", os.path.expanduser(r"~\AppData\Roaming\Telegram Desktop\Telegram.exe"), None),
    ],
    "whatsapp": [
        ("WhatsApp.exe", os.path.expanduser(r"~\AppData\Local\WhatsApp\WhatsApp.exe"), None),
    ],
}

# ─── Website Registry ─────────────────────────────────────────────
WEBSITE_REGISTRY = {
    "youtube":   "https://www.youtube.com",
    "google":    "https://www.google.com",
    "github":    "https://www.github.com",
    "chatgpt":   "https://chat.openai.com",
    "chat gpt":  "https://chat.openai.com",
    "gmail":     "https://mail.google.com",
    "instagram": "https://www.instagram.com",
    "twitter":   "https://www.twitter.com",
    "x":         "https://www.x.com",
    "facebook":  "https://www.facebook.com",
    "reddit":    "https://www.reddit.com",
    "netflix":   "https://www.netflix.com",
    "spotify":   "https://open.spotify.com",
    "discord":   "https://discord.com/app",
    "twitch":    "https://www.twitch.tv",
    "stackoverflow": "https://stackoverflow.com",
    "wikipedia": "https://www.wikipedia.org",
    "claude":    "https://claude.ai",
    "gemini":    "https://gemini.google.com",
    "linkedin":  "https://www.linkedin.com",
    "shopee":    "https://shopee.co.id",
    "tokopedia": "https://www.tokopedia.com",
    "gojek":     "https://www.gojek.com",
}

# ─── Folder Registry ──────────────────────────────────────────────
FOLDER_REGISTRY = {
    "download":   os.path.expanduser("~/Downloads"),
    "downloads":  os.path.expanduser("~/Downloads"),
    "dokumen":    os.path.expanduser("~/Documents"),
    "documents":  os.path.expanduser("~/Documents"),
    "document":   os.path.expanduser("~/Documents"),
    "desktop":    os.path.expanduser("~/Desktop"),
    "gambar":     os.path.expanduser("~/Pictures"),
    "pictures":   os.path.expanduser("~/Pictures"),
    "foto":       os.path.expanduser("~/Pictures"),
    "musik":      os.path.expanduser("~/Music"),
    "music":      os.path.expanduser("~/Music"),
    "video":      os.path.expanduser("~/Videos"),
    "videos":     os.path.expanduser("~/Videos"),
    "drive c":    "C:\\",
    "drive d":    "D:\\",
    "drive e":    "E:\\",
    "c":          "C:\\",
    "d":          "D:\\",
    "e":          "E:\\",
}


class SystemController:

    # ─── Application Control ──────────────────────────────────────

    def open_app(self, app_name: str) -> str:
        """Buka aplikasi berdasarkan nama."""
        app_key = app_name.lower().strip()
        
        # Cari di registry
        for key, variants in APP_REGISTRY.items():
            if key in app_key or app_key in key:
                result = self._try_launch_app(key, variants)
                if result:
                    return f"Oke, {key.title()} lagi dibuka."
        
        # Coba langsung via subprocess jika tidak ada di registry
        try:
            subprocess.Popen([app_key], shell=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            return f"Mencoba membuka {app_name}."
        except Exception:
            return f"Hmm, gak nemu {app_name}. Pastikan sudah terinstall ya."

    def _try_launch_app(self, app_name: str, variants: list) -> bool:
        """Coba berbagai cara untuk launch aplikasi."""
        for exe, path, args in variants:
            try:
                if path and os.path.exists(path):
                    # Launch dari path spesifik
                    cmd = [path]
                    if args:
                        cmd.extend(args.split())
                    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True
                else:
                    # Launch dari PATH / shell
                    cmd = exe
                    if args:
                        cmd = f"{exe} {args}"
                    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True
            except (FileNotFoundError, PermissionError, OSError):
                continue
        return False

    def close_app(self, app_name: str) -> str:
        """Tutup aplikasi berdasarkan nama."""
        app_key = app_name.lower().strip()
        killed = []

        # Map nama umum ke process name
        process_map = {
            "chrome": ["chrome.exe"],
            "discord": ["Discord.exe", "discord.exe"],
            "spotify": ["Spotify.exe", "spotify.exe"],
            "steam": ["steam.exe", "Steam.exe"],
            "vscode": ["Code.exe", "code.exe"],
            "firefox": ["firefox.exe"],
            "notepad": ["notepad.exe"],
            "word": ["WINWORD.EXE"],
            "excel": ["EXCEL.EXE"],
            "calculator": ["CalculatorApp.exe", "calc.exe"],
            "telegram": ["Telegram.exe"],
            "whatsapp": ["WhatsApp.exe"],
            "vlc": ["vlc.exe"],
            "obs": ["obs64.exe", "obs32.exe"],
        }

        targets = []
        for key, procs in process_map.items():
            if key in app_key or app_key in key:
                targets.extend(procs)
        
        if not targets:
            targets = [app_key, f"{app_key}.exe"]

        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] in targets or \
                   proc.info['name'].lower() in [t.lower() for t in targets]:
                    proc.kill()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed:
            return f"Oke, {app_name} sudah ditutup."
        return f"Gak nemu proses {app_name} yang aktif."

    # ─── Browser Control ──────────────────────────────────────────

    def open_website(self, site: str) -> str:
        """Buka website di browser default."""
        site_key = site.lower().strip()
        
        # Cek registry
        for key, url in WEBSITE_REGISTRY.items():
            if key in site_key:
                webbrowser.open(url)
                return f"Oke, {key.title()} udah dibuka."
        
        # Jika ada 'www' atau '.com' / '.id' dll - buka langsung
        if any(x in site_key for x in ["www.", ".com", ".id", ".net", ".org", ".io"]):
            url = site_key if site_key.startswith("http") else f"https://{site_key}"
            webbrowser.open(url)
            return f"Membuka {site}."
        
        # Fallback: Google search
        query = site.replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Gak nemu websitenya, jadi gue Google-in aja ya: '{site}'."

    def search_youtube(self, query: str) -> str:
        """Cari video di YouTube."""
        q = query.replace(" ", "+")
        webbrowser.open(f"https://www.youtube.com/results?search_query={q}")
        return f"Nyari '{query}' di YouTube."

    def search_google(self, query: str) -> str:
        """Cari sesuatu di Google."""
        q = query.replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={q}")
        return f"Googling '{query}'."

    # ─── File & Folder Control ────────────────────────────────────

    def open_folder(self, folder: str) -> str:
        """Buka folder di File Explorer."""
        folder_key = folder.lower().strip()
        
        # Cek registry
        for key, path in FOLDER_REGISTRY.items():
            if key in folder_key:
                if os.path.exists(path):
                    os.startfile(path)
                    return f"Membuka folder {key}."
                else:
                    return f"Folder {key} tidak ditemukan di path: {path}"
        
        # Coba sebagai path langsung
        if os.path.exists(folder):
            os.startfile(folder)
            return f"Membuka {folder}."
        
        # Buka Downloads sebagai default
        downloads = os.path.expanduser("~/Downloads")
        os.startfile(downloads)
        return f"Hmm, gak nemu folder '{folder}'. Dibuka Downloads aja."

    def open_last_screenshot(self) -> str:
        """Buka screenshot terakhir."""
        screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
        if not os.path.exists(screenshots_dir):
            screenshots_dir = os.path.expanduser("~/Desktop")
        
        try:
            files = [
                os.path.join(screenshots_dir, f)
                for f in os.listdir(screenshots_dir)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            ]
            if not files:
                return "Belum ada screenshot yang tersimpan."
            
            latest = max(files, key=os.path.getmtime)
            os.startfile(latest)
            return f"Membuka screenshot terakhir: {os.path.basename(latest)}"
        except Exception as e:
            return f"Gagal buka screenshot: {e}"

    # ─── System Info ──────────────────────────────────────────────

    def get_time(self) -> str:
        """Dapatkan waktu sekarang."""
        now = datetime.datetime.now()
        day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        month_names = [
            "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        day   = day_names[now.weekday()]
        month = month_names[now.month]
        return (
            f"Sekarang {day}, {now.day} {month} {now.year}, "
            f"jam {now.hour:02d}:{now.minute:02d}."
        )

    def get_battery(self) -> str:
        """Dapatkan status baterai laptop."""
        try:
            batt = psutil.sensors_battery()
            if batt is None:
                return "Perangkat ini kayaknya desktop, gak ada baterai."
            
            pct    = batt.percent
            status = "sedang dicharge" if batt.power_plugged else "tidak dicharge"
            
            if batt.power_plugged:
                msg = f"Baterai {pct:.0f}%, {status}."
            else:
                secs_left = batt.secsleft
                if secs_left != psutil.POWER_TIME_UNLIMITED and secs_left > 0:
                    hrs, mins = divmod(secs_left // 60, 60)
                    time_left = f", estimasi {hrs}j {mins}m lagi"
                else:
                    time_left = ""
                msg = f"Baterai {pct:.0f}%{time_left}, {status}."
            
            if pct <= 15 and not batt.power_plugged:
                msg += " Segera charge ya!"
            
            return msg
        except Exception as e:
            return f"Gagal cek baterai: {e}"

    def get_cpu_ram(self) -> str:
        """Dapatkan info CPU dan RAM."""
        cpu  = psutil.cpu_percent(interval=1)
        ram  = psutil.virtual_memory()
        used = ram.used / (1024 ** 3)
        total = ram.total / (1024 ** 3)
        return (
            f"CPU usage {cpu:.0f}%, "
            f"RAM {used:.1f}GB dari {total:.1f}GB "
            f"({ram.percent:.0f}% terpakai)."
        )

    # ─── Volume Control ───────────────────────────────────────────

    def volume_up(self, steps: int = 5) -> str:
        """Naikkan volume sistem."""
        for _ in range(steps):
            pyautogui.press("volumeup")
        return f"Volume dinaikkan."

    def volume_down(self, steps: int = 5) -> str:
        """Turunkan volume sistem."""
        for _ in range(steps):
            pyautogui.press("volumedown")
        return "Volume diturunkan."

    def volume_mute(self) -> str:
        """Toggle mute volume."""
        pyautogui.press("volumemute")
        return "Volume di-mute."

    # ─── Screen Control ───────────────────────────────────────────

    def take_screenshot(self) -> str:
        """Ambil screenshot layar."""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshots_dir = os.path.expanduser("~/Pictures/Screenshots")
            os.makedirs(screenshots_dir, exist_ok=True)
            
            filename = f"revethana_screenshot_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            return f"Screenshot tersimpan di Pictures/Screenshots/{filename}"
        except Exception as e:
            return f"Gagal screenshot: {e}"

    # ─── Power Management ─────────────────────────────────────────

    def shutdown(self, delay: int = 10) -> str:
        """Shutdown komputer dengan delay."""
        subprocess.run(f"shutdown /s /t {delay}", shell=True)
        return f"Komputer akan shutdown dalam {delay} detik. Bye!"

    def restart(self, delay: int = 10) -> str:
        """Restart komputer dengan delay."""
        subprocess.run(f"shutdown /r /t {delay}", shell=True)
        return f"Komputer akan restart dalam {delay} detik."

    def sleep(self) -> str:
        """Masukkan komputer ke mode sleep."""
        subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Komputer akan sleep sekarang. Sampai jumpa!"

    def cancel_shutdown(self) -> str:
        """Batalkan shutdown/restart yang terjadwal."""
        subprocess.run("shutdown /a", shell=True)
        return "Shutdown/restart dibatalkan."

    # ─── Process Info ─────────────────────────────────────────────

    def get_running_apps(self) -> str:
        """Dapatkan daftar aplikasi yang sedang berjalan."""
        known_apps = {
            "chrome.exe": "Google Chrome",
            "firefox.exe": "Firefox",
            "Discord.exe": "Discord",
            "Spotify.exe": "Spotify",
            "Code.exe": "VS Code",
            "steam.exe": "Steam",
            "notepad.exe": "Notepad",
            "explorer.exe": "File Explorer",
            "Telegram.exe": "Telegram",
        }
        
        running = []
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name in known_apps:
                    running.append(known_apps[name])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        running = list(set(running))
        if not running:
            return "Gak ada aplikasi yang dikenal lagi berjalan."
        return f"Aplikasi yang sedang jalan: {', '.join(running)}."
