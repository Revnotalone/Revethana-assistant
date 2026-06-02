"""
voice.py - Voice Recognition Engine
Revethana Assistant

Menggunakan SpeechRecognition dengan Google Web Speech API.
Ringan dan cepat - optimal untuk Ryzen 5 3500U.
"""

import speech_recognition as sr
from typing import Optional
from utils import print_info, print_error


class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone  = None
        self._init_mic()
        self._calibrate()

    def _init_mic(self):
        """Inisialisasi microphone."""
        try:
            self.microphone = sr.Microphone()
            print_info("Microphone terdeteksi dan siap.")
        except OSError as e:
            print_error(f"Microphone tidak ditemukan: {e}")
            print_error("Pastikan microphone terhubung dan driver sudah terinstall.")
            raise

    def _calibrate(self):
        """Kalibrasi noise dari ambient sound."""
        try:
            with self.microphone as source:
                print_info("Kalibrasi ambient noise... (1 detik)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
            # Setting sensitivity
            self.recognizer.energy_threshold = max(300, self.recognizer.energy_threshold)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8   # Deteksi jeda bicara
            self.recognizer.non_speaking_duration = 0.5
            
            print_info(f"Kalibrasi selesai. Energy threshold: {self.recognizer.energy_threshold:.0f}")
        except Exception as e:
            print_error(f"Gagal kalibrasi: {e}")

    def listen(
        self,
        timeout: float = 8.0,
        phrase_limit: float = 12.0,
        language: str = "id-ID"
    ) -> Optional[str]:
        """
        Dengarkan input suara dari microphone.
        
        Args:
            timeout:      Waktu tunggu sebelum mulai mendengar (detik)
            phrase_limit: Maksimum durasi satu frasa (detik)
            language:     Language code untuk STT
        
        Returns:
            String teks hasil STT, atau None jika gagal
        """
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

            # Primary: Bahasa Indonesia
            text = self._recognize(audio, language="id-ID")
            
            # Fallback: English jika Indonesia gagal
            if not text:
                text = self._recognize(audio, language="en-US")
            
            return text.strip() if text else None

        except sr.WaitTimeoutError:
            # Tidak ada suara dalam timeout - normal, bukan error
            return None
        except Exception as e:
            print_error(f"Error saat listening: {e}")
            return None

    def _recognize(self, audio: sr.AudioData, language: str) -> Optional[str]:
        """Jalankan speech recognition."""
        try:
            text = self.recognizer.recognize_google(
                audio,
                language=language,
                show_all=False
            )
            return text
        except sr.UnknownValueError:
            # Suara tidak jelas / tidak bisa dikenali
            return None
        except sr.RequestError as e:
            print_error(f"Google STT error: {e}. Cek koneksi internet.")
            return None

    def listen_once(self) -> Optional[str]:
        """
        Shorthand untuk listen sekali dengan setting default.
        Digunakan untuk konfirmasi atau input singkat.
        """
        return self.listen(timeout=5.0, phrase_limit=6.0)

    def get_available_microphones(self) -> list:
        """List semua microphone yang tersedia."""
        return sr.Microphone.list_microphone_names()
