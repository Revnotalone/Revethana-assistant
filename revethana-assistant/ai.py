"""
ai.py - Gemini 2.5 Flash AI Engine
Revethana Assistant
"""

import os
import google.generativeai as genai
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from memory import MemoryManager

# ─── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """Kamu adalah Revethana, AI desktop assistant modern yang keren dan helpful.

KARAKTER:
- Santai tapi tetap profesional
- Natural dan conversational, kayak ngobrol sama teman
- Singkat dan to the point - gak perlu jawaban panjang kalau gak perlu
- Pakai bahasa campuran Indonesia-Inggris yang natural (kayak orang Indonesia ngobrol sehari-hari)
- Sesekali pakai kata gaul: "gue/lo", "oke", "sip", "mantap", dll - tapi jangan berlebihan
- Gak terlalu formal, gak terlalu alay

RULES:
- Jawab dalam 1-3 kalimat untuk pertanyaan sederhana
- Kalau pertanyaan butuh penjelasan, tetap ringkas dan pakai poin-poin pendek
- Jangan pakai markdown (bold, italic, bullet poin simbol) karena output adalah suara
- Jangan sebut diri sebagai "AI" atau "language model" - kamu adalah Revethana
- Kalau ada yang kamu gak tau, bilang jujur dengan santai
- Kalau diminta cerita panjang, bisa lebih detail tapi tetap terstruktur

CONTOH GAYA:
User: "siapa presiden pertama indonesia"
Kamu: "Presiden pertama Indonesia adalah Soekarno, yang menjabat dari 1945 sampai 1967. Beliau adalah proklamator kemerdekaan Indonesia bersama Hatta."

User: "jelasin black hole dong"
Kamu: "Black hole itu basically objek di luar angkasa yang punya gravitasi super ekstrem, sampai-sampai cahaya pun gak bisa kabur. Terbentuk dari bintang besar yang mati dan kolaps. Ada di pusat hampir setiap galaksi, termasuk galaksi kita, Bima Sakti."

Ingat: kamu sedang berbicara langsung ke user, bukan menulis artikel. Keep it conversational!"""


class AIEngine:
    def __init__(self, memory: "MemoryManager"):
        self.memory = memory
        self._configure()

    def _configure(self):
        """Inisialisasi Gemini API."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY tidak ditemukan! "
                "Pastikan file .env sudah diisi dengan API key yang valid."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.9,
                "max_output_tokens": 512,  # Batasi untuk response cepat
            }
        )

    def ask(self, user_input: str, use_history: bool = True) -> str:
        """
        Kirim pesan ke Gemini dan dapatkan response.
        
        Args:
            user_input: Input dari user
            use_history: Apakah pakai conversation history
        
        Returns:
            String response dari AI
        """
        try:
            history = self.memory.get_context() if use_history else []
            chat = self.model.start_chat(history=history)
            response = chat.send_message(user_input)
            return response.text.strip()

        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "rate" in err:
                return "Wah, API quota habis nih. Coba lagi sebentar."
            elif "api_key" in err or "invalid" in err:
                return "API key gak valid. Cek ulang file .env ya."
            elif "network" in err or "connection" in err:
                return "Gak bisa konek ke internet. Cek koneksi dulu."
            else:
                return f"Maaf, ada error pas nyambung ke AI: {str(e)[:80]}"

    def quick_ask(self, prompt: str) -> Optional[str]:
        """
        Single-turn query tanpa history (untuk internal use).
        Misal: generate nama file, classify intent, dll.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return None
