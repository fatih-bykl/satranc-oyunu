"""
Yerleşik Python Heuristic Satranç Motoru.
İnternet bağlantısı, API anahtarı veya harici ikili dosya gerektirmeden çalışır.
Minimax + Alpha-Beta Budama ve Taş-Kare Tabloları (PST) kullanır.
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
    """Yerleşik Heuristic satranç motoru."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.difficulty = config.get("difficulty", "medium").lower()

    def get_move(self, board: chess.Board, move_history: List[str]) -> AIMoveResult:
        start_time = time.time()
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return AIMoveResult(move_uci="", move_san="", thoughts="Geçerli hamle kalmadı.")

        if self.difficulty == "easy":
            best_move, score = self._get_easy_move(board, legal_moves)
            thoughts = "Kolay mod: Basit taktikler ve hızlı hamleler seçildi."
        elif self.difficulty == "medium":
            best_move, score = self._get_minimax_move(board, depth=3)
            thoughts = "Orta seviye: 3 hamle ilerisi ve materyal dengesi analiz edildi."
        else:  # hard
            best_move, score = self._get_minimax_move(board, depth=4)
            thoughts = "Zor seviye: Taş-kare tabloları ve alpha-beta budaması ile derin hesap yapıldı."

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
        # Taş alımı veya şah çeken hamleleri %50 ihtimalle tercih et, yoksa rastgele
        captures_and_checks = [m for m in legal_moves if board.is_capture(m) or board.gives_check(m)]
        if captures_and_checks and random.random() < 0.6:
            chosen = random.choice(captures_and_checks)
        else:
            chosen = random.choice(legal_moves)
        return chosen, 0

    def _get_minimax_move(self, board: chess.Board, depth: int) -> Tuple[chess.Move, int]:
        is_white = (board.turn == chess.WHITE)
        best_move = None
        alpha = -1000000
        beta = 1000000

        ordered_moves = self._order_moves(board, list(board.legal_moves))
        
        if is_white:
            max_eval = -1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                if eval_val > max_eval:
                    max_eval = eval_val
                    best_move = move
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return best_move or ordered_moves[0], max_eval
        else:
            min_eval = 1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                if eval_val < min_eval:
                    min_eval = eval_val
                    best_move = move
                beta = min(beta, eval_val)
                if beta <= alpha:
                    break
            return best_move or ordered_moves[0], min_eval

    def _alpha_beta(self, board: chess.Board, depth: int, alpha: int, beta: int, is_maximizing: bool) -> int:
        if depth == 0 or board.is_game_over():
            return self._evaluate_board(board)

        ordered_moves = self._order_moves(board, list(board.legal_moves))

        if is_maximizing:
            max_eval = -1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_val)
                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = 1000000
            for move in ordered_moves:
                board.push(move)
                eval_val = self._alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
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
