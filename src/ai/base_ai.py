"""
Tüm Yapay Zeka modellerinin miras aldığı temel soyut sınıf ve veri yapıları.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
import chess

@dataclass
class AIMoveResult:
    """Yapay zekanın ürettiği hamle sonucu ve ek bilgiler."""
    move_uci: str
    move_san: str
    eval_score: Optional[float] = None  # Piyon cinsinden pozitif = Beyaz üstün, negatif = Siyah üstün
    mate_in: Optional[int] = None      # Kaç hamlede mat (varsa)
    thoughts: str = ""                 # LLM veya motor düşünceleri / açıklaması
    time_spent: float = 0.0            # Hesaplama süresi (saniye)

class BaseAI(ABC):
    """Yapay Zeka temel sınıfı."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.id = config.get("id", "custom_ai")
        self.name = config.get("name", "Yapay Zeka")
        self.type = config.get("type", "builtin")

    @abstractmethod
    def get_move(self, board: chess.Board, move_history: List[str]) -> AIMoveResult:
        """
        Verilen tahta durumuna göre en iyi hamleyi hesaplar ve döner.
        
        :param board: Mevcut chess.Board nesnesi.
        :param move_history: Şimdiye kadar yapılan hamlelerin SAN listesi.
        :return: AIMoveResult nesnesi.
        """
        pass

    def test_connection(self) -> Tuple[bool, str]:
        """Modelin veya motorun erişilebilir olup olmadığını test eder."""
        return True, "Bağlantı başarılı."

    def cleanup(self):
        """Kaynakları serbest bırakma (ör. motor alt sürecini kapatma)."""
        pass
