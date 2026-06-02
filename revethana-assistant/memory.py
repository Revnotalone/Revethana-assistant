"""
memory.py - Conversation Memory Manager
Revethana Assistant
"""

import json
import os
from datetime import datetime
from typing import List, Dict

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "memory.json")
MAX_HISTORY  = 20   # Simpan maksimal 20 percakapan terakhir
MAX_CONTEXT  = 8    # Kirim 8 terakhir ke AI sebagai context


class MemoryManager:
    def __init__(self):
        self.conversations: List[Dict] = []
        self.load()

    # ─── Persistence ─────────────────────────────────────────────

    def load(self):
        """Load memory dari file JSON."""
        try:
            if os.path.exists(MEMORY_FILE):
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.conversations = data.get("conversations", [])
        except Exception:
            self.conversations = []

    def save(self):
        """Simpan memory ke file JSON."""
        try:
            data = {
                "last_updated": datetime.now().isoformat(),
                "conversations": self.conversations[-MAX_HISTORY:]
            }
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # ─── Memory Operations ────────────────────────────────────────

    def add_conversation(self, user_text: str, assistant_text: str):
        """Tambahkan percakapan baru ke memory."""
        self.conversations.append({
            "timestamp": datetime.now().isoformat(),
            "user": user_text,
            "assistant": assistant_text
        })
        # Trim jika melebihi batas
        if len(self.conversations) > MAX_HISTORY:
            self.conversations = self.conversations[-MAX_HISTORY:]
        self.save()

    def get_context(self) -> List[Dict]:
        """
        Ambil recent conversations untuk context AI.
        Return format yang kompatibel dengan Gemini history.
        """
        recent = self.conversations[-MAX_CONTEXT:]
        history = []
        for conv in recent:
            history.append({
                "role": "user",
                "parts": [{"text": conv["user"]}]
            })
            history.append({
                "role": "model",
                "parts": [{"text": conv["assistant"]}]
            })
        return history

    def clear(self):
        """Hapus semua memory."""
        self.conversations = []
        self.save()

    def get_summary(self) -> str:
        """Ringkasan memory untuk display."""
        count = len(self.conversations)
        if count == 0:
            return "Belum ada percakapan."
        last = self.conversations[-1]
        last_time = last.get("timestamp", "")[:16].replace("T", " ")
        return f"{count} percakapan tersimpan. Terakhir: {last_time}"
