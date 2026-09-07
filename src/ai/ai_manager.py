"""
Yapay Zeka Yöneticisi ve Arka Plan Hesaplama İş Parçacığı.
Kullanıcı arayüzünün donmaması için AI hesaplamalarını QThread içinde yürütür.
Zaman aşımı koruması (Watchdog Timer) ve hata durumunda otomatik yedek hamle (Fallback Move) içerir.
Oyunun kilitlenmesini %100 engeller.
"""
import os
import json
import random
from typing import Dict, List, Any, Optional
import chess
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal

from .base_ai import BaseAI, AIMoveResult
from .heuristic_ai import HeuristicAI
from .uci_ai import UCIAI
from .gemini_ai import GeminiAI
from .ollama_ai import OllamaAI
from .generic_llm_ai import GenericLLMAI

class AICalculationWorker(QThread):
    """Arka planda AI hesaplaması yapan iş parçacığı."""
    move_ready = pyqtSignal(object)  # AIMoveResult
    error_occurred = pyqtSignal(str)

    def __init__(self, ai_instance: BaseAI, board_copy: chess.Board, move_history: List[str]):
        super().__init__()
        self.ai_instance = ai_instance
        self.board_copy = board_copy
        self.move_history = move_history
        self._is_aborted = False

    def abort(self):
        self._is_aborted = True

    def run(self):
        try:
            result = self.ai_instance.get_move(self.board_copy, self.move_history)
            if not self._is_aborted:
                self.move_ready.emit(result)
        except Exception as e:
            if not self._is_aborted:
                self.error_occurred.emit(str(e))

class AIManager(QObject):
    """Tüm AI modellerini yöneten merkezi sınıf."""
    
    calculation_started = pyqtSignal(str)  # model_name
    move_ready = pyqtSignal(object)        # AIMoveResult
    calculation_failed = pyqtSignal(str)   # error_msg
    models_updated = pyqtSignal()

    def __init__(self, config_path: str, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.config_path = config_path
        self.models_data: List[Dict[str, Any]] = []
        self.active_model_id: str = "builtin_medium"
        self._current_worker: Optional[AICalculationWorker] = None
        self._cached_instances: Dict[str, BaseAI] = {}
        self._last_board: Optional[chess.Board] = None

        # Watchdog Timer: AI yanıt vermezse kilidi çözer
        self._watchdog_timer = QTimer(self)
        self._watchdog_timer.setSingleShot(True)
        self._watchdog_timer.timeout.connect(self._on_watchdog_timeout)

        self.load_models()

    def load_models(self):
        """Yapılandırma dosyasından modelleri yükler."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.models_data = data.get("models", [])
                    self.active_model_id = data.get("active_model_id", "builtin_medium")
            except Exception as e:
                print(f"Model yapılandırma dosyası okunamadı: {e}")
                self._create_default_config()
        else:
            self._create_default_config()

    def save_models(self):
        """Modelleri JSON dosyasına kaydeder."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = {
            "active_model_id": self.active_model_id,
            "models": self.models_data
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.models_updated.emit()

    def _create_default_config(self):
        self.models_data = [
            {
                "id": "builtin_easy",
                "name": "Yerleşik Kolay (Acemi)",
                "type": "builtin",
                "difficulty": "easy",
                "description": "Temel kuralları bilen başlangıç seviyesi motor.",
                "enabled": True
            },
            {
                "id": "builtin_medium",
                "name": "Yerleşik Orta (Kulüp)",
                "type": "builtin",
                "difficulty": "medium",
                "description": "3 hamle derinliğinde minimax ve pozisyonel analiz.",
                "enabled": True
            },
            {
                "id": "builtin_hard",
                "name": "Yerleşik Usta (Zor)",
                "type": "builtin",
                "difficulty": "hard",
                "description": "Taş-kare tabloları ve alpha-beta budaması ile zorlu motor.",
                "enabled": True
            }
        ]
        self.active_model_id = "builtin_medium"
        self.save_models()

    def get_active_model_info(self) -> Optional[Dict[str, Any]]:
        for m in self.models_data:
            if m.get("id") == self.active_model_id:
                return m
        return self.models_data[0] if self.models_data else None

    def set_active_model(self, model_id: str):
        self.active_model_id = model_id
        self.save_models()

    def create_ai_instance(self, model_config: Dict[str, Any]) -> BaseAI:
        ai_type = model_config.get("type", "builtin")
        if ai_type == "builtin":
            return HeuristicAI(model_config)
        elif ai_type == "uci":
            return UCIAI(model_config)
        elif ai_type == "gemini":
            return GeminiAI(model_config)
        elif ai_type == "ollama":
            return OllamaAI(model_config)
        elif ai_type in ("openai", "custom_llm"):
            return GenericLLMAI(model_config)
        else:
            return HeuristicAI(model_config)

    def request_move(self, board: chess.Board, move_history: List[str]):
        """Aktif modelden arka planda hamle talep eder."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            self.move_ready.emit(AIMoveResult(move_uci="", move_san="", thoughts="Geçerli hamle kalmadı."))
            return

        self._last_board = board.copy()

        active_config = self.get_active_model_info()
        if not active_config:
            # Model yoksa doğrudan hızlı yedek hamle üret
            self._emit_fallback_move(board, "Varsayılan yapay zeka hamlesi.")
            return

        model_id = active_config.get("id", "default")
        ai_type = active_config.get("type", "builtin")
        
        # Instance önbelleğe al veya yenisini üret
        if model_id not in self._cached_instances:
            self._cached_instances[model_id] = self.create_ai_instance(active_config)
        
        ai_inst = self._cached_instances[model_id]
        
        self.calculation_started.emit(ai_inst.name)

        # Önceki worker varsa durdur
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.abort()
            self._current_worker.wait(200)

        board_copy = board.copy()
        history_copy = list(move_history)

        self._current_worker = AICalculationWorker(ai_inst, board_copy, history_copy)
        self._current_worker.move_ready.connect(self._on_worker_move_ready)
        self._current_worker.error_occurred.connect(self._on_worker_error)
        self._current_worker.start()

        # Watchdog zaman aşımı süresi: Yerleşik için 3.5 sn, Harici/LLM için 8.0 sn
        timeout_ms = 3500 if ai_type == "builtin" else 8000
        self._watchdog_timer.start(timeout_ms)

    def _on_worker_move_ready(self, result: AIMoveResult):
        self._watchdog_timer.stop()
        
        # Hamle geçerliliğini doğrula
        if self._last_board:
            try:
                move = chess.Move.from_uci(result.move_uci)
                if move not in self._last_board.legal_moves:
                    # Model geçersiz bir UCI hamlesi dönerse güvenli yasal hamleye geç
                    self._emit_fallback_move(self._last_board, "Yedek yasal hamle uygulandı.")
                    return
            except Exception:
                self._emit_fallback_move(self._last_board, "Yedek yasal hamle uygulandı.")
                return

        self.move_ready.emit(result)

    def _on_worker_error(self, err: str):
        self._watchdog_timer.stop()
        print(f"[AIManager] AI Hatası: {err}")
        # Hata durumunda oyunu durdurma! Otomatik yedek hamle ile akışı sürdür
        if self._last_board and not self._last_board.is_game_over():
            self._emit_fallback_move(self._last_board, f"Otomatik kurtarma hamlesi yapıldı ({err})")
        else:
            self.calculation_failed.emit(err)

    def _on_watchdog_timeout(self):
        """AI beklenen sürede yanıt vermezse devreye girer ve kilidi açar."""
        print("[AIManager] Watchdog zaman aşımı devreye girdi. Otomatik hamle yapılıyor.")
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.abort()

        if self._last_board and not self._last_board.is_game_over():
            self._emit_fallback_move(self._last_board, "Zaman aşımı koruması: Hızlı hamle yapıldı.")

    def _emit_fallback_move(self, board: chess.Board, reason: str):
        """Her zaman geçerli ve hızlı bir taktiksel/yasal hamle üretir."""
        legal = list(board.legal_moves)
        if not legal:
            self.move_ready.emit(AIMoveResult(move_uci="", move_san="", thoughts="Geçerli hamle kalmadı."))
            return

        # Taş alımı veya şah çeken hamleleri öncelikle seç
        captures = [m for m in legal if board.is_capture(m) or board.gives_check(m)]
        chosen = random.choice(captures) if captures else random.choice(legal)
        san = board.san(chosen)

        self.move_ready.emit(AIMoveResult(
            move_uci=chosen.uci(),
            move_san=san,
            eval_score=0.0,
            thoughts=reason,
            time_spent=0.01
        ))

    def add_or_update_model(self, model_config: Dict[str, Any]):
        model_id = model_config.get("id")
        existing_idx = None
        for i, m in enumerate(self.models_data):
            if m.get("id") == model_id:
                existing_idx = i
                break

        if existing_idx is not None:
            self.models_data[existing_idx] = model_config
        else:
            self.models_data.append(model_config)

        if model_id in self._cached_instances:
            self._cached_instances[model_id].cleanup()
            del self._cached_instances[model_id]

        self.save_models()

    def delete_model(self, model_id: str):
        self.models_data = [m for m in self.models_data if m.get("id") != model_id]
        if model_id in self._cached_instances:
            self._cached_instances[model_id].cleanup()
            del self._cached_instances[model_id]
        if self.active_model_id == model_id and self.models_data:
            self.active_model_id = self.models_data[0].get("id", "builtin_medium")
        self.save_models()

    def cleanup(self):
        self._watchdog_timer.stop()
        if self._current_worker and self._current_worker.isRunning():
            self._current_worker.abort()
            self._current_worker.wait(300)
        for inst in self._cached_instances.values():
            inst.cleanup()
        self._cached_instances.clear()
