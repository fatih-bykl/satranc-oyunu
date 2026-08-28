"""
Oyun ve Tahta Ayarları Penceresi (Game Settings Dialog).
Süre formatı, oynanacak taraf (Beyaz/Siyah), tema ve ses seçeneklerini yönetir.
"""
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QPushButton, QGroupBox, QFormLayout, QWidget
)
from PyQt6.QtCore import Qt

class GameSettingsDialog(QDialog):
    """Oyun ayarları penceresi."""

    def __init__(self, current_settings: Dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Oyun ve Tahta Ayarları")
        self.resize(450, 420)
        self.settings = dict(current_settings)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 1. Oyun Modu ve Taraf
        grp_mode = QGroupBox("Oyun Modu ve Taraf")
        f_mode = QFormLayout(grp_mode)

        self.cmb_player_side = QComboBox()
        self.cmb_player_side.addItems([
            "Beyaz Olarak Oyna (AI Siyah)",
            "Siyah Olarak Oyna (AI Beyaz)",
            "Rastgele Taraf",
            "İki Kişilik Yerel Oyun (İnsan vs İnsan)"
        ])
        # Mevcut tarafa göre seç
        side = self.settings.get("player_side", "white")
        if side == "white":
            self.cmb_player_side.setCurrentIndex(0)
        elif side == "black":
            self.cmb_player_side.setCurrentIndex(1)
        elif side == "random":
            self.cmb_player_side.setCurrentIndex(2)
        else:
            self.cmb_player_side.setCurrentIndex(3)
        f_mode.addRow("Oyuncu Tarafı:", self.cmb_player_side)

        layout.addWidget(grp_mode)

        # 2. Süre Ayarları
        grp_time = QGroupBox("Zaman Kontrolü (Satranç Saati)")
        f_time = QFormLayout(grp_time)

        self.cmb_time_preset = QComboBox()
        self.cmb_time_preset.addItems([
            "Süresiz (Rahat Oyun)",
            "Bullet 1 dk + 1 sn",
            "Blitz 3 dk + 2 sn",
            "Blitz 5 dk + 0 sn",
            "Rapid 10 dk + 0 sn",
            "Rapid 15 dk + 10 sn",
            "Klasik 30 dk + 0 sn",
            "Özel Süre Belirle"
        ])
        self.cmb_time_preset.currentIndexChanged.connect(self._on_time_preset_changed)
        f_time.addRow("Süre Şablonu:", self.cmb_time_preset)

        h_custom = QHBoxLayout()
        self.spin_custom_min = QSpinBox()
        self.spin_custom_min.setRange(1, 180)
        self.spin_custom_min.setValue(10)
        self.spin_custom_min.setSuffix(" dk")

        self.spin_custom_inc = QSpinBox()
        self.spin_custom_inc.setRange(0, 60)
        self.spin_custom_inc.setValue(0)
        self.spin_custom_inc.setSuffix(" sn artırma")

        h_custom.addWidget(self.spin_custom_min)
        h_custom.addWidget(self.spin_custom_inc)
        f_time.addRow("Özel Değerler:", h_custom)

        layout.addWidget(grp_time)

        # 3. Görsel ve Ses Ayarları
        grp_visual = QGroupBox("Görünüm ve Ses")
        f_visual = QFormLayout(grp_visual)

        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems([
            "Zümrüt Yeşili (emerald)",
            "Klasik Ahşap (wood)",
            "Okyanus Mavisi (ocean)",
            "Koyu Gece (charcoal)"
        ])
        current_theme = self.settings.get("theme", "emerald")
        theme_map = {"emerald": 0, "wood": 1, "ocean": 2, "charcoal": 3}
        self.cmb_theme.setCurrentIndex(theme_map.get(current_theme, 0))
        f_visual.addRow("Tahta Rengi:", self.cmb_theme)

        self.cmb_screen_size = QComboBox()
        self.cmb_screen_size.addItems([
            "📱 Mini Boy (Kompakt Mod)",
            "💻 Standart Boy (Normal Mod)",
            "🖥️ Mega Boy (Büyük Ekran Modu)",
            "🔲 Tam Ekran"
        ])
        cur_size = self.settings.get("screen_size", "standard")
        size_map = {"mini": 0, "standard": 1, "mega": 2, "fullscreen": 3}
        self.cmb_screen_size.setCurrentIndex(size_map.get(cur_size, 1))
        f_visual.addRow("Ekran Boyutu:", self.cmb_screen_size)

        self.chk_sound = QCheckBox("Hamle ve uyarı seslerini çal")
        self.chk_sound.setChecked(self.settings.get("sound_enabled", True))
        f_visual.addRow("", self.chk_sound)

        self.chk_eval_bar = QCheckBox("Değerlendirme çubuğunu (Eval Bar) göster")
        self.chk_eval_bar.setChecked(self.settings.get("show_eval_bar", True))
        f_visual.addRow("", self.chk_eval_bar)

        layout.addWidget(grp_visual)

        # Alt Butonlar
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Kaydet ve Uygula")
        btn_save.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        btn_save.clicked.connect(self._save_settings)
        btn_cancel = QPushButton("İptal")
        btn_cancel.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        # Preset indexini mevcut süreye göre ayarla
        self._match_preset()

    def _match_preset(self):
        init_sec = self.settings.get("initial_seconds", 600)
        inc_sec = self.settings.get("increment_seconds", 0)

        if init_sec <= 0:
            self.cmb_time_preset.setCurrentIndex(0)
        elif init_sec == 60 and inc_sec == 1:
            self.cmb_time_preset.setCurrentIndex(1)
        elif init_sec == 180 and inc_sec == 2:
            self.cmb_time_preset.setCurrentIndex(2)
        elif init_sec == 300 and inc_sec == 0:
            self.cmb_time_preset.setCurrentIndex(3)
        elif init_sec == 600 and inc_sec == 0:
            self.cmb_time_preset.setCurrentIndex(4)
        elif init_sec == 900 and inc_sec == 10:
            self.cmb_time_preset.setCurrentIndex(5)
        elif init_sec == 1800 and inc_sec == 0:
            self.cmb_time_preset.setCurrentIndex(6)
        else:
            self.cmb_time_preset.setCurrentIndex(7)
            self.spin_custom_min.setValue(max(1, int(init_sec // 60)))
            self.spin_custom_inc.setValue(int(inc_sec))

    def _on_time_preset_changed(self, idx: int):
        is_custom = (idx == 7)
        self.spin_custom_min.setEnabled(is_custom)
        self.spin_custom_inc.setEnabled(is_custom)

    def _save_settings(self):
        # Taraf
        side_idx = self.cmb_player_side.currentIndex()
        sides = ["white", "black", "random", "human_vs_human"]
        self.settings["player_side"] = sides[side_idx]

        # Süre
        preset_idx = self.cmb_time_preset.currentIndex()
        preset_times = [
            (0, 0),        # Süresiz
            (60, 1),       # 1+1
            (180, 2),      # 3+2
            (300, 0),      # 5+0
            (600, 0),      # 10+0
            (900, 10),     # 15+10
            (1800, 0),     # 30+0
        ]
        if preset_idx < 7:
            init_sec, inc_sec = preset_times[preset_idx]
        else:
            init_sec = self.spin_custom_min.value() * 60
            inc_sec = self.spin_custom_inc.value()

        self.settings["initial_seconds"] = init_sec
        self.settings["increment_seconds"] = inc_sec

        # Tema, Boyut & Ses
        theme_keys = ["emerald", "wood", "ocean", "charcoal"]
        self.settings["theme"] = theme_keys[self.cmb_theme.currentIndex()]

        size_keys = ["mini", "standard", "mega", "fullscreen"]
        self.settings["screen_size"] = size_keys[self.cmb_screen_size.currentIndex()]

        self.settings["sound_enabled"] = self.chk_sound.isChecked()
        self.settings["show_eval_bar"] = self.chk_eval_bar.isChecked()

        self.accept()
