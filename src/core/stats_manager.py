"""
Oyun İstatistikleri Yöneticisi (Stats Manager).
Oynanan maçları, süreleri, galibiyet/mağlubiyet oranlarını ve maç geçmişini JSON formatında saklar.
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class StatsManager:
    """Satranç istatistiklerini ve maç geçmişini yöneten sınıf."""

    def __init__(self, stats_file_path: str):
        self.stats_file_path = stats_file_path
        self.data: Dict[str, Any] = self._get_empty_stats()
        self.load()

    def _get_empty_stats(self) -> Dict[str, Any]:
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "total_play_time_seconds": 0.0,
            "total_moves_played": 0,
            "fastest_win_seconds": None,
            "matches": []
        }

    def load(self):
        """İstatistikleri diskten yükler."""
        if os.path.exists(self.stats_file_path):
            try:
                with open(self.stats_file_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"İstatistik dosyası okunamadı, sıfırlanıyor: {e}")
                self.data = self._get_empty_stats()
        else:
            self.data = self._get_empty_stats()

    def save(self):
        """İstatistikleri diske kaydeder."""
        os.makedirs(os.path.dirname(self.stats_file_path), exist_ok=True)
        with open(self.stats_file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def record_match(
        self,
        opponent_name: str,
        result: str,           # 'win', 'loss', 'draw'
        reason: str,           # 'Şah Mat', 'Terk', 'Zaman Aşımı', 'Pat', vb.
        duration_seconds: float,
        moves_count: int,
        player_color: str      # 'Beyaz' veya 'Siyah'
    ):
        """Yeni bir maç sonucunu istatistiklere ekler."""
        self.data["total_games"] += 1
        self.data["total_play_time_seconds"] += duration_seconds
        self.data["total_moves_played"] += moves_count

        if result == "win":
            self.data["wins"] += 1
            cur_fastest = self.data.get("fastest_win_seconds")
            if cur_fastest is None or duration_seconds < cur_fastest:
                self.data["fastest_win_seconds"] = round(duration_seconds, 1)
        elif result == "loss":
            self.data["losses"] += 1
        else:
            self.data["draws"] += 1

        match_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "opponent": opponent_name,
            "result": result,  # 'win', 'loss', 'draw'
            "reason": reason,
            "duration_seconds": round(duration_seconds, 1),
            "moves_count": moves_count,
            "player_color": player_color
        }

        # Son 100 maçı sakla
        matches = self.data.get("matches", [])
        matches.insert(0, match_entry)
        self.data["matches"] = matches[:100]

        self.save()

    def reset_stats(self):
        """Tüm istatistikleri sıfırlar."""
        self.data = self._get_empty_stats()
        self.save()

    @property
    def win_rate(self) -> float:
        """Kazanma yüzdesini döner."""
        total = self.data.get("total_games", 0)
        if total == 0:
            return 0.0
        return (self.data.get("wins", 0) / total) * 100.0

    @property
    def average_duration_seconds(self) -> float:
        """Ortalama maç süresini döner."""
        total = self.data.get("total_games", 0)
        if total == 0:
            return 0.0
        return self.data.get("total_play_time_seconds", 0.0) / total

    @staticmethod
    def format_duration(seconds: Optional[float]) -> str:
        """Saniyeyi okunabilir süre dizesine dönüştürür (ör: '12 dk 34 sn')."""
        if seconds is None or seconds <= 0:
            return "--"
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        if mins > 0:
            return f"{mins} dk {secs:02d} sn"
        return f"{secs} sn"
