"""
Google Gemini API Entegrasyonu.
Gemini modellerine FEN, PGN ve yasal hamleleri besleyerek persona destekli satranç oynamasını sağlar.
"""
import os
import json
import time
import re
from typing import List, Dict, Any, Tuple, Optional
import chess
import requests
from .base_ai import BaseAI, AIMoveResult

class GeminiAI(BaseAI):
    """Google Gemini API ile satranç oynayan yapay zeka sınıfı."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key", "").strip() or os.getenv("GEMINI_API_KEY", "")
        self.model_name = config.get("model_name", "gemini-2.5-flash")
        self.persona = config.get("persona", "Sen yetenekli bir satranç ustasısın. Rakibine karşı hem zekice oyna hem de kısa esprili yorumlar yap.")

    def get_move(self, board: chess.Board, move_history: List[str]) -> AIMoveResult:
        start_time = time.time()
        
        legal_uci_moves = [m.uci() for m in board.legal_moves]
        legal_san_moves = [board.san(m) for m in board.legal_moves]
        turn_str = "Beyaz" if board.turn == chess.WHITE else "Siyah"

        prompt = f"""
Sen bir satranç yapay zekasısın. Kişiliğin: {self.persona}

Mevcut Satranç Durumu:
- Sıra: {turn_str}
- Tahta FEN: {board.fen()}
- Son Hamleler (PGN): {" ".join(move_history[-10:]) if move_history else "Oyunun başı"}
- YAPABİLECEĞİN YASAL HAMLELER LİSTESİ:
UCI formatında: {", ".join(legal_uci_moves)}
SAN formatında: {", ".join(legal_san_moves)}

GÖREV:
1. Sadece yukarıdaki YASAL HAMLELER listesinden en iyi hamleyi seç.
2. Karakterine uygun, 1-2 cümlelik kısa bir düşünce/yorum (Türkçe) yaz.

AŞAĞIDAKİ JSON FORMATINDA CEVAP VER:
```json
{{
  "move": "seçtiğin_uci_hamlesi_örneğin_{legal_uci_moves[0]}",
  "thoughts": "Pozisyon hakkındaki yorumun"
}}
```
"""
        response_text = self._call_gemini_api(prompt)
        elapsed = time.time() - start_time

        parsed_move, thoughts = self._parse_response(response_text, board)
        
        if parsed_move:
            san_move = board.san(parsed_move)
            return AIMoveResult(
                move_uci=parsed_move.uci(),
                move_san=san_move,
                thoughts=thoughts or f"Gemini ({self.model_name}) hamlesini yaptı.",
                time_spent=elapsed
            )
        else:
            # Fallback to first legal move
            fallback = list(board.legal_moves)[0]
            return AIMoveResult(
                move_uci=fallback.uci(),
                move_san=board.san(fallback),
                thoughts=f"Gemini yanıtı çözümlenemedi ({thoughts}). Güvenli hamle oynandı.",
                time_spent=elapsed
            )

    def _call_gemini_api(self, prompt: str) -> str:
        """Gemini REST API'sini çağırır."""
        if not self.api_key:
            raise ValueError("Gemini API Anahtarı (API Key) girilmemiş. Lütfen AI Ayarları penceresinden ekleyin.")

        # Gemini v1beta REST endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code != 200:
                # responseMimeType desteklenmeyen eski modeller için fallback
                payload["generationConfig"].pop("responseMimeType", None)
                resp = requests.post(url, headers=headers, json=payload, timeout=20)

            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""
        except Exception as e:
            raise RuntimeError(f"Gemini API Çağrı Hatası: {str(e)}")

    def _parse_response(self, text: str, board: chess.Board) -> Tuple[Optional[chess.Move], str]:
        """JSON veya metin cevabından yasal hamleyi ayıklar."""
        move_candidate = None
        thoughts = ""

        # JSON bloğunu bul
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                move_str = data.get("move", "").strip()
                thoughts = data.get("thoughts", "").strip()
                
                # UCI veya SAN olarak dene
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in board.legal_moves:
                        return move, thoughts
                except Exception:
                    pass

                try:
                    move = board.parse_san(move_str)
                    if move in board.legal_moves:
                        return move, thoughts
                except Exception:
                    pass
            except Exception:
                pass

        # Yedek Regex Arama
        for move in board.legal_moves:
            if move.uci() in text:
                return move, text[:150]
            try:
                san = board.san(move)
                if re.search(r'\b' + re.escape(san) + r'\b', text):
                    return move, text[:150]
            except Exception:
                pass

        return None, "Yasal hamle metinden tespit edilemedi."

    def test_connection(self) -> Tuple[bool, str]:
        if not self.api_key:
            return False, "API Anahtarı boş olamaz."
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}?key={self.api_key}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return True, f"Google Gemini API ({self.model_name}) başarıyla doğrulandı!"
            else:
                return False, f"API Hatası (Kod: {resp.status_code}): {resp.text[:200]}"
        except Exception as e:
            return False, f"Bağlantı Hatası: {str(e)}"
