"""
Yerleşik Python Heuristic Satranç Motoru.
İnternet bağlantısı, API anahtarı veya harici ikili dosya gerektirmeden çalışır.
Zaman Bütçeli İteratif Derinleşme (Iterative Deepening) + Alpha-Beta Budaması ve Taş-Kare Tabloları (PST) kullanır.
Asla kilitlenmez, donmaz ve maksimum 0.5 - 1.0 saniye içinde en iyi hamleyi döner.
"""
import time
import random
from typing import List, Dict, Any, Tuple, Optional
import chess
from .base_ai import BaseAI, AIMoveResult

# Taş Değerleri (Sentipiyon cinsinden)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Taş Kare Tabloları (Piece-Square Tables - Beyaz perspektifinden)
PST_PAWN = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

PST_BISHOP = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

PST_ROOK = [
      0,  0,  0,  0,  0,  0,  0,  0,
      5, 10, 10, 10, 10, 10, 10,  5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      0,  0,  0,  5,  5,  0,  0,  0
]

PST_QUEEN = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

PST_KING_MID = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

PST_TABLES = {
    chess.PAWN: PST_PAWN,
    chess.KNIGHT: PST_KNIGHT,
    chess.BISHOP: PST_BISHOP,
    chess.ROOK: PST_ROOK,
    chess.QUEEN: PST_QUEEN,
    chess.KING: PST_KING_MID
}

class HeuristicAI(BaseAI):
    """Yerleşik Heuristic satranç motoru - Hızlı, güvenli ve kilitlenmeyen motor."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.difficulty = config.get("difficulty", "medium").lower()

    def get_move(self, board: chess.Board, move_history: List[str]) -> AIMoveResult:
        start_time = time.time()
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return AIMoveResult(move_uci="", move_san="", thoughts="Geçerli hamle kalmadı.")

        # Tek yasal hamle varsa doğrudan oyna (0 saniye)
        if len(legal_moves) == 1:
            best_move = legal_moves[0]
            san_move = board.san(best_move)
            return AIMoveResult(
                move_uci=best_move.uci(),
                move_san=san_move,
                eval_score=0.0,
                thoughts="Zorunlu tek hamle yapıldı.",
                time_spent=time.time() - start_time
            )

        if self.difficulty == "easy":
            best_move, score = self._get_easy_move(board, legal_moves)
            thoughts = "Kolay mod: Hızlı ve basit taktik hamle seçildi."
        elif self.difficulty == "medium":
            best_move, score = self._get_iterative_move(board, max_depth=3, time_limit=0.45)
            thoughts = "Orta seviye: 3 hamle derinliği ve pozisyon dengesi analiz edildi."
        else:  # hard
            best_move, score = self._get_iterative_move(board, max_depth=4, time_limit=0.90)
            thoughts = "Zor seviye: Taş-kare tabloları ve alpha-beta budaması ile derin hesap yapıldı."

        # Herhangi bir nedenle hamle None olursa ilk yasal hamleye dön
        if best_move is None or best_move not in board.legal_moves:
            best_move = legal_moves[0]
            score = 0

        elapsed = time.time() - start_time
        san_move = board.san(best_move)
        eval_pawn = score / 100.0 if score is not None else 0.0

        return AIMoveResult(
            move_uci=best_move.uci(),
            move_san=san_move,
            eval_score=eval_pawn,
            thoughts=thoughts,
            time_spent=elapsed
        )

    def _get_easy_move(self, board: chess.Board, legal_moves: List[chess.Move]) -> Tuple[chess.Move, int]:
        """Kolay mod: Anlık taş alımı veya basit hamle."""
        captures_and_checks = [m for m in legal_moves if board.is_capture(m) or board.gives_check(m)]
        if captures_and_checks and random.random() < 0.6:
            chosen = random.choice(captures_and_checks)
        else:
            chosen = random.choice(legal_moves)
        return chosen, 0

    def _get_iterative_move(self, board: chess.Board, max_depth: int, time_limit: float) -> Tuple[chess.Move, int]:
        """
        Zaman Bütçeli İteratif Derinleşme (Iterative Deepening).
        Önce 1. derinliği, sonra 2. derinliği hesaplar.
        Süre dolarsa eldeki en son tamamlanmış en iyi hamleyi hemen döner.
        """
        start_time = time.time()
        legal_moves = list(board.legal_moves)
        best_overall_move = legal_moves[0]
        best_overall_score = 0

        ordered_moves = self._order_moves(board, legal_moves)

        for current_depth in range(1, max_depth + 1):
            move, score, aborted = self._search_root(board, ordered_moves, current_depth, start_time, time_limit)
            if move is not None and not aborted:
                best_overall_move = move
                best_overall_score = score
            
            # Zaman sınırına yaklaşıldıysa daha derin aramayı başlatma
            if aborted or (time.time() - start_time) >= time_limit * 0.8:
                break

        return best_overall_move, best_overall_score

    def _search_root(
        self,
        board: chess.Board,
        moves: List[chess.Move],
        depth: int,
        start_time: float,
        time_limit: float
    ) -> Tuple[Optional[chess.Move], int, bool]:
        """Kök seviyesinde alpha-beta araması."""
        is_white = (board.turn == chess.WHITE)
        best_move = None
        alpha = -1000000
        beta = 1000000

        if is_white:
            max_eval = -1000000
            for move in moves:
                if (time.time() - start_time) > time_limit:
                    return best_move, max_eval, True

                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, False, start_time, time_limit)
                board.pop()

                if eval_val is None:  # Süre doldu
                    return best_move, max_eval, True

                if eval_val > max_eval:
                    max_eval = eval_val
                    best_move = move
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return best_move, max_eval, False
        else:
            min_eval = 1000000
            for move in moves:
                if (time.time() - start_time) > time_limit:
                    return best_move, min_eval, True

                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, True, start_time, time_limit)
                board.pop()

                if eval_val is None:  # Süre doldu
                    return best_move, min_eval, True

                if eval_val < min_eval:
                    min_eval = eval_val
                    best_move = move
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return best_move, min_eval, False

    def _alpha_beta(
        self,
        board: chess.Board,
        depth: int,
        alpha: int,
        beta: int,
        is_maximizing: bool,
        start_time: float,
        time_limit: float
    ) -> Optional[int]:
        """Zaman kontrollü Alpha-Beta araması."""
        if (time.time() - start_time) > time_limit:
            return None

        if depth == 0 or board.is_game_over():
            return self._evaluate_board(board)

        ordered_moves = self._order_moves(board, list(board.legal_moves))

        if is_maximizing:
            max_eval = -1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, False, start_time, time_limit)
                board.pop()

                if eval_val is None:
                    return None

                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, True, start_time, time_limit)
                board.pop()

                if eval_val is None:
                    return None

                min_eval = min(min_eval, eval_val)
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return min_eval

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Hamleleri önceliklendir (Budama performansını katlar)."""
        def move_score(move: chess.Move) -> int:
            score = 0
            if board.is_capture(move):
                victim = board.piece_at(move.to_square)
                attacker = board.piece_at(move.from_square)
                victim_val = PIECE_VALUES.get(victim.piece_type, 0) if victim else 100
                attacker_val = PIECE_VALUES.get(attacker.piece_type, 0) if attacker else 100
                score += 10000 + (victim_val * 10 - attacker_val)
            if move.promotion:
                score += 9000
            if board.gives_check(move):
                score += 500
            return score

        return sorted(moves, key=move_score, reverse=True)

    def _evaluate_board(self, board: chess.Board) -> int:
        """Tahtanın genel sentipiyon puanını hesaplar (Pozitif = Beyaz üstün)."""
        if board.is_checkmate():
            return -900000 if board.turn == chess.WHITE else 900000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        piece_map = board.piece_map()

        for sq, piece in piece_map.items():
            val = PIECE_VALUES.get(piece.piece_type, 0)
            
            # Kare indexini PST tablosuna eşle (Beyaz alttan, Siyah üstten)
            if piece.color == chess.WHITE:
                pst_idx = 63 - sq
                pst_val = PST_TABLES.get(piece.piece_type, [0]*64)[pst_idx]
                score += (val + pst_val)
            else:
                pst_idx = sq
                pst_val = PST_TABLES.get(piece.piece_type, [0]*64)[pst_idx]
                score -= (val + pst_val)

        return score
