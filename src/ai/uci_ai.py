"""
UCI (Universal Chess Interface) Satranç Motoru Adaptörü (Ör: Stockfish, Komodo, LCZero).
"""
import os
import time
from typing import List, Dict, Any, Tuple
import chess
import chess.engine
from .base_ai import BaseAI, AIMoveResult

class UCIAI(BaseAI):
    """UCI motorları ile haberleşen yapay zeka sınıfı."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.executable_path = config.get("executable_path", "/usr/bin/stockfish")
        self.depth = int(config.get("depth", 15))
        self.time_limit = float(config.get("time_limit", 1.5))
        self.skill_level = int(config.get("skill_level", 20))
        self._engine: Optional[chess.engine.SimpleEngine] = None

    def _get_or_create_engine(self) -> chess.engine.SimpleEngine:
        if self._engine is None or self._engine.is_closed():
            if not os.path.isfile(self.executable_path):
                raise FileNotFoundError(f"UCI motor dosyası bulunamadı: {self.executable_path}")
            if not os.access(self.executable_path, os.X_OK):
                raise PermissionError(f"UCI motor dosyası çalıştırılabilir değil: {self.executable_path}")
            
            self._engine = chess.engine.SimpleEngine.popen_uci(self.executable_path)
            try:
                # Skill level ayarını dene (Stockfish destekler)
                self._engine.configure({"Skill Level": self.skill_level})
            except Exception:
                pass
        return self._engine

    def get_move(self, board: chess.Board, move_history: List[str]) -> AIMoveResult:
        start_time = time.time()
        try:
            engine = self._get_or_create_engine()
            
            limit = chess.engine.Limit(time=self.time_limit, depth=self.depth)
            result = engine.play(board, limit, info=chess.engine.INFO_ALL)
            
            elapsed = time.time() - start_time
            best_move = result.move
            
            if not best_move or best_move not in board.legal_moves:
                # Fallback to any legal move
                best_move = list(board.legal_moves)[0]

            eval_score = None
            mate_in = None
            if result.info:
                score_obj = result.info.get("score")
                if score_obj:
                    # Skoru beyaz perspektifine çevir
                    pov_score = score_obj.white()
                    if pov_score.is_mate():
                        mate_in = pov_score.mate()
                    else:
                        eval_score = pov_score.score() / 100.0

            san_move = board.san(best_move)
            thoughts = f"UCI Motoru ({os.path.basename(self.executable_path)}) - Derinlik: {self.depth}, Süre: {elapsed:.2f}s"
            if mate_in:
                thoughts += f" | Mat #{abs(mate_in)}"
            elif eval_score is not None:
                thoughts += f" | Skor: {eval_score:+.2f}"

            return AIMoveResult(
                move_uci=best_move.uci(),
                move_san=san_move,
                eval_score=eval_score,
                mate_in=mate_in,
                thoughts=thoughts,
                time_spent=elapsed
            )

        except Exception as e:
            elapsed = time.time() - start_time
            # Motor hatası durumunda rastgele yasal hamle yap
            legal_moves = list(board.legal_moves)
            fallback_move = legal_moves[0] if legal_moves else None
            if fallback_move:
                return AIMoveResult(
                    move_uci=fallback_move.uci(),
                    move_san=board.san(fallback_move),
                    thoughts=f"UCI Motor Hatası ({str(e)}). Yedek hamle oynandı.",
                    time_spent=elapsed
                )
            raise e

    def test_connection(self) -> Tuple[bool, str]:
        try:
            if not os.path.exists(self.executable_path):
                return False, f"Motor dosyası bulunamadı: {self.executable_path}"
            if not os.access(self.executable_path, os.X_OK):
                return False, f"Dosyanın çalıştırma yetkisi yok (chmod +x gerekebilir): {self.executable_path}"
            
            engine = chess.engine.SimpleEngine.popen_uci(self.executable_path)
            engine_name = engine.id.get("name", "Bilinmeyen Motor")
            engine.quit()
            return True, f"Başarıyla bağlandı! Motor Adı: {engine_name}"
        except Exception as e:
            return False, f"UCI Başlatma Hatası: {str(e)}"

    def cleanup(self):
        if self._engine and not self._engine.is_closed():
            try:
                self._engine.quit()
            except Exception:
                pass
            self._engine = None
