"""
Hakkında ve İletişim Penceresi (About Dialog).
Uygulama detayları, özellikler, sürüm ve Fatih Bıyıklı geliştirici künye & iletişim bilgilerini görüntüler.
"""
import os
import json
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTabWidget, QWidget, QFrame, QFormLayout, QLineEdit, QTextEdit,
    QMessageBox, QScrollArea
)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QPainterPath, QColor
from PyQt6.QtCore import Qt, QUrl

class AboutDialog(QDialog):
    """Hakkında ve İletişim Bilgileri Penceresi."""

    def __init__(self, config_path: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.config_path = config_path
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(config_path), ".."))
        self.setWindowTitle("ℹ️ Hakkında & Geliştirici İletişim")
        self.resize(680, 580)
        self.setMinimumSize(560, 480)

        self.about_data = self._load_data()
        self._init_ui()

    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_data(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.about_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Hakkında bilgisi kaydedilemedi: {e}")

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 1. Üst Başlık & Logo Kartı
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background-color: #242830;
                border: 1px solid #3d4450;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        l_head = QHBoxLayout(header_card)
        l_head.setSpacing(12)

        lbl_logo = QLabel("♟️")
        lbl_logo.setFont(QFont("Segoe UI Emoji", 30))
        l_head.addWidget(lbl_logo)

        l_head_text = QVBoxLayout()
        lbl_title = QLabel(f"{self.about_data.get('app_name', 'Satranç Oyunu')}")
        lbl_title.setFont(QFont("Sans Serif", 13, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #ffffff;")
        
        lbl_sub = QLabel(f"Sürüm {self.about_data.get('version', '1.0.0')} | Linux Edition ({self.about_data.get('release_year', '2026')})")
        lbl_sub.setStyleSheet("color: #81c784; font-weight: bold; font-size: 11px;")

        l_head_text.addWidget(lbl_title)
        l_head_text.addWidget(lbl_sub)
        l_head.addLayout(l_head_text, 1)

        layout.addWidget(header_card)

        # 2. Sekmeler (Tabs)
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3c3c3c;
                background-color: #1e1e1e;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #cccccc;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #375375;
                color: #ffffff;
                font-weight: bold;
            }
        """)

        # Sekme 1: Geliştirici & Künye
        tab_contact = self._create_tab_developer()
        self.tabs.addTab(tab_contact, "👤 Geliştirici Künyesi")

        # Sekme 2: Oyun Hakkında
        tab_about = self._create_tab_about()
        self.tabs.addTab(tab_about, "🎮 Oyun Özellikleri")

        # Sekme 3: Teknolojiler & Lisans
        tab_tech = self._create_tab_tech()
        self.tabs.addTab(tab_tech, "🛠️ Teknolojiler & Lisans")

        layout.addWidget(self.tabs, 1)

        # 3. Alt Butonlar
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        btn_close = QPushButton("Kapat")
        btn_close.setStyleSheet("background-color: #333333; color: white; padding: 6px 24px; font-weight: bold; border-radius: 4px;")
        btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(btn_close)

        layout.addLayout(bottom_layout)

    def _create_tab_developer(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: transparent; border: none;")

        self.tab_dev_widget = QWidget()
        l = QVBoxLayout(self.tab_dev_widget)
        l.setContentsMargins(12, 12, 12, 12)
        l.setSpacing(12)

        dev = self.about_data.get("developer", {})

        # Geliştirici Profil Kartı (Fotoğraf + İsim + Biyografi)
        self.card_dev = QFrame()
        self.card_dev.setStyleSheet("background-color: #262626; border: 1px solid #3a3a3a; border-radius: 8px; padding: 12px;")
        l_profile = QHBoxLayout(self.card_dev)
        l_profile.setSpacing(14)

        # Profil Fotoğrafı (Kırpılmadan tam görsel, orantılı ve ortalanmış)
        photo_label = QLabel()
        size = 104
        photo_label.setFixedSize(size, size)
        photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_path = os.path.join(self.base_dir, "assets", "developer.jpg")
        if not os.path.exists(photo_path):
            photo_path = os.path.join(self.base_dir, "assets", "developer.png")

        if os.path.exists(photo_path):
            src_pix = QPixmap(photo_path)
            rounded_pix = QPixmap(size, size)
            rounded_pix.fill(Qt.GlobalColor.transparent)
            painter = QPainter(rounded_pix)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, size, size, 12, 12)
            painter.setClipPath(path)
            
            # Kırpma yapmadan tam görseli orantılı ölçeklendir ve çerçeveye ortala
            scaled_pix = src_pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            draw_x = (size - scaled_pix.width()) // 2
            draw_y = (size - scaled_pix.height()) // 2
            painter.drawPixmap(draw_x, draw_y, scaled_pix)
            painter.end()
            photo_label.setPixmap(rounded_pix)
        else:
            photo_label.setText("👤")
            photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            photo_label.setFont(QFont("Sans Serif", 36))

        l_profile.addWidget(photo_label)

        # İsim, Ünvan & Biyo
        l_info = QVBoxLayout()
        self.lbl_dev_name = QLabel(dev.get("name", "Fatih Bıyıklı"))
        self.lbl_dev_name.setFont(QFont("Sans Serif", 14, QFont.Weight.Bold))
        self.lbl_dev_name.setStyleSheet("color: #ffffff;")

        self.lbl_dev_title = QLabel(dev.get("title", "İnternet Sihirbazı Proje Kurucusu"))
        self.lbl_dev_title.setStyleSheet("color: #64b5f6; font-size: 12px; font-weight: bold;")

        self.lbl_dev_web = QLabel(f"<a href='{dev.get('website', '')}' style='color: #42a5f5; text-decoration: none;'>🌐 {dev.get('website', '')}</a>")
        self.lbl_dev_web.setOpenExternalLinks(True)

        self.lbl_dev_bio = QLabel(dev.get("bio", ""))
        self.lbl_dev_bio.setWordWrap(True)
        self.lbl_dev_bio.setStyleSheet("color: #d0d0d0; font-size: 11px; margin-top: 4px; line-height: 1.3;")

        l_info.addWidget(self.lbl_dev_name)
        l_info.addWidget(self.lbl_dev_title)
        l_info.addWidget(self.lbl_dev_web)
        l_info.addWidget(self.lbl_dev_bio)
        l_profile.addLayout(l_info, 1)

        l.addWidget(self.card_dev)

        # İletişim & Sosyal Medya Izgarası
        self.social_grid_widget = QWidget()
        grid = QGridLayout(self.social_grid_widget)
        grid.setSpacing(8)

        social_links = [
            ("📧 E-Posta", f"mailto:{dev.get('email', '')}", dev.get("email", ""), "#e57373"),
            ("🌐 Web Sitesi", dev.get("website", ""), "internetsihirbazi.com", "#64b5f6"),
            ("🐙 GitHub", dev.get("github", ""), "github.com/fatih-bykl", "#ba68c8"),
            ("💼 LinkedIn", dev.get("linkedin", ""), "linkedin.com/in/fthbykl", "#42a5f5"),
            ("🐦 X (Twitter)", dev.get("x", ""), "x.com/fathbykl", "#90caf9"),
            ("📸 Instagram", dev.get("instagram", ""), "instagram.com/f.t.h.b.y.k.l", "#f06292"),
            ("💬 WhatsApp", dev.get("whatsapp", ""), "WhatsApp İletişim", "#81c784"),
            ("📘 Facebook", dev.get("facebook", ""), "facebook.com/fathbykl", "#4fc3f7"),
            ("🎮 Steam", dev.get("steam", ""), "steamcommunity.com", "#90a4ae"),
            ("🎵 Spotify", dev.get("spotify", ""), "spotify/fatihbykl", "#aed581"),
            ("🤖 Reddit", dev.get("reddit", ""), "reddit.com/user/fatihbykl", "#ff8a65"),
            ("🎬 TikTok", dev.get("tiktok", ""), "tiktok.com/@fatih.b.y.k.l", "#80deea")
        ]

        for i, (title, url, text, color) in enumerate(social_links):
            row = i // 2
            col = i % 2
            card = QFrame()
            card.setStyleSheet(f"background-color: #292929; border: 1px solid #3d3d3d; border-radius: 6px; padding: 6px;")
            l_c = QHBoxLayout(card)
            l_c.setContentsMargins(6, 4, 6, 4)
            lbl = QLabel(f"<b>{title}:</b> <a href='{url}' style='color: {color}; text-decoration: none;'>{text}</a>")
            lbl.setOpenExternalLinks(True)
            l_c.addWidget(lbl)
            grid.addWidget(card, row, col)

        l.addWidget(self.social_grid_widget)

        l.addStretch()
        scroll.setWidget(self.tab_dev_widget)
        return scroll

    def _create_tab_about(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(10)

        desc = QLabel(self.about_data.get("description", ""))
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #e0e0e0; font-size: 12px; line-height: 1.4;")
        l.addWidget(desc)

        lbl_feat_title = QLabel("🌟 Öne Çıkan Özellikler:")
        lbl_feat_title.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_feat_title.setStyleSheet("color: #90caf9; margin-top: 6px;")
        l.addWidget(lbl_feat_title)

        features = [
            "🤖 <b>Modüler Yapay Zeka (AI Hub):</b> Stockfish UCI motorları, Google Gemini API, yerel Ollama LLM modelleri ve çevrimdışı yerleşik Heuristic motor.",
            "🎨 <b>Özel PNG Taş Desteği:</b> Kendi PNG taş setinizi <code>assets/pieces/</code> dizinine bırakarak anında kullanabilme.",
            "📐 <b>Çoklu Ekran Modları:</b> Mini Boy (Kompakt), Standart Boy, Mega Boy ve Tam Ekran seçenekleri.",
            "📊 <b>İstatistik & Maç Geçmişi:</b> Kazanma oranı, ortalama süre, rekorlar ve tüm maç kayıtları.",
            "⏱️ <b>Profesyonel Saatler & Analiz:</b> Blitz, Rapid, Klasik zamanlayıcılar ve canlı Eval Bar."
        ]

        for feat in features:
            lbl = QLabel(feat)
            lbl.setWordWrap(True)
            lbl.setStyleSheet("color: #cccccc; font-size: 11px;")
            l.addWidget(lbl)

        l.addStretch()
        return w

    def _create_tab_tech(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.setContentsMargins(14, 14, 14, 14)
        l.setSpacing(8)

        lbl_tech_title = QLabel("🛠️ Kullanılan Açık Kaynak Kütüphaneler & Altyapı:")
        lbl_tech_title.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_tech_title.setStyleSheet("color: #90caf9;")
        l.addWidget(lbl_tech_title)

        techs = [
            ("Python 3", "Temel programlama dili ve çekirdek mimari"),
            ("PyQt6", "Gelişmiş, akıcı ve yüksek çözünürlüklü grafik arayüz (GUI)"),
            ("python-chess", "FIDE satranç kuralları, PGN/FEN ayrıştırıcı ve UCI protokolü"),
            ("Stockfish", "Dünyanın en güçlü açık kaynak satranç motoru desteği"),
            ("Google Gemini & Ollama", "Büyük dil modelleri ile persona destekli yapay zeka"),
            ("FFmpeg / QSoundEffect", "Düşük gecikmeli yerel ses motoru")
        ]

        for name, desc in techs:
            lbl = QLabel(f"• <b>{name}:</b> {desc}")
            lbl.setStyleSheet("color: #cccccc; font-size: 11px;")
            l.addWidget(lbl)

        lbl_lic_title = QLabel("📜 Lisans & Kullanım:")
        lbl_lic_title.setFont(QFont("Sans Serif", 11, QFont.Weight.Bold))
        lbl_lic_title.setStyleSheet("color: #90caf9; margin-top: 10px;")
        l.addWidget(lbl_lic_title)

        lbl_license = QLabel(
            "Bu proje açık kaynaklıdır. Özgürce değiştirilebilir, genişletilebilir ve kişisel/eğitim amaçlı kullanılabilir."
        )
        lbl_license.setWordWrap(True)
        lbl_license.setStyleSheet("color: #aaaaaa; font-size: 11px;")
        l.addWidget(lbl_license)

        l.addStretch()
        return w
