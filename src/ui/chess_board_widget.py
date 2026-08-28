"""
İnteraktif Satranç Tahtası Bileşeni (PyQt6).
Akıcı taş sürükleme, tıkla-oyna desteği, yasal hamle göstergeleri, son hamle ve şah vurguları.
"""
from typing import Optional, List, Tuple, Dict
import chess
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QMouseEvent, QPixmap, QRadialGradient, QIcon
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize

from ..core.board_manager import BoardManager
from ..utils.asset_loader import AssetLoader

class PromotionDialog(QDialog):
    """Piyon son yataya ulaştığında açılan Terfi (Vezir, Kale, Fil, At) Seçim Penceresi."""
    def __init__(self, color: bool, asset_loader: AssetLoader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Piyon Terfisi")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.chosen_piece = chess.QUEEN

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(15, 12, 15, 15)
        main_vbox.setSpacing(8)

        # Başlık Etiketi
        lbl_title = QLabel("Terfi Edecek Taşı Seçin:", self)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #e0e0e0; font-weight: bold;")
        main_vbox.addWidget(lbl_title)

        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setStyleSheet("""
            QDialog {
                background-color: #262421;
                border: 2px solid #b58863;
                border-radius: 12px;
            }
            QPushButton {
                background-color: #36322d;
                color: #ffffff;
                border: 2px solid #524b42;
                border-radius: 8px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #635b50;
                border-color: #8c7f6f;
            }
        """)

        pieces = [
            (chess.QUEEN, "Vezir"),
            (chess.KNIGHT, "At"),
            (chess.ROOK, "Kale"),
            (chess.BISHOP, "Fil")
        ]

        for p_type, name in pieces:
            btn = QPushButton(self)
            pix = asset_loader.get_piece_pixmap(color, p_type, 64)
            btn.setIcon(QIcon(pix))
            btn.setIconSize(QSize(56, 56))
            btn.setToolTip(f"{name} olarak terfi et")
            btn.clicked.connect(lambda checked, pt=p_type: self._select_piece(pt))
            layout.addWidget(btn)

        main_vbox.addLayout(layout)

    def _select_piece(self, piece_type: int):
        self.chosen_piece = piece_type
        self.accept()

class ChessBoardWidget(QWidget):
    """Satranç tahtası görsel bileşeni."""
    
    move_made = pyqtSignal(chess.Move)       # Kullanıcı hamle yaptığında
    square_clicked = pyqtSignal(int)          # Bir kareye tıklandığında

    THEMES = {
        "wood": {
            "name": "Klasik Ahşap",
            "light": QColor(240, 217, 181),
            "dark": QColor(181, 136, 99),
            "last_move": QColor(205, 210, 106, 160),
            "selected": QColor(255, 215, 0, 150),
            "legal_dot": QColor(0, 0, 0, 60),
            "legal_capture": QColor(0, 0, 0, 50),
            "check": QColor(235, 64, 52, 180)
        },
        "emerald": {
            "name": "Zümrüt Yeşili",
            "light": QColor(238, 238, 210),
            "dark": QColor(118, 150, 86),
            "last_move": QColor(187, 203, 43, 160),
            "selected": QColor(246, 235, 100, 150),
            "legal_dot": QColor(0, 0, 0, 60),
            "legal_capture": QColor(0, 0, 0, 50),
            "check": QColor(235, 64, 52, 180)
        },
        "ocean": {
            "name": "Okyanus Mavisi",
            "light": QColor(222, 227, 230),
            "dark": QColor(88, 131, 168),
            "last_move": QColor(130, 180, 220, 160),
            "selected": QColor(100, 200, 255, 150),
            "legal_dot": QColor(0, 0, 0, 60),
            "legal_capture": QColor(0, 0, 0, 50),
            "check": QColor(235, 64, 52, 180)
        },
        "charcoal": {
            "name": "Koyu Gece",
            "light": QColor(140, 140, 140),
            "dark": QColor(60, 60, 60),
            "last_move": QColor(100, 140, 180, 160),
            "selected": QColor(220, 180, 60, 150),
            "legal_dot": QColor(255, 255, 255, 100),
            "legal_capture": QColor(255, 255, 255, 80),
            "check": QColor(235, 64, 52, 180)
        }
    }

    def __init__(self, board_manager: BoardManager, asset_loader: AssetLoader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.board_manager = board_manager
        self.asset_loader = asset_loader
        
        self.flipped = False               # False: Beyaz altta, True: Siyah altta
        self.interactive = True            # Kullanıcı taş oynayabilir mi
        self.current_theme_key = "emerald"
        
        # Etkileşim durumları
        self.selected_square: Optional[int] = None
        self.legal_moves_for_selected: List[chess.Move] = []
        self.last_move: Optional[chess.Move] = None
        
        # Sürükle-bırak durumları
        self.is_dragging = False
        self.drag_piece: Optional[chess.Piece] = None
        self.drag_square: Optional[int] = None
        self.drag_current_pos: QPointF = QPointF(0, 0)

        self.setMouseTracking(True)
        self.setMinimumSize(400, 400)

    @property
    def theme(self) -> Dict[str, QColor]:
        return self.THEMES.get(self.current_theme_key, self.THEMES["emerald"])

    def set_theme(self, theme_key: str):
        if theme_key in self.THEMES:
            self.current_theme_key = theme_key
            self.update()

    def set_flipped(self, flipped: bool):
        self.flipped = flipped
        self.update()

    def set_last_move(self, move: Optional[chess.Move]):
        self.last_move = move
        self.update()

    def clear_selection(self):
        self.selected_square = None
        self.legal_moves_for_selected.clear()
        self.is_dragging = False
        self.drag_piece = None
        self.drag_square = None
        self.update()

    # --- Koordinat ve Kare Hesaplamaları ---

    def _get_square_size(self) -> float:
        w = self.width()
        h = self.height()
        return min(w, h) / 8.0

    def _get_board_offset(self) -> Tuple[float, float, float]:
        """(offset_x, offset_y, square_size) döner."""
        sq_size = self._get_square_size()
        board_dim = sq_size * 8
        ox = (self.width() - board_dim) / 2.0
        oy = (self.height() - board_dim) / 2.0
        return ox, oy, sq_size

    def _square_to_row_col(self, square: int) -> Tuple[int, int]:
        """Satranç karesini (0-63) ekrandaki (row, col) (0-7) değerine çevirir."""
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if not self.flipped:
            col = file
            row = 7 - rank
        else:
            col = 7 - file
            row = rank
        return row, col

    def _row_col_to_square(self, row: int, col: int) -> Optional[int]:
        """Ekrandaki (row, col) değerini satranç karesine (0-63) çevirir."""
        if 0 <= row < 8 and 0 <= col < 8:
            if not self.flipped:
                file = col
                rank = 7 - row
            else:
                file = 7 - col
                rank = row
            return chess.square(file, rank)
        return None

    def _pos_to_square(self, pos: QPointF) -> Optional[int]:
        ox, oy, sq_size = self._get_board_offset()
        x = pos.x() - ox
        y = pos.y() - oy
        if 0 <= x < sq_size * 8 and 0 <= y < sq_size * 8:
            col = int(x // sq_size)
            row = int(y // sq_size)
            return self._row_col_to_square(row, col)
        return None

    def _get_square_rect(self, square: int) -> QRectF:
        ox, oy, sq_size = self._get_board_offset()
        row, col = self._square_to_row_col(square)
        return QRectF(ox + col * sq_size, oy + row * sq_size, sq_size, sq_size)

    # --- Boyama ve Çizim Olayları ---

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        ox, oy, sq_size = self._get_board_offset()
        theme = self.theme

        # 1. Kareleri Çiz
        for row in range(8):
            for col in range(8):
                sq = self._row_col_to_square(row, col)
                rect = QRectF(ox + col * sq_size, oy + row * sq_size, sq_size, sq_size)
                
                # Açık / Koyu Renk
                is_light = (row + col) % 2 == 0
                color = theme["light"] if is_light else theme["dark"]
                painter.fillRect(rect, color)

                # Son Hamle Vurgusu
                if self.last_move and sq in (self.last_move.from_square, self.last_move.to_square):
                    painter.fillRect(rect, theme["last_move"])

                # Seçili Kare Vurgusu
                if self.selected_square is not None and sq == self.selected_square:
                    painter.fillRect(rect, theme["selected"])

                # Şah Durumu Kırmızı Vurgu
                if sq is not None and self.board_manager.board.is_check():
                    king_sq = self.board_manager.board.king(self.board_manager.board.turn)
                    if sq == king_sq:
                        rad_grad = QRadialGradient(rect.center(), sq_size * 0.7)
                        rad_grad.setColorAt(0, QColor(255, 0, 0, 200))
                        rad_grad.setColorAt(1, QColor(255, 0, 0, 0))
                        painter.fillRect(rect, QBrush(rad_grad))

        # 2. Koordinat Harfleri ve Sayıları
        font = QFont("Sans Serif", int(sq_size * 0.16), QFont.Weight.Bold)
        painter.setFont(font)
        for i in range(8):
            # Dosya harfleri (a-h)
            file_char = chr(ord('h') - i) if self.flipped else chr(ord('a') + i)
            rect = QRectF(ox + i * sq_size + 4, oy + 8 * sq_size - sq_size * 0.22, sq_size, sq_size * 0.2)
            is_light = (7 + i) % 2 == 0
            painter.setPen(theme["dark"] if is_light else theme["light"])
            painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom, file_char)

            # Yatay sayıları (1-8)
            rank_char = str(i + 1) if self.flipped else str(8 - i)
            rect = QRectF(ox + 4, oy + i * sq_size + 2, sq_size * 0.3, sq_size * 0.3)
            is_light = (i + 0) % 2 == 0
            painter.setPen(theme["dark"] if is_light else theme["light"])
            painter.drawText(rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, rank_char)

        # 3. Yasal Hamle Hedef Göstergeleri
        if self.selected_square is not None and self.legal_moves_for_selected:
            for move in self.legal_moves_for_selected:
                target_sq = move.to_square
                target_rect = self._get_square_rect(target_sq)
                target_piece = self.board_manager.get_piece_at(target_sq)
                is_en_passant = self.board_manager.board.is_en_passant(move)

                if target_piece or is_en_passant:
                    # Taş alma karesi: Kenarlarda halka/köşe göstergesi
                    painter.setPen(QPen(theme["legal_capture"], sq_size * 0.08))
                    painter.setBrush(Qt.BrushStyle.NoBrush)
                    radius = sq_size * 0.42
                    painter.drawEllipse(target_rect.center(), radius, radius)
                else:
                    # Boş kare: Ortada şık nokta
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.setBrush(theme["legal_dot"])
                    radius = sq_size * 0.16
                    painter.drawEllipse(target_rect.center(), radius, radius)

        # 4. Taşları Çiz
        for sq, piece in self.board_manager.board.piece_map().items():
            # Eğer taş sürükleniyorsa orijinal yerinde çizme
            if self.is_dragging and sq == self.drag_square:
                continue

            rect = self._get_square_rect(sq)
            pix = self.asset_loader.get_piece_pixmap(piece.color, piece.piece_type, int(sq_size))
            if pix and not pix.isNull():
                painter.drawPixmap(rect.toRect(), pix)

        # 5. Sürüklenen Taşı Çiz (Farenin altında)
        if self.is_dragging and self.drag_piece:
            pix = self.asset_loader.get_piece_pixmap(self.drag_piece.color, self.drag_piece.piece_type, int(sq_size * 1.05))
            if pix and not pix.isNull():
                drag_rect = QRectF(
                    self.drag_current_pos.x() - sq_size / 2.0,
                    self.drag_current_pos.y() - sq_size / 2.0,
                    sq_size * 1.05,
                    sq_size * 1.05
                )
                painter.drawPixmap(drag_rect.toRect(), pix)

        painter.end()

    # --- Fare Olayları (Tıkla-Oyna & Sürükle-Bırak) ---

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton or not self.interactive:
            return

        sq = self._pos_to_square(event.position())
        if sq is None:
            self.clear_selection()
            return

        self.square_clicked.emit(sq)
        piece = self.board_manager.get_piece_at(sq)

        # 1. Eğer halihazırda seçili bir kare varsa ve tıklanan kare yasal bir hedefse hamle yap
        if self.selected_square is not None and self.selected_square != sq:
            move_candidate = self._find_matching_move(self.selected_square, sq)
            if move_candidate:
                self._handle_move_execution(move_candidate)
                return

        # 2. Taş seçimi ve sürükleme başlatma
        if piece and piece.color == self.board_manager.board.turn:
            self.selected_square = sq
            self.legal_moves_for_selected = self.board_manager.get_legal_moves_from(sq)
            self.is_dragging = True
            self.drag_piece = piece
            self.drag_square = sq
            self.drag_current_pos = event.position()
            self.update()
        else:
            self.clear_selection()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging:
            self.drag_current_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton or not self.is_dragging:
            return

        target_sq = self._pos_to_square(event.position())
        from_sq = self.drag_square

        self.is_dragging = False
        self.drag_piece = None
        self.drag_square = None

        if target_sq is not None and from_sq is not None and target_sq != from_sq:
            move_candidate = self._find_matching_move(from_sq, target_sq)
            if move_candidate:
                self._handle_move_execution(move_candidate)
                return

        self.update()

    def _find_matching_move(self, from_sq: int, to_sq: int) -> Optional[chess.Move]:
        legal_candidates = [
            m for m in self.legal_moves_for_selected 
            if m.from_square == from_sq and m.to_square == to_sq
        ]
        if not legal_candidates:
            return None

        # Terfi durumu kontrolü
        promotions = [m for m in legal_candidates if m.promotion]
        if promotions:
            # Terfi penceresi aç
            moving_piece = self.board_manager.get_piece_at(from_sq)
            color = moving_piece.color if moving_piece else self.board_manager.board.turn
            
            dlg = PromotionDialog(color, self.asset_loader, self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                chosen_promo = dlg.chosen_piece
                for m in promotions:
                    if m.promotion == chosen_promo:
                        return m
            return None

        return legal_candidates[0]

    def _handle_move_execution(self, move: chess.Move):
        self.clear_selection()
        self.move_made.emit(move)
