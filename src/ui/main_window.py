"""
Ana Uygulama Penceresi (Main Window).
Tüm satranç bileşenlerini, kontrolleri, saatleri, boyut modlarını (Mini/Standart/Mega) ve yapay zeka entegrasyonunu birleştirir.
"""
import os
import time
import random
import chess
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QToolBar, QStatusBar, QMessageBox,
    QFrame, QSplitter, QSizePolicy, QProgressBar
)
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, pyqtSlot

from ..core.board_manager import BoardManager
from ..core.timer_manager import ChessTimerManager
from ..core.stats_manager import StatsManager
from ..ai.ai_manager import AIManager
from ..ai.base_ai import AIMoveResult
from ..utils.asset_loader import AssetLoader
from ..utils.sound_player import SoundPlayer

from .chess_board_widget import ChessBoardWidget
from .eval_bar_widget import EvalBarWidget
from .move_history_widget import MoveHistoryWidget
from .ai_config_dialog import AIConfigDialog
from .game_settings_dialog import GameSettingsDialog
from .stats_dialog import StatsDialog
from .about_dialog import AboutDialog

class MainWindow(QMainWindow):
    """Satranç Oyunu Ana Penceresi."""

    def __init__(self, base_dir: str):
        super().__init__()
        self.base_dir = base_dir
        self.setWindowTitle("Satranç Oyunu - Modüler Yapay Zeka")
        
        # Varsayılan Oyun Ayarları
        self.game_settings = {
            "player_side": "white",         # 'white', 'black', 'random', 'human_vs_human'
            "initial_seconds": 600.0,      # 10 dk
            "increment_seconds": 0.0,
            "theme": "emerald",
            "screen_size": "standard",     # 'mini', 'standard', 'mega', 'fullscreen'
            "sound_enabled": True,
            "show_eval_bar": True
        }

        # Çekirdek ve Yardımcı Servisler
        self.board_manager = BoardManager()
        self.asset_loader = AssetLoader(self.base_dir)
        self.sound_player = SoundPlayer(self.asset_loader.sounds_dir, enabled=True, parent=self)
        self.timer_manager = ChessTimerManager(600.0, 0.0, parent=self)
        
        stats_path = os.path.join(self.base_dir, "config", "stats.json")
        self.stats_manager = StatsManager(stats_path)
        self.game_start_time = time.time()

        config_path = os.path.join(self.base_dir, "config", "ai_models.json")
        self.ai_manager = AIManager(config_path, parent=self)

        # Oyun Durumu Değişkenleri
        self.human_color = chess.WHITE     # Oyuncunun rengi (Beyaz veya Siyah)
        self.is_ai_game = True             # True: İnsan vs AI, False: İnsan vs İnsan
        self.game_active = False
        self.current_screen_mode = "standard"

        self._init_ui()
        self._setup_shortcuts()
        self._connect_signals()

        # Ekran boyutunu uygula
        self.set_screen_size(self.game_settings.get("screen_size", "standard"))

        # Yeni Oyunu Başlat
        self.start_new_game()

    def _init_ui(self):
        # 1. Üst Menü / Araç Çubuğu
        toolbar = QToolBar("Oyun Kontrolleri", self)
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.btn_new_game = QPushButton("♟ Yeni Oyun")
        self.btn_new_game.clicked.connect(self.start_new_game)
        toolbar.addWidget(self.btn_new_game)

        toolbar.addSeparator()

        lbl_ai = QLabel("  Yapay Zeka: ")
        lbl_ai.setFont(QFont("Sans Serif", 9, QFont.Weight.Bold))
        toolbar.addWidget(lbl_ai)

        self.cmb_ai_models = QComboBox()
        self.cmb_ai_models.setMinimumWidth(180)
        self.cmb_ai_models.currentIndexChanged.connect(self._on_ai_model_dropdown_changed)
        toolbar.addWidget(self.cmb_ai_models)

        self.btn_manage_ai = QPushButton("🤖 AI Yönet")
        self.btn_manage_ai.clicked.connect(self._open_ai_config_dialog)
        toolbar.addWidget(self.btn_manage_ai)

        toolbar.addSeparator()

        # EKRAN BOYUTU SEÇİCİ MENÜSÜ
        lbl_size = QLabel("  📐 Boyut: ")
        lbl_size.setFont(QFont("Sans Serif", 9, QFont.Weight.Bold))
        toolbar.addWidget(lbl_size)

        self.cmb_screen_size = QComboBox()
        self.cmb_screen_size.setMinimumWidth(170)
        self.cmb_screen_size.addItem("📱 Mini Boy (Ctrl+1)", "mini")
        self.cmb_screen_size.addItem("💻 Standart Boy (Ctrl+2)", "standard")
        self.cmb_screen_size.addItem("🖥️ Mega Boy (Ctrl+3)", "mega")
        self.cmb_screen_size.addItem("🔲 Tam Ekran (F11)", "fullscreen")
        self.cmb_screen_size.currentIndexChanged.connect(self._on_screen_size_dropdown_changed)
        toolbar.addWidget(self.cmb_screen_size)

        toolbar.addSeparator()

        self.btn_flip = QPushButton("🔄 Çevir")
        self.btn_flip.clicked.connect(self._toggle_flip_board)
        toolbar.addWidget(self.btn_flip)

        self.btn_stats = QPushButton("📊 İstatistik")
        self.btn_stats.clicked.connect(self._open_stats_dialog)
        toolbar.addWidget(self.btn_stats)

        self.btn_settings = QPushButton("⚙️ Ayarlar")
        self.btn_settings.clicked.connect(self._open_settings_dialog)
        toolbar.addWidget(self.btn_settings)

        self.btn_about = QPushButton("ℹ️ Hakkında")
        self.btn_about.clicked.connect(self._open_about_dialog)
        toolbar.addWidget(self.btn_about)

        self.btn_resign = QPushButton("🏳 Terk Et")
        self.btn_resign.clicked.connect(self._on_resign)
        toolbar.addWidget(self.btn_resign)

        # 2. Ana Gövde Düzeni
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # SOL/ORTA ALAN: Mini Başlık + Tahta/Eval Bar + Mini Alt Bilgi
        board_vertical_layout = QVBoxLayout()
        board_vertical_layout.setSpacing(6)

        # MİNİ MOD ÜST BİLGİ ŞERİDİ (Mini boyutta görünür)
        self.mini_top_bar = QFrame()
        self.mini_top_bar.setStyleSheet("background-color: #242424; border-radius: 6px; padding: 4px 8px;")
        l_mini_top = QHBoxLayout(self.mini_top_bar)
        l_mini_top.setContentsMargins(6, 2, 6, 2)
        
        self.lbl_mini_opp = QLabel("🤖 Rakip: 10:00")
        self.lbl_mini_opp.setStyleSheet("color: #64b5f6; font-weight: bold; font-size: 12px;")
        self.lbl_mini_turn = QLabel("Beyaz'ın Sırası")
        self.lbl_mini_turn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_mini_turn.setStyleSheet("color: #ffeb3b; font-weight: bold; font-size: 12px;")
        self.lbl_mini_ply = QLabel("👤 Siz: 10:00")
        self.lbl_mini_ply.setStyleSheet("color: #81c784; font-weight: bold; font-size: 12px;")
        
        l_mini_top.addWidget(self.lbl_mini_opp)
        l_mini_top.addStretch()
        l_mini_top.addWidget(self.lbl_mini_turn)
        l_mini_top.addStretch()
        l_mini_top.addWidget(self.lbl_mini_ply)
        self.mini_top_bar.hide()
        board_vertical_layout.addWidget(self.mini_top_bar)

        # TAHTA + EVAL BAR
        board_container = QHBoxLayout()
        board_container.setSpacing(8)

        self.eval_bar = EvalBarWidget(self)
        board_container.addWidget(self.eval_bar)

        self.chess_board = ChessBoardWidget(self.board_manager, self.asset_loader, self)
        board_container.addWidget(self.chess_board, 1)

        board_vertical_layout.addLayout(board_container, 1)

        # MİNİ MOD ALT BİLGİ ŞERİDİ (Son hamle & Persona yorumu)
        self.mini_bottom_bar = QFrame()
        self.mini_bottom_bar.setStyleSheet("background-color: #242424; border-radius: 6px; padding: 4px 8px;")
        l_mini_bot = QVBoxLayout(self.mini_bottom_bar)
        l_mini_bot.setContentsMargins(6, 4, 6, 4)
        l_mini_bot.setSpacing(2)

        self.lbl_mini_last_move = QLabel("Hamle bekleniyor...")
        self.lbl_mini_last_move.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        self.lbl_mini_ai_thought = QLabel("“İyi olan kazansın!”")
        self.lbl_mini_ai_thought.setStyleSheet("color: #90caf9; font-size: 11px; font-style: italic;")
        self.lbl_mini_ai_thought.setWordWrap(True)

        l_mini_bot.addWidget(self.lbl_mini_last_move)
        l_mini_bot.addWidget(self.lbl_mini_ai_thought)
        self.mini_bottom_bar.hide()
        board_vertical_layout.addWidget(self.mini_bottom_bar)

        main_layout.addLayout(board_vertical_layout, 3)

        # SAĞ ALAN: Tam Kenar Paneli (Oyuncu Kartları, Saatler, Hamle Geçmişi ve AI Yorum Baloncuğu)
        self.right_panel_widget = QWidget()
        right_panel = QVBoxLayout(self.right_panel_widget)
        right_panel.setContentsMargins(0, 0, 0, 0)
        right_panel.setSpacing(10)

        # ÜST OYUNCU KARTI (Rakip / AI)
        self.card_opponent = QFrame()
        self.card_opponent.setStyleSheet("background-color: #242424; border-radius: 8px; padding: 6px;")
        l_opp = QHBoxLayout(self.card_opponent)
        
        self.lbl_opp_name = QLabel("Yapay Zeka")
        self.lbl_opp_name.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        self.lbl_opp_name.setStyleSheet("color: #ffffff;")
        
        self.lbl_opp_clock = QLabel("10:00")
        self.lbl_opp_clock.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        self.lbl_opp_clock.setStyleSheet("background-color: #1a1a1a; color: #64b5f6; padding: 4px 10px; border-radius: 6px;")

        l_opp.addWidget(self.lbl_opp_name)
        l_opp.addStretch()
        l_opp.addWidget(self.lbl_opp_clock)
        right_panel.addWidget(self.card_opponent)

        # AI Düşünce & Yorum Baloncuğu (Persona)
        self.ai_thought_box = QFrame()
        self.ai_thought_box.setStyleSheet("background-color: #1e2638; border-left: 4px solid #4a90e2; border-radius: 4px; padding: 6px;")
        l_thought = QVBoxLayout(self.ai_thought_box)
        l_thought.setContentsMargins(6, 4, 6, 4)
        
        self.lbl_ai_status = QLabel("Yapay Zeka hazır.")
        self.lbl_ai_status.setStyleSheet("color: #90caf9; font-size: 11px; font-weight: bold;")
        self.lbl_ai_thought = QLabel("“İyi olan kazansın!”")
        self.lbl_ai_thought.setWordWrap(True)
        self.lbl_ai_thought.setStyleSheet("color: #e0e0e0; font-size: 12px; font-style: italic;")

        l_thought.addWidget(self.lbl_ai_status)
        l_thought.addWidget(self.lbl_ai_thought)
        right_panel.addWidget(self.ai_thought_box)

        # ORTA: Hamle Tablosu & Alınan Taşlar
        self.move_history_widget = MoveHistoryWidget(self.board_manager, self.asset_loader, self)
        right_panel.addWidget(self.move_history_widget, 1)

        # ALT OYUNCU KARTI (İnsan / Siz)
        self.card_player = QFrame()
        self.card_player.setStyleSheet("background-color: #242424; border-radius: 8px; padding: 6px;")
        l_ply = QHBoxLayout(self.card_player)
        
        self.lbl_ply_name = QLabel("Oyuncu (Siz)")
        self.lbl_ply_name.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        self.lbl_ply_name.setStyleSheet("color: #ffffff;")
        
        self.lbl_ply_clock = QLabel("10:00")
        self.lbl_ply_clock.setFont(QFont("Monospace", 14, QFont.Weight.Bold))
        self.lbl_ply_clock.setStyleSheet("background-color: #1a1a1a; color: #81c784; padding: 4px 10px; border-radius: 6px;")

        l_ply.addWidget(self.lbl_ply_name)
        l_ply.addStretch()
        l_ply.addWidget(self.lbl_ply_clock)
        right_panel.addWidget(self.card_player)

        # Oyun Durum Bildirim Alanı
        self.lbl_game_status = QLabel("Yeni Oyun Başladı.")
        self.lbl_game_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_game_status.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        self.lbl_game_status.setStyleSheet("background-color: #333333; color: #ffeb3b; padding: 6px; border-radius: 4px;")
        right_panel.addWidget(self.lbl_game_status)

        main_layout.addWidget(self.right_panel_widget, 1)

        # 3. Durum Çubuğu (Status Bar)
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")

        # Model listesini doldur
        self._refresh_ai_dropdown()

    def _setup_shortcuts(self):
        """Klavye kısayollarını ayarla."""
        QShortcut(QKeySequence("Ctrl+1"), self, lambda: self.set_screen_size("mini"))
        QShortcut(QKeySequence("Ctrl+2"), self, lambda: self.set_screen_size("standard"))
        QShortcut(QKeySequence("Ctrl+3"), self, lambda: self.set_screen_size("mega"))
        QShortcut(QKeySequence("Ctrl+I"), self, self._open_stats_dialog)
        QShortcut(QKeySequence("Ctrl+H"), self, self._open_about_dialog)
        QShortcut(QKeySequence("F1"), self, self._open_about_dialog)
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)

    def _connect_signals(self):
        # Tahta Sinyalleri
        self.chess_board.move_made.connect(self._on_user_move_made)

        # Zamanlayıcı Sinyalleri
        self.timer_manager.time_updated.connect(self._on_time_updated)
        self.timer_manager.flag_dropped.connect(self._on_time_flag_dropped)

        # AI Yönetici Sinyalleri
        self.ai_manager.calculation_started.connect(self._on_ai_started)
        self.ai_manager.move_ready.connect(self._on_ai_move_ready)
        self.ai_manager.calculation_failed.connect(self._on_ai_failed)
        self.ai_manager.models_updated.connect(self._refresh_ai_dropdown)

    # --- Ekran Boyutu Yönetimi (Mini, Standart, Mega, Tam Ekran) ---

    def set_screen_size(self, mode: str):
        """Ekran boyutunu ve düzenini değiştirir."""
        self.current_screen_mode = mode
        
        # ComboBox seçimini güncelle
        idx = self.cmb_screen_size.findData(mode)
        if idx >= 0 and self.cmb_screen_size.currentIndex() != idx:
            self.cmb_screen_size.blockSignals(True)
            self.cmb_screen_size.setCurrentIndex(idx)
            self.cmb_screen_size.blockSignals(False)

        if mode == "fullscreen":
            self.setMinimumSize(800, 550)
            self.right_panel_widget.show()
            self.mini_top_bar.hide()
            self.mini_bottom_bar.hide()
            self.eval_bar.setVisible(self.game_settings.get("show_eval_bar", True))
            self.showFullScreen()
            return

        if self.isFullScreen():
            self.showNormal()

        if mode == "mini":
            # 📱 MİNİ BOY (Kompakt ve Tahta Odaklı)
            self.right_panel_widget.hide()
            self.mini_top_bar.show()
            self.mini_bottom_bar.show()
            self.eval_bar.hide()
            self.setMinimumSize(360, 440)
            self.resize(460, 580)
        elif mode == "mega":
            # 🖥️ MEGA BOY (Geniş HD Ekran)
            self.mini_top_bar.hide()
            self.mini_bottom_bar.hide()
            self.right_panel_widget.show()
            self.eval_bar.setVisible(self.game_settings.get("show_eval_bar", True))
            self.setMinimumSize(1100, 750)
            self.resize(1550, 950)
        else:  # standard
            # 💻 STANDART BOY (Dengeli)
            self.mini_top_bar.hide()
            self.mini_bottom_bar.hide()
            self.right_panel_widget.show()
            self.eval_bar.setVisible(self.game_settings.get("show_eval_bar", True))
            self.setMinimumSize(800, 550)
            self.resize(1080, 750)

        self._update_status_display()

    def _on_screen_size_dropdown_changed(self, index: int):
        mode = self.cmb_screen_size.itemData(index)
        if mode:
            self.set_screen_size(mode)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.set_screen_size("standard")
        else:
            self.set_screen_size("fullscreen")

    # --- Oyun Başlatma ve Yönetim ---

    def start_new_game(self):
        """Yeni bir satranç oyunu başlatır."""
        self.board_manager.reset()
        self.chess_board.set_last_move(None)
        self.chess_board.clear_selection()
        
        # Taraf Seçimi
        side_pref = self.game_settings.get("player_side", "white")
        if side_pref == "white":
            self.human_color = chess.WHITE
            self.is_ai_game = True
        elif side_pref == "black":
            self.human_color = chess.BLACK
            self.is_ai_game = True
        elif side_pref == "random":
            self.human_color = random.choice([chess.WHITE, chess.BLACK])
            self.is_ai_game = True
        else:  # human_vs_human
            self.human_color = chess.WHITE
            self.is_ai_game = False

        # Tahta yönünü ayarla
        should_flip = (self.human_color == chess.BLACK and self.is_ai_game)
        self.chess_board.set_flipped(should_flip)
        self.eval_bar.set_flipped(should_flip)

        # Saatleri Yapılandır
        init_sec = self.game_settings.get("initial_seconds", 600.0)
        inc_sec = self.game_settings.get("increment_seconds", 0.0)
        self.timer_manager.configure(init_sec, inc_sec)
        self.game_start_time = time.time()

        # Arayüzü Güncelle
        self.eval_bar.set_evaluation(0.0)
        self.move_history_widget.update_history()
        self.game_active = True
        self._update_player_card_labels()
        self._update_status_display()

        self.chess_board.interactive = True
        self.chess_board.update()

        # Eğer insan Siyah ise, AI ilk hamleyi (Beyaz) yapsın
        if self.is_ai_game and self.human_color == chess.BLACK:
            self._trigger_ai_turn()

    def _update_player_card_labels(self):
        active_ai = self.ai_manager.get_active_model_info()
        ai_name = active_ai.get("name", "Yapay Zeka") if active_ai else "Yapay Zeka"

        if not self.is_ai_game:
            p1_str = "Oyuncu 1 (Beyaz)"
            p2_str = "Oyuncu 2 (Siyah)"
            self.lbl_opp_name.setText(p2_str if not self.chess_board.flipped else p1_str)
            self.lbl_ply_name.setText(p1_str if not self.chess_board.flipped else p2_str)
            self.lbl_mini_opp.setText(f"👤 {p2_str}")
            self.lbl_mini_ply.setText(f"👤 {p1_str}")
        else:
            if self.human_color == chess.WHITE:
                self.lbl_opp_name.setText(f"🤖 {ai_name} (Siyah)")
                self.lbl_ply_name.setText("👤 Siz (Beyaz)")
                self.lbl_mini_opp.setText(f"🤖 {ai_name}")
                self.lbl_mini_ply.setText("👤 Siz (Beyaz)")
            else:
                self.lbl_opp_name.setText(f"🤖 {ai_name} (Beyaz)")
                self.lbl_ply_name.setText("👤 Siz (Siyah)")
                self.lbl_mini_opp.setText(f"🤖 {ai_name}")
                self.lbl_mini_ply.setText("👤 Siz (Siyah)")

    def _on_user_move_made(self, move: chess.Move):
        """Kullanıcı tahtada bir hamle yaptığında tetiklenir."""
        if not self.game_active:
            return

        # Sadece oyuncunun sırasıysa izin ver (AI oyunlarında)
        if self.is_ai_game and self.board_manager.board.turn != self.human_color:
            return

        record = self.board_manager.make_move(move)
        if record:
            self.chess_board.set_last_move(move)
            self._play_move_sound(record)
            self.move_history_widget.update_history()
            
            # Mini mod son hamle metni
            turn_no = (len(self.board_manager.move_history) + 1) // 2
            side_str = "Beyaz" if record.color else "Siyah"
            self.lbl_mini_last_move.setText(f"{turn_no}. {side_str}: {record.san}")

            # Saati değiştir
            self.timer_manager.switch_turn(self.board_manager.turn)
            if not self.timer_manager.is_running and not self.timer_manager.is_unlimited:
                self.timer_manager.start()

            self._update_status_display()

            # Oyun bitti mi kontrol et
            is_over, reason, _ = self.board_manager.get_game_status()
            if is_over:
                self._handle_game_over(reason)
                return

            # AI Sırası
            if self.is_ai_game and self.board_manager.board.turn != self.human_color:
                self._trigger_ai_turn()

    def _trigger_ai_turn(self):
        """Yapay zekanın hamle yapmasını talep eder."""
        if not self.game_active:
            return
        
        self.chess_board.interactive = False
        self.lbl_ai_status.setText("⏳ Düşünüyor...")
        self.lbl_mini_ai_thought.setText("⏳ Yapay Zeka düşünüyor...")
        history_san = [r.san for r in self.board_manager.move_history]
        self.ai_manager.request_move(self.board_manager.board, history_san)

    @pyqtSlot(str)
    def _on_ai_started(self, model_name: str):
        self.lbl_ai_status.setText(f"🤖 {model_name} analiz ediyor...")
        self.lbl_mini_ai_thought.setText(f"🤖 {model_name} analiz ediyor...")

    @pyqtSlot(object)
    def _on_ai_move_ready(self, result: AIMoveResult):
        """Yapay zeka hamlesini tamamladığında tetiklenir."""
        if not self.game_active:
            return

        self.chess_board.interactive = True
        self.lbl_ai_status.setText("✓ Hamle yapıldı.")
        
        if result.thoughts:
            self.lbl_ai_thought.setText(f"“{result.thoughts}”")
            self.lbl_mini_ai_thought.setText(f"“{result.thoughts}”")

        if result.eval_score is not None or result.mate_in is not None:
            self.eval_bar.set_evaluation(result.eval_score, result.mate_in)

        # Hamleyi tahtada uygula
        record = self.board_manager.make_uci_move(result.move_uci)
        if record:
            move = chess.Move.from_uci(result.move_uci)
            self.chess_board.set_last_move(move)
            self._play_move_sound(record)
            self.move_history_widget.update_history()

            turn_no = (len(self.board_manager.move_history) + 1) // 2
            side_str = "Beyaz" if record.color else "Siyah"
            self.lbl_mini_last_move.setText(f"{turn_no}. {side_str}: {record.san}")

            self.timer_manager.switch_turn(self.board_manager.turn)
            self._update_status_display()

            is_over, reason, _ = self.board_manager.get_game_status()
            if is_over:
                self._handle_game_over(reason)

    @pyqtSlot(str)
    def _on_ai_failed(self, error_msg: str):
        self.chess_board.interactive = True
        self.lbl_ai_status.setText("⚠️ AI Hatası!")
        self.lbl_ai_thought.setText(f"Hata: {error_msg}")
        self.lbl_mini_ai_thought.setText(f"Hata: {error_msg}")
        QMessageBox.warning(self, "Yapay Zeka Hatası", f"Yapay zeka hamle üretemedi:\n{error_msg}")

    def _play_move_sound(self, record):
        if not self.game_settings.get("sound_enabled", True):
            return

        if record.is_mate or record.is_check:
            self.sound_player.play("check")
        elif record.captured_piece_type is not None:
            self.sound_player.play("capture")
        else:
            self.sound_player.play("move")

    def _update_status_display(self):
        is_over, status_text, _ = self.board_manager.get_game_status()
        self.lbl_game_status.setText(status_text)
        self.lbl_mini_turn.setText(status_text)
        self.status_bar.showMessage(f"FEN: {self.board_manager.current_fen}")

    def _handle_game_over(self, reason: str):
        self.game_active = False
        self.timer_manager.stop()
        self.chess_board.interactive = False
        self.sound_player.play("game_over")
        self.lbl_game_status.setText(f"Oyun Bitti: {reason}")
        self.lbl_mini_turn.setText(f"Oyun Bitti: {reason}")

        # İstatistikleri kaydet
        duration = max(1.0, time.time() - getattr(self, "game_start_time", time.time()))
        moves_count = len(self.board_manager.move_history)
        player_color_str = "Beyaz" if self.human_color == chess.WHITE else "Siyah"
        active_ai = self.ai_manager.get_active_model_info()
        opp_name = active_ai.get("name", "Yapay Zeka") if self.is_ai_game else "2. Oyuncu"

        if "Berabere" in reason or "Pat" in reason or "Yetersiz" in reason:
            result = "draw"
        elif f"{player_color_str} kazandı" in reason:
            result = "win"
        else:
            result = "loss"

        self.stats_manager.record_match(
            opponent_name=opp_name,
            result=result,
            reason=reason,
            duration_seconds=duration,
            moves_count=moves_count,
            player_color=player_color_str
        )

        QMessageBox.information(self, "Oyun Bitti", reason)

    def _open_stats_dialog(self):
        """İstatistikler penceresini açar."""
        dlg = StatsDialog(self.stats_manager, self)
        dlg.exec()

    def _open_about_dialog(self):
        """Hakkında ve İletişim penceresini açar."""
        about_path = os.path.join(self.base_dir, "config", "about.json")
        dlg = AboutDialog(about_path, self)
        dlg.exec()

    # --- Zamanlayıcı Olayları ---

    def _on_time_updated(self, w_time: float, b_time: float):
        w_str = ChessTimerManager.format_time(w_time)
        b_str = ChessTimerManager.format_time(b_time)

        if not self.chess_board.flipped:
            self.lbl_ply_clock.setText(w_str)
            self.lbl_opp_clock.setText(b_str)
            self.lbl_mini_ply.setText(f"👤 {w_str}")
            self.lbl_mini_opp.setText(f"🤖 {b_str}")
        else:
            self.lbl_ply_clock.setText(b_str)
            self.lbl_opp_clock.setText(w_str)
            self.lbl_mini_ply.setText(f"👤 {b_str}")
            self.lbl_mini_opp.setText(f"🤖 {w_str}")

    def _on_time_flag_dropped(self, loser: str):
        winner = "Siyah" if loser == "white" else "Beyaz"
        self._handle_game_over(f"Süre Doldu! {winner} zamanla kazandı.")

    # --- Araç Çubuğu ve Diyalog İşlemleri ---

    def _refresh_ai_dropdown(self):
        self.cmb_ai_models.blockSignals(True)
        self.cmb_ai_models.clear()
        for m in self.ai_manager.models_data:
            self.cmb_ai_models.addItem(f"[{m.get('type', 'builtin').upper()}] {m.get('name')}", m.get("id"))
        
        # Aktif modeli seç
        idx = self.cmb_ai_models.findData(self.ai_manager.active_model_id)
        if idx >= 0:
            self.cmb_ai_models.setCurrentIndex(idx)
        self.cmb_ai_models.blockSignals(False)
        self._update_player_card_labels()

    def _on_ai_model_dropdown_changed(self, index: int):
        model_id = self.cmb_ai_models.itemData(index)
        if model_id:
            self.ai_manager.set_active_model(model_id)
            self._update_player_card_labels()

    def _open_ai_config_dialog(self):
        dlg = AIConfigDialog(self.ai_manager, self)
        dlg.exec()
        self._refresh_ai_dropdown()

    def _open_settings_dialog(self):
        dlg = GameSettingsDialog(self.game_settings, self)
        if dlg.exec():
            self.game_settings = dlg.settings
            self.chess_board.set_theme(self.game_settings.get("theme", "emerald"))
            self.sound_player.set_enabled(self.game_settings.get("sound_enabled", True))
            self.eval_bar.setVisible(self.game_settings.get("show_eval_bar", True))
            
            # Ekran boyutu değiştiyse uygula
            new_size = self.game_settings.get("screen_size", "standard")
            if new_size != self.current_screen_mode:
                self.set_screen_size(new_size)

            reply = QMessageBox.question(
                self, "Yeni Oyun?",
                "Ayarların geçerli olması için yeni bir oyun başlatılsın mı?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.start_new_game()

    def _toggle_flip_board(self):
        new_flipped = not self.chess_board.flipped
        self.chess_board.set_flipped(new_flipped)
        self.eval_bar.set_flipped(new_flipped)
        self._update_player_card_labels()
        # Saatleri de güncelle
        self._on_time_updated(self.timer_manager.white_time, self.timer_manager.black_time)

    def _on_resign(self):
        if not self.game_active:
            return
        reply = QMessageBox.question(
            self, "Terk Onayı",
            "Oyunu terk etmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            winner = "Siyah" if self.human_color == chess.WHITE else "Beyaz"
            self._handle_game_over(f"Oyuncu terk etti. {winner} kazandı.")

    def closeEvent(self, event):
        self.timer_manager.stop()
        self.ai_manager.cleanup()
        event.accept()
