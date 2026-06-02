"""
commands.py - Natural Language Command Detector & Processor
Revethana Assistant

Mendeteksi perintah dari input natural bahasa Indonesia/Inggris.
Flexible parser yang mengenali berbagai variasi phrasing.
"""

import re
from typing import Optional, Tuple, TYPE_CHECKING
from system_control import SystemController

if TYPE_CHECKING:
    from speak import Speaker
    from ai import AIEngine


# ─── Intent Patterns ──────────────────────────────────────────────

# Kata-kata yang sering menjadi prefix dan bisa diabaikan
NOISE_PREFIXES = [
    "tolong ", "coba ", "minta ", "bisa ", "kamu ", "bang ", "mas ",
    "please ", "can you ", "could you ", "hey ", "hei ", "ok ",
    "bro ", "sis ", "oi ", "yo ", "dong ", "deh ",
]

NOISE_SUFFIXES = [
    " dong", " deh", " ya", " ga", " gak", " yuk", " dong ya",
    " please", " ya ga", " ya gak", " kan", " nih", " sih",
]

# ─── Command Keywords ─────────────────────────────────────────────

OPEN_KEYWORDS = [
    "buka", "bukain", "open", "jalanin", "jalankan", "start",
    "launch", "nyalain", "aktifin", "coba buka", "coba jalanin",
]

CLOSE_KEYWORDS = [
    "tutup", "tutupkan", "close", "kill", "matiin", "matikan",
    "hentikan", "stop", "nonaktifkan",
]

SEARCH_YOUTUBE_KEYWORDS = [
    "cari di youtube", "cariin di youtube", "cari video",
    "search youtube", "putar", "putar lagu", "putar video",
    "nyari di youtube", "lihat di youtube",
]

SEARCH_GOOGLE_KEYWORDS = [
    "cari di google", "cariin di google", "googling",
    "google", "search", "cari info", "cari tentang",
]

FOLDER_KEYWORDS = [
    "buka folder", "bukain folder", "open folder", "buka directory",
    "buka file explorer", "buka drive",
]

SCREENSHOT_KEYWORDS = [
    "screenshot", "screenshoot", "screen shot", "tangkap layar",
    "ambil screenshot", "foto layar", "capture screen",
]

TIME_KEYWORDS = [
    "jam berapa", "jam sekarang", "pukul berapa", "waktu sekarang",
    "what time", "sekarang jam", "tanggal berapa", "hari ini",
]

BATTERY_KEYWORDS = [
    "battery", "baterai", "charge", "daya", "sisa baterai",
    "berapa persen baterai", "battery laptop", "daya laptop",
]

VOLUME_UP_KEYWORDS = [
    "volume naik", "naikkan volume", "tambah volume", "kerasin",
    "volume up", "louder", "volume tinggi", "keraskan suara",
    "naikan suara",
]

VOLUME_DOWN_KEYWORDS = [
    "volume turun", "turunkan volume", "kurangi volume", "pelanin",
    "volume down", "quieter", "volume rendah", "pelankan suara",
    "kecilkan volume", "turunin volume",
]

MUTE_KEYWORDS = [
    "mute", "bisukan", "diamkan", "matiin suara", "silent",
    "no sound", "mute suara", "hening",
]

SHUTDOWN_KEYWORDS = [
    "shutdown", "matikan komputer", "matikan laptop", "turn off",
    "shut down", "matiin laptop", "matiin komputer", "padamkan",
]

RESTART_KEYWORDS = [
    "restart", "reboot", "restart komputer", "restart laptop",
    "nyalain ulang", "hidupkan ulang",
]

SLEEP_KEYWORDS = [
    "sleep", "tidur", "sleep komputer", "mode tidur",
    "suspend", "hibernate", "istirahat komputer",
]

CPU_RAM_KEYWORDS = [
    "cpu", "ram", "memory", "performa", "performance", "stat sistem",
    "sistem info", "cpu usage", "ram usage", "berapa cpu", "berapa ram",
]

RUNNING_APPS_KEYWORDS = [
    "aplikasi aktif", "aplikasi yang jalan", "running apps",
    "apa yang lagi buka", "lagi buka apa",
]

SCREENSHOT_LAST_KEYWORDS = [
    "screenshot terakhir", "lihat screenshot", "buka screenshot",
    "last screenshot", "foto layar terakhir",
]

MEMORY_KEYWORDS = [
    "ingat", "memory", "riwayat percakapan", "hapus ingatan",
    "clear memory", "lupa semua",
]


class CommandProcessor:
    def __init__(self, speaker: "Speaker", ai_engine: "AIEngine"):
        self.speaker    = speaker
        self.ai_engine  = ai_engine
        self.sys_ctrl   = SystemController()

    # ─── Main Entry ───────────────────────────────────────────────

    def process(self, text: str) -> str:
        """
        Proses input teks - detect command atau fallback ke AI.
        
        Returns:
            String response yang siap diucapkan.
        """
        cleaned = self._clean_input(text)
        original_lower = text.lower().strip()

        # ── System Commands ──────────────────────────────────────

        # Waktu & tanggal
        if self._match_any(original_lower, TIME_KEYWORDS):
            return self.sys_ctrl.get_time()

        # Baterai
        if self._match_any(original_lower, BATTERY_KEYWORDS):
            return self.sys_ctrl.get_battery()

        # CPU & RAM
        if self._match_any(original_lower, CPU_RAM_KEYWORDS):
            return self.sys_ctrl.get_cpu_ram()

        # Screenshot
        if self._match_any(original_lower, SCREENSHOT_KEYWORDS) and \
           not self._match_any(original_lower, ["buka", "lihat", "terakhir", "last"]):
            return self.sys_ctrl.take_screenshot()

        # Screenshot terakhir
        if self._match_any(original_lower, SCREENSHOT_LAST_KEYWORDS):
            return self.sys_ctrl.open_last_screenshot()

        # Volume up
        if self._match_any(original_lower, VOLUME_UP_KEYWORDS):
            return self.sys_ctrl.volume_up()

        # Volume down
        if self._match_any(original_lower, VOLUME_DOWN_KEYWORDS):
            return self.sys_ctrl.volume_down()

        # Mute
        if self._match_any(original_lower, MUTE_KEYWORDS):
            return self.sys_ctrl.volume_mute()

        # Shutdown
        if self._match_any(original_lower, SHUTDOWN_KEYWORDS):
            return self.sys_ctrl.shutdown()

        # Restart
        if self._match_any(original_lower, RESTART_KEYWORDS):
            return self.sys_ctrl.restart()

        # Sleep
        if self._match_any(original_lower, SLEEP_KEYWORDS):
            return self.sys_ctrl.sleep()

        # Aplikasi aktif
        if self._match_any(original_lower, RUNNING_APPS_KEYWORDS):
            return self.sys_ctrl.get_running_apps()

        # ── Open Folder ──────────────────────────────────────────
        for kw in FOLDER_KEYWORDS:
            if kw in original_lower:
                target = original_lower.replace(kw, "").strip()
                if target:
                    return self.sys_ctrl.open_folder(target)
                return self.sys_ctrl.open_folder("downloads")

        # Buka drive langsung (drive d, drive c, dll)
        drive_match = re.search(r'buka\s+drive\s+([a-e])', original_lower)
        if drive_match:
            return self.sys_ctrl.open_folder(f"drive {drive_match.group(1)}")

        # ── Search YouTube ────────────────────────────────────────
        for kw in SEARCH_YOUTUBE_KEYWORDS:
            if kw in original_lower:
                query = original_lower
                for remove in [kw, "tolong", "coba", "minta", "dong", "deh", "ya"]:
                    query = query.replace(remove, "").strip()
                if query:
                    return self.sys_ctrl.search_youtube(query)

        # Pattern: "cari [query] di youtube"
        yt_pattern = re.search(
            r'(?:cari|cariin|search|nyari)\s+(.+?)\s+(?:di\s+)?(?:youtube|yt)',
            original_lower
        )
        if yt_pattern:
            return self.sys_ctrl.search_youtube(yt_pattern.group(1).strip())

        # ── Search Google ─────────────────────────────────────────
        google_pattern = re.search(
            r'(?:cari|cariin|search|googling)\s+(.+?)\s+(?:di\s+)?google',
            original_lower
        )
        if google_pattern:
            return self.sys_ctrl.search_google(google_pattern.group(1).strip())

        # ── Close App ─────────────────────────────────────────────
        for kw in CLOSE_KEYWORDS:
            if original_lower.startswith(kw + " ") or f" {kw} " in original_lower:
                target = self._extract_target(original_lower, [kw])
                if target:
                    return self.sys_ctrl.close_app(target)

        # ── Open App / Website ────────────────────────────────────
        open_target = self._extract_open_target(cleaned, original_lower)
        if open_target:
            return self._handle_open(open_target)

        # ── Fallback ke AI ────────────────────────────────────────
        return self.ai_engine.ask(text)

    # ─── Open Handler ─────────────────────────────────────────────

    def _handle_open(self, target: str) -> str:
        """
        Tentukan apakah target adalah website atau aplikasi,
        lalu buka yang sesuai.
        """
        from system_control import WEBSITE_REGISTRY, APP_REGISTRY

        target_lower = target.lower().strip()

        # Cek apakah website
        for key in WEBSITE_REGISTRY:
            if key in target_lower:
                return self.sys_ctrl.open_website(target_lower)

        # Cek apakah ada dot (domain) → website
        if "." in target_lower and " " not in target_lower:
            return self.sys_ctrl.open_website(target_lower)

        # Cek apakah app
        for key in APP_REGISTRY:
            if key in target_lower or target_lower in key:
                return self.sys_ctrl.open_app(target_lower)

        # Ambiguous: coba buka sebagai app dulu, fallback ke website
        try:
            return self.sys_ctrl.open_app(target_lower)
        except Exception:
            return self.sys_ctrl.open_website(target_lower)

    # ─── Helpers ──────────────────────────────────────────────────

    def _clean_input(self, text: str) -> str:
        """Bersihkan input dari noise prefixes dan suffixes."""
        result = text.lower().strip()
        
        for prefix in NOISE_PREFIXES:
            if result.startswith(prefix):
                result = result[len(prefix):].strip()
                break  # Hapus satu prefix saja
        
        for suffix in NOISE_SUFFIXES:
            if result.endswith(suffix):
                result = result[:-len(suffix)].strip()
                break
        
        return result

    def _match_any(self, text: str, keywords: list) -> bool:
        """Cek apakah text mengandung salah satu keyword."""
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords)

    def _extract_target(self, text: str, keywords: list) -> Optional[str]:
        """Ekstrak target setelah keyword."""
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                idx = text_lower.index(kw)
                target = text_lower[idx + len(kw):].strip()
                # Bersihkan suffix noise
                for suffix in NOISE_SUFFIXES:
                    target = target.rstrip(suffix).strip()
                if target:
                    return target
        return None

    def _extract_open_target(self, cleaned: str, original: str) -> Optional[str]:
        """
        Ekstrak target dari perintah 'buka/open/jalanin [target]'.
        Mendukung berbagai variasi phrasing.
        """
        # Coba dari cleaned text
        for kw in OPEN_KEYWORDS:
            if cleaned.startswith(kw + " "):
                return cleaned[len(kw):].strip()

        # Coba dari original (dengan noise)
        for kw in OPEN_KEYWORDS:
            if kw in original.lower():
                idx = original.lower().index(kw)
                after = original[idx + len(kw):].strip()
                if after:
                    # Bersihkan suffix
                    for suffix in NOISE_SUFFIXES:
                        if after.lower().endswith(suffix):
                            after = after[:-len(suffix)].strip()
                    return after

        # Pattern lanjut: "youtube dong", "discordnya", dll
        # Jika kata pertama adalah nama app/website yang dikenal
        from system_control import WEBSITE_REGISTRY, APP_REGISTRY
        first_word = cleaned.split()[0] if cleaned.split() else ""
        all_known  = list(WEBSITE_REGISTRY.keys()) + list(APP_REGISTRY.keys())
        if first_word in all_known:
            return first_word

        return None
