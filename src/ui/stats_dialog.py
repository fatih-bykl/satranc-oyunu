"""
Oyun İstatistikleri ve Maç Geçmişi Penceresi (Stats Dialog).
Kullanıcının maç sayılarını, kazanma oranını, oyun sürelerini ve detaylı maç geçmişini gösterir.
İstatistikleri sıfırlama seçeneği sunar.
"""
from typing import Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFrame, QWidget
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

from ..core.stats_manager import StatsManager

class StatCard(QFrame):
    """Şık istatistik bilgi kartı."""
    def __init__(self, title: str, value: str, subtext: str = "", color_hex: str = "#81c784", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #262626;
                border: 1px solid #3d3d3d;
                border-top: 3px solid {color_hex};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #aaaaaa; font-size: 11px; font-weight: bold;")
        
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(f"color: {color_hex}; font-size: 20px; font-weight: bold;")
        
        self.lbl_subtext = QLabel(subtext)
        self.lbl_subtext.setStyleSheet("color: #888888; font-size: 11px;")
        if not subtext:
            self.lbl_subtext.hide()

        layout.addWidget(lbl_title)
        layout.addWidget(self.lbl_value)
        layout.addWidget(self.lbl_subtext)

    def set_content(self, value: str, subtext: str = ""):
        self.lbl_value.setText(value)
        if subtext:
            self.lbl_subtext.setText(subtext)
            self.lbl_subtext.show()
        else:
            self.lbl_subtext.hide()

class StatsDialog(QDialog):
    """İstatistikler ve Maç Geçmişi Penceresi."""

    def __init__(self, stats_manager: StatsManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.stats_manager = stats_manager
        self.setWindowTitle("📊 Satranç Oyun İstatistikleri")
        self.resize(780, 580)
        self.setMinimumSize(600, 450)

        self._init_ui()
        self.refresh_display()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # 1. Başlık
        header_layout = QHBoxLayout()
        lbl_header = QLabel("🏆 Performans ve Oyun Özeti", self)
        lbl_header.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
        lbl_header.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(lbl_header)
        header_layout.addStretch()

        self.btn_reset = QPushButton("🗑️ İstatistikleri Sıfırla")
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #5c2424;
                color: #ffcdd2;
                border: 1px solid #7a3333;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7a3333;
                color: #ffffff;
            }
        """)
        self.btn_reset.clicked.connect(self._on_reset_clicked)
        header_layout.addWidget(self.btn_reset)
        main_layout.addLayout(header_layout)

        # 2. İstatistik Özet Kartları Izgarası (2x3 Grid)
        grid_cards = QGridLayout()
        grid_cards.setSpacing(10)

        self.card_total = StatCard("TOPLAM MAÇ", "0", "Tamamlanan Oyun", "#64b5f6")
        self.card_winrate = StatCard("KAZANMA ORANI", "%0.0", "0G - 0M - 0B", "#81c784")
        self.card_time = StatCard("TOPLAM SÜRE", "0 dk", "Ortalama: --", "#ffb74d")
        self.card_fastest = StatCard("EN HIZLI GALİBİYET", "--", "Rekor Süre", "#ba68c8")
        self.card_moves = StatCard("TOPLAM HAMLE", "0", "Tahtada Oynanan", "#4dd0e1")
        self.card_record = StatCard("SONUÇ DAĞILIMI", "0 / 0 / 0", "Galibiyet / Mağlubiyet / Berabere", "#e57373")

        grid_cards.addWidget(self.card_total, 0, 0)
        grid_cards.addWidget(self.card_winrate, 0, 1)
        grid_cards.addWidget(self.card_time, 0, 2)
        grid_cards.addWidget(self.card_fastest, 1, 0)
        grid_cards.addWidget(self.card_moves, 1, 1)
        grid_cards.addWidget(self.card_record, 1, 2)

        main_layout.addLayout(grid_cards)

        # 3. Son Maçlar Geçmişi
        lbl_history = QLabel("📜 Son Maçlar Geçmişi", self)
        lbl_history.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_history.setStyleSheet("color: #e0e0e0; margin-top: 6px;")
        main_layout.addWidget(lbl_history)

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels([
            "Tarih", "Rakip", "Taraf", "Sonuç", "Bitiş Nedeni", "Süre"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #222222;
                color: #f0f0f0;
                gridline-color: #333333;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #cccccc;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #3c3c3c;
            }
        """)
        main_layout.addWidget(self.table, 1)

        # Alt Buton
        bottom_layout = QHBoxLayout()
        btn_close = QPushButton("Kapat", self)
        btn_close.setStyleSheet("background-color: #333333; color: white; padding: 8px 24px; font-weight: bold;")
        btn_close.clicked.connect(self.accept)
        bottom_layout.addStretch()
        bottom_layout.addWidget(btn_close)
        main_layout.addLayout(bottom_layout)

    def refresh_display(self):
        """İstatistik kartlarını ve geçmiş tablosunu günceller."""
        data = self.stats_manager.data
        total_games = data.get("total_games", 0)
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        draws = data.get("draws", 0)
        total_time = data.get("total_play_time_seconds", 0.0)
        total_moves = data.get("total_moves_played", 0)
        fastest_win = data.get("fastest_win_seconds")
        win_rate = self.stats_manager.win_rate
        avg_time = self.stats_manager.average_duration_seconds

        # Kartları Güncelle
        self.card_total.set_content(str(total_games), f"{wins + losses + draws} Oyun Kaydedildi")
        self.card_winrate.set_content(f"%{win_rate:.1f}", f"🏆 {wins} Galibiyet - {losses} Mağlubiyet")
        self.card_time.set_content(
            StatsManager.format_duration(total_time),
            f"Ortalama: {StatsManager.format_duration(avg_time)}"
        )
        self.card_fastest.set_content(
            StatsManager.format_duration(fastest_win) if fastest_win else "--",
            "En kısa kazanç" if fastest_win else "Henüz galibiyet yok"
        )
        self.card_moves.set_content(f"{total_moves:,}", f"Maç Başı: {int(total_moves / max(1, total_games))} hamle")
        self.card_record.set_content(f"{wins}G  {losses}M  {draws}B", "W / L / D")

        # Tabloyu Güncelle
        matches = data.get("matches", [])
        self.table.setRowCount(len(matches))

        for row, m in enumerate(matches):
            # Tarih
            it_date = QTableWidgetItem(m.get("date", ""))
            it_date.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, it_date)

            # Rakip
            it_opp = QTableWidgetItem(m.get("opponent", "Bilinmeyen"))
            self.table.setItem(row, 1, it_opp)

            # Taraf
            it_side = QTableWidgetItem(m.get("player_color", "Beyaz"))
            it_side.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 2, it_side)

            # Sonuç (Renkli)
            res = m.get("result", "draw")
            if res == "win":
                it_res = QTableWidgetItem("✓ Galibiyet")
                it_res.setForeground(QColor("#81c784"))
            elif res == "loss":
                it_res = QTableWidgetItem("✗ Mağlubiyet")
                it_res.setForeground(QColor("#e57373"))
            else:
                it_res = QTableWidgetItem("= Berabere")
                it_res.setForeground(QColor("#ffb74d"))
            it_res.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, it_res)

            # Bitiş Nedeni
            it_reason = QTableWidgetItem(f"{m.get('reason', '')} ({m.get('moves_count', 0)} hamle)")
            self.table.setItem(row, 4, it_reason)

            # Süre
            dur_str = StatsManager.format_duration(m.get("duration_seconds", 0.0))
            it_dur = QTableWidgetItem(dur_str)
            it_dur.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 5, it_dur)

    def _on_reset_clicked(self):
        reply = QMessageBox.question(
            self, "İstatistikleri Sıfırla",
            "Tüm oyun istatistiklerini ve geçmiş kayıtları kalıcı olarak silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.stats_manager.reset_stats()
            self.refresh_display()
            QMessageBox.information(self, "Bilgi", "İstatistikler başarıyla sıfırlandı!")
