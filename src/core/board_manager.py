"""
Satranç tahtası kural motoru ve durum yöneticisi.
python-chess kütüphanesini sarmalar ve UI ile AI katmanlarına temiz bir API sunar.
"""
from typing import List, Dict, Optional, Tuple
import chess
import chess.pgn
import io

class MoveRecord:
    """Tek bir hamlenin detayları."""
    def __init__(self, uci_move: str, san_move: str, piece_type: int, color: bool, 
                 captured_piece_type: Optional[int] = None, is_check: bool = False, is_mate: bool = False):
        self.uci = uci_move
        self.san = san_move
        self.uci_move = uci_move
        self.san_move = san_move
        self.piece_type = piece_type
        self.color = color  # True: White, False: Black
        self.captured_piece_type = captured_piece_type
        self.is_check = is_check
        self.is_mate = is_mate

class BoardManager:
    """Satranç tahtası durumunu yöneten ana sınıf."""

    PIECE_VALUES = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    PIECE_CHARS = {
        (chess.WHITE, chess.PAWN): "P",
        (chess.WHITE, chess.KNIGHT): "N",
        (chess.WHITE, chess.BISHOP): "B",
        (chess.WHITE, chess.ROOK): "R",
        (chess.WHITE, chess.QUEEN): "Q",
        (chess.WHITE, chess.KING): "K",
        (chess.BLACK, chess.PAWN): "p",
        (chess.BLACK, chess.KNIGHT): "n",
        (chess.BLACK, chess.BISHOP): "b",
        (chess.BLACK, chess.ROOK): "r",
        (chess.BLACK, chess.QUEEN): "q",
        (chess.BLACK, chess.KING): "k",
    }

    def __init__(self, fen: Optional[str] = None):
        self.board = chess.Board(fen) if fen else chess.Board()
        self.move_history: List[MoveRecord] = []
        self._redo_stack: List[chess.Move] = []

    def reset(self, fen: Optional[str] = None):
        """Tahtayı başlangıç veya verilen FEN durumuna sıfırlar."""
        self.board = chess.Board(fen) if fen else chess.Board()
        self.move_history.clear()
        self._redo_stack.clear()

    @property
    def turn(self) -> bool:
        """Sıranın kimde olduğunu döner (True: Beyaz, False: Siyah)."""
        return self.board.turn == chess.WHITE

    @property
    def current_fen(self) -> str:
        """Mevcut tahta durumunun FEN dizesini döner."""
        return self.board.fen()

    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        """Verilen karedeki taşı döner."""
        return self.board.piece_at(square)

    def is_legal(self, move: chess.Move) -> bool:
        """Verilen hamlenin yasal olup olmadığını kontrol eder."""
        return move in self.board.legal_moves

    def get_legal_moves_from(self, square: int) -> List[chess.Move]:
        """Belirtilen kareden yapılabilecek tüm yasal hamleleri listeler."""
        return [m for m in self.board.legal_moves if m.from_square == square]

    def make_move(self, move: chess.Move) -> Optional[MoveRecord]:
        """Tahtada bir hamle yapar ve kayıt oluşturur."""
        if not self.is_legal(move):
            return None

        # Hamle detaylarını topla
        moving_piece = self.board.piece_at(move.from_square)
        captured_piece = self.board.piece_at(move.to_square)
        
        # Geçerken alma (en-passant) yakalama kontrolü
        if moving_piece and moving_piece.piece_type == chess.PAWN and self.board.is_en_passant(move):
            captured_piece_type = chess.PAWN
        else:
            captured_piece_type = captured_piece.piece_type if captured_piece else None

        san = self.board.san(move)
        uci = move.uci()
        piece_type = moving_piece.piece_type if moving_piece else chess.PAWN
        color = self.board.turn

        # Hamleyi tahtada uygula
        self.board.push(move)
        self._redo_stack.clear()

        record = MoveRecord(
            uci_move=uci,
            san_move=san,
            piece_type=piece_type,
            color=color,
            captured_piece_type=captured_piece_type,
            is_check=self.board.is_check(),
            is_mate=self.board.is_checkmate()
        )
        self.move_history.append(record)
        return record

    def make_uci_move(self, uci_str: str) -> Optional[MoveRecord]:
        """UCI formatındaki dizeden (örneğin 'e2e4' veya 'e7e8q') hamle yapar."""
        try:
            move = chess.Move.from_uci(uci_str)
            return self.make_move(move)
        except Exception:
            return None

    def undo_move(self) -> Optional[chess.Move]:
        """Son hamleyi geri alır."""
        if len(self.board.move_stack) > 0:
            move = self.board.pop()
            self._redo_stack.append(move)
            if self.move_history:
                self.move_history.pop()
            return move
        return None

    def redo_move(self) -> Optional[MoveRecord]:
        """Geri alınan hamleyi tekrar ileri alır."""
        if self._redo_stack:
            move = self._redo_stack.pop()
            return self.make_move(move)
        return None

    def is_game_over(self) -> bool:
        """Oyunun bitip bitmediğini kontrol eder."""
        return self.board.is_game_over()

    def get_game_status(self) -> Tuple[bool, str, Optional[str]]:
        """
        Oyun durumunu döner.
        Dönüş: (is_over, reason_text, winner_text ['Beyaz', 'Siyah', 'Berabere', None])
        """
        if self.board.is_checkmate():
            winner = "Siyah" if self.board.turn == chess.WHITE else "Beyaz"
            return True, f"Şah Mat! {winner} kazandı.", winner
        elif self.board.is_stalemate():
            return True, "Pat (Berabere)! Yasal hamle yok.", "Berabere"
        elif self.board.is_insufficient_material():
            return True, "Yetersiz Taş Nedeniyle Berabere!", "Berabere"
        elif self.board.is_seventyfive_moves():
            return True, "75 Hamle Kuralı Nedeniyle Berabere!", "Berabere"
        elif self.board.is_fivefold_repetition():
            return True, "5 Kez Pozisyon Tekrarı Nedeniyle Berabere!", "Berabere"
        elif self.board.can_claim_fifty_moves():
            return True, "50 Hamle Kuralı Nedeniyle Berabere!", "Berabere"
        elif self.board.can_claim_threefold_repetition():
            return True, "3 Kez Pozisyon Tekrarı Nedeniyle Berabere!", "Berabere"
        
        if self.board.is_check():
            turn_name = "Beyaz" if self.board.turn == chess.WHITE else "Siyah"
            return False, f"Şah! Sıra {turn_name} oyuncuda.", None

        turn_name = "Beyaz" if self.board.turn == chess.WHITE else "Siyah"
        return False, f"Sıra: {turn_name}", None

    def get_captured_pieces(self) -> Dict[str, List[int]]:
        """
        Alınan taşları listeler.
        Dönüş: {'white': [chess.PAWN, ...], 'black': [chess.BISHOP, ...]}
        """
        captured = {'white': [], 'black': []}
        for rec in self.move_history:
            if rec.captured_piece_type is not None:
                # Alınan taşın rengi hamleyi yapanın zıttıdır
                captured_color = 'black' if rec.color else 'white'
                captured[captured_color].append(rec.captured_piece_type)
        return captured

    def get_material_difference(self) -> int:
        """
        Tahtadaki materyal farkını hesaplar.
        Pozitif: Beyaz önde, Negatif: Siyah önde.
        """
        white_val = sum(self.PIECE_VALUES[p.piece_type] for p in self.board.piece_map().values() if p.color == chess.WHITE)
        black_val = sum(self.PIECE_VALUES[p.piece_type] for p in self.board.piece_map().values() if p.color == chess.BLACK)
        return white_val - black_val

    def get_pgn_string(self) -> str:
        """Mevcut oyunun PGN metnini oluşturur."""
        game = chess.pgn.Game.from_board(self.board)
        exporter = chess.pgn.StringExporter(headers=True, variations=True, comments=True)
        return game.accept(exporter)

    def get_legal_moves_san_list(self) -> List[str]:
        """Tüm yasal hamleleri SAN formatında döner."""
        return [self.board.san(m) for m in self.board.legal_moves]

    def get_legal_moves_uci_list(self) -> List[str]:
        """Tüm yasal hamleleri UCI formatında döner."""
        return [m.uci() for m in self.board.legal_moves]
