"""
Yapay Zeka Yöneticisi ve Arka Plan Hesaplama İş Parçacığı.
Kullanıcı arayüzünün donmaması için AI hesaplamalarını QThread içinde yürütür.
"""
import os
import json
from typing import Dict, List, Any, Optional
import chess
from PyQt6.QtCore import QObject, QThread, pyqtSignal

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

    def run(self):
        try:
            result = self.ai_instance.get_move(self.board_copy, self.move_history)
            self.move_ready.emit(result)
        except Exception as e:
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
        active_config = self.get_active_model_info()
        if not active_config:
            self.calculation_failed.emit("Aktif yapay zeka modeli bulunamadı.")
            return

        model_id = active_config.get("id", "default")
        
        # Instance önbelleğe al veya yenisini üret
        if model_id not in self._cached_instances:
            self._cached_instances[model_id] = self.create_ai_instance(active_config)
        
        ai_inst = self._cached_instances[model_id]
        
        self.calculation_started.emit(ai_inst.name)

        board_copy = board.copy()
        history_copy = list(move_history)

        self._current_worker = AICalculationWorker(ai_inst, board_copy, history_copy)
        self._current_worker.move_ready.connect(self._on_worker_move_ready)
        self._current_worker.error_occurred.connect(self._on_worker_error)
        self._current_worker.start()

    def _on_worker_move_ready(self, result: AIMoveResult):
        self.move_ready.emit(result)

    def _on_worker_error(self, err: str):
        self.calculation_failed.emit(err)

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

        # Cache temizle
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
        for inst in self._cached_instances.values():
            inst.cleanup()
        self._cached_instances.clear()
