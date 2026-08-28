"""
Hamle Geçmişi, Alınan Taşlar ve PGN Notasyon Bileşeni.
"""
from typing import Optional, List, Dict
import chess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton, QApplication
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal

from ..core.board_manager import BoardManager
from ..utils.asset_loader import AssetLoader

class MoveHistoryWidget(QWidget):
    """Hamle geçmişi ve alınan taşlar tablosu."""

    step_back_requested = pyqtSignal()
    step_forward_requested = pyqtSignal()

    def __init__(self, board_manager: BoardManager, asset_loader: AssetLoader, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.board_manager = board_manager
        self.asset_loader = asset_loader

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(6)

        # Başlık
        title_label = QLabel("Hamle Geçmişi", self)
        title_label.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(title_label)

        # 1. Alınan Taşlar (Siyahın aldıkları / Beyazın kaybettikleri)
        self.captured_top_label = QLabel(self)
        self.captured_top_label.setStyleSheet("color: #b0b0b0; font-size: 13px; padding: 2px;")
        layout.addWidget(self.captured_top_label)

        # 2. Hamle Listesi Tablosu
        self.table = QTableWidget(0, 3, self)
        self.table.setHorizontalHeaderLabels(["No", "Beyaz", "Siyah"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: #f0f0f0;
                gridline-color: #3d3d3d;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #383838;
                color: #ccc;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #444;
            }
            QTableWidget::item:selected {
                background-color: #4a6984;
            }
        """)
        layout.addWidget(self.table)

        # 3. Alınan Taşlar (Beyazın aldıkları / Siyahın kaybettikleri)
        self.captured_bottom_label = QLabel(self)
        self.captured_bottom_label.setStyleSheet("color: #b0b0b0; font-size: 13px; padding: 2px;")
        layout.addWidget(self.captured_bottom_label)

        # 4. Alt Butonlar (PGN Kopyala)
        btn_layout = QHBoxLayout()
        self.btn_copy_pgn = QPushButton("PGN Kopyala", self)
        self.btn_copy_pgn.clicked.connect(self._copy_pgn_to_clipboard)
        self.btn_copy_pgn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #eee;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
        btn_layout.addWidget(self.btn_copy_pgn)
        layout.addLayout(btn_layout)

    def update_history(self):
        """Hamle tablosunu ve alınan taşları günceller."""
        history = self.board_manager.move_history
        self.table.setRowCount(0)

        num_turns = (len(history) + 1) // 2
        self.table.setRowCount(num_turns)

        for i, record in enumerate(history):
            turn_idx = i // 2
            col_idx = 1 if (i % 2 == 0) else 2

            # Hamle numarası
            if col_idx == 1:
                item_no = QTableWidgetItem(f"{turn_idx + 1}.")
                item_no.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_no.setForeground(QColor(160, 160, 160))
                self.table.setItem(turn_idx, 0, item_no)

            # Hamle SAN metni
            item_move = QTableWidgetItem(record.san)
            item_move.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(turn_idx, col_idx, item_move)

        self.table.scrollToBottom()
        self._update_captured_pieces()

    def _update_captured_pieces(self):
        """Alınan taş gliflerini ve materyal avantajını gösterir."""
        captured = self.board_manager.get_captured_pieces()
        mat_diff = self.board_manager.get_material_difference()

        # Beyazın aldığı siyah taşlar (vektör unicode sembolleri)
        white_got = "".join(AssetLoader.UNICODE_GLYPHS.get((chess.BLACK, pt), "") for pt in sorted(captured['black'], reverse=True))
        # Siyahın aldığı beyaz taşlar
        black_got = "".join(AssetLoader.UNICODE_GLYPHS.get((chess.WHITE, pt), "") for pt in sorted(captured['white'], reverse=True))

        top_text = f"Siyah Kayıpları: {white_got}"
        if mat_diff > 0:
            top_text += f" (+{mat_diff} Beyaz)"
        self.captured_top_label.setText(top_text)

        bottom_text = f"Beyaz Kayıpları: {black_got}"
        if mat_diff < 0:
            bottom_text += f" (+{abs(mat_diff)} Siyah)"
        self.captured_bottom_label.setText(bottom_text)

    def _copy_pgn_to_clipboard(self):
        pgn = self.board_manager.get_pgn_string()
        QApplication.clipboard().setText(pgn)
        self.btn_copy_pgn.setText("Kopyalandı! ✓")
        self.btn_copy_pgn.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; border-radius: 4px; padding: 6px;")
        # 2 saniye sonra eski haline döndür
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.btn_copy_pgn.setText("PGN Kopyala")
        self.btn_copy_pgn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                color: #eee;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
        """)
