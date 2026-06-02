"""
main.py - Revethana Assistant - Main Entry Point
AI Desktop Assistant powered by Gemini 2.5 Flash

Author: Revethana Project
Usage: python main.py
"""

import os
import sys
import time
import signal
import threading
from dotenv import load_dotenv

# Load environment variables dari .env
load_dotenv()

# Validasi API key sebelum import modul lain
if not os.getenv("GEMINI_API_KEY"):
    print("\n[ERROR] GEMINI_API_KEY tidak ditemukan!")
    print("Buat file .env dengan isi: GEMINI_API_KEY=api_key_kamu")
    print("Dapatkan API key gratis di: https://aistudio.google.com/app/apikey\n")
    sys.exit(1)

from utils import (
    print_banner, print_status, print_user, print_ai,
    print_error, print_info, print_success, print_divider,
    clear_status
)
from voice import VoiceRecognizer
from speak import Speaker
from commands import CommandProcessor
from ai import AIEngine
from memory import MemoryManager


def initialize_components():
    """Inisialisasi semua komponen assistant."""
    components = {}

    print_info("Memuat memory percakapan...")
    components["memory"] = MemoryManager()
    print_success(f"Memory siap. {components['memory'].get_summary()}")

    print_info("Menginisialisasi AI Engine (Gemini 2.5 Flash)...")
    try:
        components["ai"] = AIEngine(components["memory"])
        print_success("AI Engine siap.")
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    print_info("Menginisialisasi Text-to-Speech...")
    components["speaker"] = Speaker()
    print_success("Text-to-Speech siap (id-ID-ArdiNeural).")

    print_info("Menginisialisasi Voice Recognition...")
    try:
        components["voice"] = VoiceRecognizer()
        print_success("Voice Recognition siap.")
    except OSError:
        print_error("Microphone tidak ditemukan. Jalankan ulang setelah menghubungkan microphone.")
        sys.exit(1)

    print_info("Menyiapkan Command Processor...")
    components["commands"] = CommandProcessor(
        components["speaker"],
        components["ai"]
    )
    print_success("Command Processor siap.")

    return components


def main():
    """Main loop Revethana Assistant."""
    print_banner()

    # Inisialisasi
    try:
        comp = initialize_components()
    except Exception as e:
        print_error(f"Gagal inisialisasi: {e}")
        sys.exit(1)

    speaker  = comp["speaker"]
    voice    = comp["voice"]
    memory   = comp["memory"]
    commands = comp["commands"]

    print_divider()
    print()

    # Welcome message
    welcome = (
        "Hei! Gue Revethana, AI assistant lo. "
        "Gue bisa bantu buka aplikasi, website, kontrol volume, "
        "kasih info sistem, atau ngobrol soal apapun. "
        "Mau ngapain sekarang?"
    )
    print_ai(welcome, typing=False)
    speaker.speak(welcome)

    # ── Signal handler untuk graceful exit ─────────────────────
    running = {"active": True}

    def handle_exit(sig, frame):
        running["active"] = False

    signal.signal(signal.SIGINT, handle_exit)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, handle_exit)

    # ── Consecutive error counter ───────────────────────────────
    error_count = 0
    MAX_ERRORS  = 5

    # ── Main Loop ───────────────────────────────────────────────
    print_info("Loop utama dimulai. Tekan Ctrl+C untuk berhenti.\n")

    while running["active"]:
        try:
            # Show listening indicator
            print_status("LISTENING...")

            # Dengarkan input suara
            text = voice.listen(timeout=8.0, phrase_limit=15.0)

            # Tidak ada input - lanjutkan loop
            if not text:
                clear_status()
                continue

            clear_status()
            error_count = 0  # Reset error counter

            # Print input user
            print_user(text)

            # ── Exit Commands ─────────────────────────────────
            text_lower = text.lower().strip()
            exit_triggers = [
                "exit", "quit", "bye", "goodbye",
                "matikan assistant", "tutup assistant",
                "stop revethana", "bye revethana",
                "selamat tinggal", "sampai jumpa revethana",
                "gak usah nyala lagi", "tidur dulu",
            ]
            if any(trigger in text_lower for trigger in exit_triggers):
                farewell = "Oke, gue istirahat dulu. Sampai jumpa!"
                print_ai(farewell, typing=False)
                speaker.speak(farewell)
                break

            # ── Memory Clear Command ──────────────────────────
            if any(kw in text_lower for kw in [
                "hapus ingatan", "clear memory", "lupa semua",
                "reset memory", "hapus percakapan"
            ]):
                memory.clear()
                response = "Oke, ingatan gue udah dihapus. Fresh start!"
                print_ai(response)
                speaker.speak(response)
                continue

            # ── Help Command ──────────────────────────────────
            if any(kw in text_lower for kw in [
                "help", "bantuan", "apa yang bisa", "bisa ngapain",
                "fitur apa", "kemampuan", "contoh perintah",
            ]):
                response = (
                    "Gue bisa: buka aplikasi seperti Discord, Spotify, VSCode. "
                    "Buka website YouTube, GitHub, Google. "
                    "Cari video di YouTube. "
                    "Kontrol volume, screenshot, cek baterai dan jam. "
                    "Shutdown, restart, atau sleep komputer. "
                    "Dan ngobrol soal apapun lewat AI!"
                )
                print_ai(response)
                speaker.speak(response)
                continue

            # ── Process Command ───────────────────────────────
            print_status("THINKING...")
            start_time = time.time()

            response = commands.process(text)

            elapsed = time.time() - start_time
            clear_status()

            if not response:
                response = "Maaf, gue gak bisa proses itu. Coba lagi?"

            # Print dan ucapkan response
            print_ai(response)
            speaker.speak(response)

            # Simpan ke memory
            memory.add_conversation(text, response)

        except KeyboardInterrupt:
            running["active"] = False
            break

        except Exception as e:
            error_count += 1
            clear_status()
            err_msg = f"Ada error: {str(e)[:100]}"
            print_error(err_msg)

            if error_count >= MAX_ERRORS:
                print_error(
                    f"Terlalu banyak error berturut-turut ({MAX_ERRORS}x). "
                    "Mungkin ada masalah dengan microphone atau koneksi."
                )
                error_count = 0  # Reset dan lanjutkan
            
            time.sleep(0.5)
            continue

    # ── Cleanup ─────────────────────────────────────────────────
    print()
    print_divider()
    print_info("Revethana Assistant dimatikan. Sampai jumpa!")
    print_divider()


if __name__ == "__main__":
    main()
