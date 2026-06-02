"""
speak.py - Text-to-Speech Engine
Revethana Assistant

Menggunakan edge-tts (Microsoft Edge TTS) untuk suara natural.
Voice: id-ID-ArdiNeural (Indonesian male, natural dan modern).
"""

import asyncio
import os
import tempfile
import edge_tts
import pygame
from utils import print_error, print_status, clear_status

# ─── Voice Config ─────────────────────────────────────────────────
PRIMARY_VOICE  = "id-ID-ArdiNeural"    # Indonesian Male - natural dan modern
FALLBACK_VOICE = "en-US-GuyNeural"     # English fallback
SPEECH_RATE    = "+5%"                 # Sedikit lebih cepat dari default
SPEECH_VOLUME  = "+0%"


class Speaker:
    def __init__(self):
        self._init_pygame()
        self.voice = PRIMARY_VOICE

    def _init_pygame(self):
        """Inisialisasi pygame mixer untuk playback audio."""
        try:
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
            pygame.mixer.init()
        except Exception as e:
            print_error(f"Gagal init audio mixer: {e}")

    # ─── Core Speak ───────────────────────────────────────────────

    def speak(self, text: str):
        """
        Convert text ke suara dan mainkan.
        Blocking - tunggu sampai selesai berbicara.
        """
        if not text or not text.strip():
            return

        # Bersihkan teks dari karakter yang tidak perlu untuk TTS
        clean_text = self._clean_for_tts(text)

        try:
            print_status("SPEAKING...")
            # Jalankan async TTS generation
            asyncio.run(self._generate_and_play(clean_text))
        except RuntimeError:
            # Jika event loop sudah berjalan
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self._generate_and_play(clean_text))
            finally:
                loop.close()
        except Exception as e:
            print_error(f"TTS error: {e}")
        finally:
            clear_status()

    async def _generate_and_play(self, text: str):
        """Generate audio file dan mainkan."""
        tmp_path = None
        try:
            # Buat temp file
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".mp3", dir=tempfile.gettempdir()
            ) as tmp:
                tmp_path = tmp.name

            # Generate audio dengan edge-tts
            communicate = edge_tts.Communicate(
                text,
                voice=self.voice,
                rate=SPEECH_RATE,
                volume=SPEECH_VOLUME
            )
            await communicate.save(tmp_path)

            # Mainkan audio
            self._play_audio(tmp_path)

        except edge_tts.exceptions.NoAudioReceived:
            # Fallback ke English voice
            if self.voice != FALLBACK_VOICE:
                communicate = edge_tts.Communicate(
                    text, voice=FALLBACK_VOICE, rate=SPEECH_RATE
                )
                if tmp_path:
                    await communicate.save(tmp_path)
                    self._play_audio(tmp_path)
        finally:
            # Cleanup temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass

    def _play_audio(self, file_path: str):
        """Mainkan file audio menggunakan pygame."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            # Tunggu sampai selesai
            while pygame.mixer.music.get_busy():
                pygame.time.wait(50)
            pygame.mixer.music.unload()
        except Exception as e:
            print_error(f"Audio playback error: {e}")

    # ─── Text Cleaning ────────────────────────────────────────────

    def _clean_for_tts(self, text: str) -> str:
        """
        Bersihkan teks agar lebih natural saat diucapkan.
        Hapus karakter markdown dan simbol yang tidak perlu.
        """
        replacements = [
            ("**", ""), ("__", ""), ("##", ""), ("# ", ""),
            ("```", ""), ("`", ""), ("*", ""), ("_", " "),
            ("  ", " "), ("\n\n", ". "), ("\n", ". "),
            ("...", "…"), ("URL:", ""), ("http://", ""), ("https://", ""),
        ]
        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        return result.strip()

    # ─── Utility ──────────────────────────────────────────────────

    def set_voice(self, voice: str):
        """Ganti voice TTS."""
        self.voice = voice

    def stop(self):
        """Stop audio yang sedang diputar."""
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    async def get_available_voices(self) -> list:
        """Dapatkan list semua voice yang tersedia."""
        voices_gen = edge_tts.list_voices()
        voices = await voices_gen
        return [v for v in voices if "id-" in v["Name"].lower() or "en-" in v["Name"].lower()]
