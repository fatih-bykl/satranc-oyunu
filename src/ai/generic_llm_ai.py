"""
OpenAI & OpenAI-Uyumlu (DeepSeek, Groq, OpenRouter, yerel vLLM vb.) API Entegrasyonu.
"""
import os
import json
import time
import re
from typing import List, Dict, Any, Tuple, Optional
import chess
import requests
from .base_ai import BaseAI, AIMoveResult

class GenericLLMAI(BaseAI):
    """OpenAI standart API'si ile çalışan yapay zeka adaptörü."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        self.api_key = config.get("api_key", "").strip() or os.getenv("OPENAI_API_KEY", "")
        self.model_name = config.get("model_name", "gpt-4o-mini")
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
UCI: {", ".join(legal_uci_moves)}
SAN: {", ".join(legal_san_moves)}

GÖREV:
1. Sadece yukarıdaki YASAL HAMLELER listesinden en iyi hamleyi seç.
2. Karakterine uygun, 1-2 cümlelik kısa bir düşünce/yorum (Türkçe) yaz.

AŞAĞIDAKİ JSON FORMATINDA CEVAP VER:
```json
{{
  "move": "{legal_uci_moves[0]}",
  "thoughts": "Pozisyon hakkındaki yorumun"
}}
```
"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "Sen yalnızca belirtilen JSON formatında cevap veren profesyonel bir satranç motorusun."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=25)
            resp.raise_for_status()
            data = resp.json()
            choices = data.get("choices", [])
            response_text = choices[0].get("message", {}).get("content", "") if choices else ""
        except Exception as e:
            elapsed = time.time() - start_time
            fallback = list(board.legal_moves)[0]
            return AIMoveResult(
                move_uci=fallback.uci(),
                move_san=board.san(fallback),
                thoughts=f"LLM API Hatası ({str(e)}). Güvenli hamle oynandı.",
                time_spent=elapsed
            )

        elapsed = time.time() - start_time
        parsed_move, thoughts = self._parse_response(response_text, board)

        if parsed_move:
            san_move = board.san(parsed_move)
            return AIMoveResult(
                move_uci=parsed_move.uci(),
                move_san=san_move,
                thoughts=thoughts or f"LLM ({self.model_name}) hamlesini yaptı.",
                time_spent=elapsed
            )
        else:
            fallback = list(board.legal_moves)[0]
            return AIMoveResult(
                move_uci=fallback.uci(),
                move_san=board.san(fallback),
                thoughts=f"LLM yanıtı çözümlenemedi ({thoughts}). Güvenli hamle oynandı.",
                time_spent=elapsed
            )

    def _parse_response(self, text: str, board: chess.Board) -> Tuple[Optional[chess.Move], str]:
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                move_str = data.get("move", "").strip()
                thoughts = data.get("thoughts", "").strip()
                
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

        for move in board.legal_moves:
            if move.uci() in text:
                return move, text[:150]

        return None, "Yasal hamle bulunamadı."

    def test_connection(self) -> Tuple[bool, str]:
        try:
            url = f"{self.base_url}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return True, f"API Uç Noktasına ({self.base_url}) başarıyla bağlandı!"
            return False, f"API Yanıtı: HTTP {resp.status_code} - {resp.text[:150]}"
        except Exception as e:
            return False, f"Bağlantı hatası: {str(e)}"
