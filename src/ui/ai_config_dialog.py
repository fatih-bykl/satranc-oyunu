"""
Yapay Zeka Modelleri Yönetim ve Ekleme Penceresi (AI Config Dialog).
Kullanıcının dilediği UCI motorunu (Stockfish vb.) veya LLM modelini (Gemini, Ollama, OpenAI vb.) ekleyip yapılandırmasını sağlar.
"""
import uuid
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit,
    QPushButton, QFileDialog, QMessageBox, QGroupBox, QFormLayout, QWidget, QStackedWidget
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt

from ..ai.ai_manager import AIManager

class AIConfigDialog(QDialog):
    """Yapay zeka modellerini yönetme penceresi."""

    def __init__(self, ai_manager: AIManager, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.ai_manager = ai_manager
        self.setWindowTitle("Yapay Zeka Modellerini Yönet")
        self.resize(750, 560)
        self.selected_model_data: Optional[Dict[str, Any]] = None

        self._init_ui()
        self._load_model_list()

    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)

        # SOL PANEL: Model Listesi ve Ekle/Sil Butonları
        left_layout = QVBoxLayout()
        
        lbl_list = QLabel("Kayıtlı Yapay Zeka Modelleri:")
        lbl_list.setFont(QFont("Sans Serif", 10, QFont.Weight.Bold))
        left_layout.addWidget(lbl_list)

        self.model_list_widget = QListWidget(self)
        self.model_list_widget.currentRowChanged.connect(self._on_model_selected)
        left_layout.addWidget(self.model_list_widget)

        btn_list_layout = QHBoxLayout()
        self.btn_new_model = QPushButton("+ Yeni Model Ekle")
        self.btn_new_model.clicked.connect(self._create_new_model)
        self.btn_delete_model = QPushButton("Sil")
        self.btn_delete_model.clicked.connect(self._delete_selected_model)
        btn_list_layout.addWidget(self.btn_new_model)
        btn_list_layout.addWidget(self.btn_delete_model)
        left_layout.addLayout(btn_list_layout)

        main_layout.addLayout(left_layout, 1)

        # SAĞ PANEL: Model Düzenleme Formu
        right_layout = QVBoxLayout()

        self.group_details = QGroupBox("Model Detayları ve Parametreleri")
        form = QFormLayout(self.group_details)
        form.setSpacing(10)

        # Model Adı
        self.txt_name = QLineEdit()
        form.addRow("Görünen Ad:", self.txt_name)

        # Model Türü
        self.cmb_type = QComboBox()
        self.cmb_type.addItems([
            "Yerleşik Python Motoru (builtin)",
            "UCI Satranç Motoru (Stockfish vb.) (uci)",
            "Google Gemini API (gemini)",
            "Ollama Yerel Modeli (ollama)",
            "OpenAI / Uyumlu API (openai)"
        ])
        self.cmb_type.currentIndexChanged.connect(self._on_type_changed)
        form.addRow("Model Türü:", self.cmb_type)

        # Dinamik Ayar Sayfaları
        self.stack_settings = QStackedWidget()

        # Sayfa 0: Builtin
        p_builtin = QWidget()
        l_builtin = QFormLayout(p_builtin)
        self.cmb_difficulty = QComboBox()
        self.cmb_difficulty.addItems(["Kolay (Acemi)", "Orta (Kulüp)", "Zor (Usta)"])
        l_builtin.addRow("Zorluk Seviyesi:", self.cmb_difficulty)
        self.stack_settings.addWidget(p_builtin)

        # Sayfa 1: UCI Motoru
        p_uci = QWidget()
        l_uci = QFormLayout(p_uci)
        h_path = QHBoxLayout()
        self.txt_uci_path = QLineEdit("/usr/bin/stockfish")
        btn_browse = QPushButton("Gözat...")
        btn_browse.clicked.connect(self._browse_uci_path)
        h_path.addWidget(self.txt_uci_path)
        h_path.addWidget(btn_browse)
        l_uci.addRow("Motor Dosya Yolu:", h_path)

        self.spin_uci_depth = QSpinBox()
        self.spin_uci_depth.setRange(1, 35)
        self.spin_uci_depth.setValue(15)
        l_uci.addRow("Arama Derinliği:", self.spin_uci_depth)

        self.spin_uci_time = QDoubleSpinBox()
        self.spin_uci_time.setRange(0.1, 30.0)
        self.spin_uci_time.setValue(1.5)
        self.spin_uci_time.setSuffix(" sn")
        l_uci.addRow("Düşünme Süresi:", self.spin_uci_time)

        self.spin_uci_skill = QSpinBox()
        self.spin_uci_skill.setRange(0, 20)
        self.spin_uci_skill.setValue(20)
        l_uci.addRow("Yetenek (Skill 0-20):", self.spin_uci_skill)
        self.stack_settings.addWidget(p_uci)

        # Sayfa 2: Gemini API
        p_gemini = QWidget()
        l_gemini = QFormLayout(p_gemini)
        self.txt_gemini_key = QLineEdit()
        self.txt_gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_gemini_key.setPlaceholderText("AIzaSy...")
        l_gemini.addRow("Gemini API Key:", self.txt_gemini_key)

        self.txt_gemini_model = QLineEdit("gemini-2.5-flash")
        l_gemini.addRow("Model Kodu:", self.txt_gemini_model)

        self.txt_gemini_persona = QTextEdit()
        self.txt_gemini_persona.setMaximumHeight(70)
        self.txt_gemini_persona.setPlaceholderText("Yapay zekanın oynarken takınacağı tavır / persona...")
        l_gemini.addRow("Oyun Stili (Persona):", self.txt_gemini_persona)
        self.stack_settings.addWidget(p_gemini)

        # Sayfa 3: Ollama
        p_ollama = QWidget()
        l_ollama = QFormLayout(p_ollama)
        self.txt_ollama_url = QLineEdit("http://localhost:11434")
        l_ollama.addRow("Ollama URL:", self.txt_ollama_url)

        self.txt_ollama_model = QLineEdit("llama3:latest")
        l_ollama.addRow("Model Adı:", self.txt_ollama_model)

        self.txt_ollama_persona = QTextEdit()
        self.txt_ollama_persona.setMaximumHeight(70)
        l_ollama.addRow("Oyun Stili (Persona):", self.txt_ollama_persona)
        self.stack_settings.addWidget(p_ollama)

        # Sayfa 4: OpenAI / Uyumlu API
        p_openai = QWidget()
        l_openai = QFormLayout(p_openai)
        self.txt_openai_url = QLineEdit("https://api.openai.com/v1")
        l_openai.addRow("Base URL:", self.txt_openai_url)

        self.txt_openai_key = QLineEdit()
        self.txt_openai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_openai_key.setPlaceholderText("sk-...")
        l_openai.addRow("API Key:", self.txt_openai_key)

        self.txt_openai_model = QLineEdit("gpt-4o-mini")
        l_openai.addRow("Model Adı:", self.txt_openai_model)

        self.txt_openai_persona = QTextEdit()
        self.txt_openai_persona.setMaximumHeight(70)
        l_openai.addRow("Oyun Stili (Persona):", self.txt_openai_persona)
        self.stack_settings.addWidget(p_openai)

        form.addRow("Yapılandırma:", self.stack_settings)

        # Açıklama
        self.txt_desc = QLineEdit()
        form.addRow("Açıklama:", self.txt_desc)

        right_layout.addWidget(self.group_details)

        # Alt Butonlar: Test Et, Kaydet, Kapat
        bottom_btn_layout = QHBoxLayout()
        self.btn_test = QPushButton("🔍 Bağlantıyı / Motoru Test Et")
        self.btn_test.clicked.connect(self._test_model_connection)
        
        self.btn_save = QPushButton("💾 Değişiklikleri Kaydet")
        self.btn_save.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold; padding: 8px;")
        self.btn_save.clicked.connect(self._save_current_model)

        self.btn_close = QPushButton("Kapat")
        self.btn_close.clicked.connect(self.accept)

        bottom_btn_layout.addWidget(self.btn_test)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(self.btn_save)
        bottom_btn_layout.addWidget(self.btn_close)
        right_layout.addLayout(bottom_btn_layout)

        main_layout.addLayout(right_layout, 2)

    def _on_type_changed(self, index: int):
        self.stack_settings.setCurrentIndex(index)

    def _browse_uci_path(self):
        filename, _ = QFileDialog.getOpenFileName(self, "UCI Motoru Seç", "/usr/bin", "Tüm Dosyalar (*)")
        if filename:
            self.txt_uci_path.setText(filename)

    def _load_model_list(self):
        self.model_list_widget.clear()
        for m in self.ai_manager.models_data:
            item = QListWidgetItem(f"[{m.get('type', 'builtin').upper()}] {m.get('name', 'İsimsiz')}")
            item.setData(Qt.ItemDataRole.UserRole, m)
            self.model_list_widget.addItem(item)

        if self.model_list_widget.count() > 0:
            self.model_list_widget.setCurrentRow(0)

    def _on_model_selected(self, row: int):
        if row < 0 or row >= self.model_list_widget.count():
            return
        item = self.model_list_widget.item(row)
        m = item.data(Qt.ItemDataRole.UserRole)
        self.selected_model_data = m

        self.txt_name.setText(m.get("name", ""))
        self.txt_desc.setText(m.get("description", ""))

        ai_type = m.get("type", "builtin")
        if ai_type == "builtin":
            self.cmb_type.setCurrentIndex(0)
            diff = m.get("difficulty", "medium")
            diff_idx = 0 if diff == "easy" else (2 if diff == "hard" else 1)
            self.cmb_difficulty.setCurrentIndex(diff_idx)
        elif ai_type == "uci":
            self.cmb_type.setCurrentIndex(1)
            self.txt_uci_path.setText(m.get("executable_path", "/usr/bin/stockfish"))
            self.spin_uci_depth.setValue(m.get("depth", 15))
            self.spin_uci_time.setValue(m.get("time_limit", 1.5))
            self.spin_uci_skill.setValue(m.get("skill_level", 20))
        elif ai_type == "gemini":
            self.cmb_type.setCurrentIndex(2)
            self.txt_gemini_key.setText(m.get("api_key", ""))
            self.txt_gemini_model.setText(m.get("model_name", "gemini-2.5-flash"))
            self.txt_gemini_persona.setText(m.get("persona", ""))
        elif ai_type == "ollama":
            self.cmb_type.setCurrentIndex(3)
            self.txt_ollama_url.setText(m.get("endpoint_url", "http://localhost:11434"))
            self.txt_ollama_model.setText(m.get("model_name", "llama3:latest"))
            self.txt_ollama_persona.setText(m.get("persona", ""))
        elif ai_type in ("openai", "custom_llm"):
            self.cmb_type.setCurrentIndex(4)
            self.txt_openai_url.setText(m.get("base_url", "https://api.openai.com/v1"))
            self.txt_openai_key.setText(m.get("api_key", ""))
            self.txt_openai_model.setText(m.get("model_name", "gpt-4o-mini"))
            self.txt_openai_persona.setText(m.get("persona", ""))

    def _collect_form_data(self) -> Dict[str, Any]:
        type_idx = self.cmb_type.currentIndex()
        type_keys = ["builtin", "uci", "gemini", "ollama", "openai"]
        ai_type = type_keys[type_idx]

        model_id = self.selected_model_data.get("id") if self.selected_model_data else f"model_{uuid.uuid4().hex[:8]}"

        data: Dict[str, Any] = {
            "id": model_id,
            "name": self.txt_name.text().strip() or "Yeni Model",
            "type": ai_type,
            "description": self.txt_desc.text().strip(),
            "enabled": True
        }

        if ai_type == "builtin":
            diff_idx = self.cmb_difficulty.currentIndex()
            data["difficulty"] = ["easy", "medium", "hard"][diff_idx]
        elif ai_type == "uci":
            data["executable_path"] = self.txt_uci_path.text().strip()
            data["depth"] = self.spin_uci_depth.value()
            data["time_limit"] = self.spin_uci_time.value()
            data["skill_level"] = self.spin_uci_skill.value()
        elif ai_type == "gemini":
            data["api_key"] = self.txt_gemini_key.text().strip()
            data["model_name"] = self.txt_gemini_model.text().strip()
            data["persona"] = self.txt_gemini_persona.toPlainText().strip()
        elif ai_type == "ollama":
            data["endpoint_url"] = self.txt_ollama_url.text().strip()
            data["model_name"] = self.txt_ollama_model.text().strip()
            data["persona"] = self.txt_ollama_persona.toPlainText().strip()
        elif ai_type == "openai":
            data["base_url"] = self.txt_openai_url.text().strip()
            data["api_key"] = self.txt_openai_key.text().strip()
            data["model_name"] = self.txt_openai_model.text().strip()
            data["persona"] = self.txt_openai_persona.toPlainText().strip()

        return data

    def _save_current_model(self):
        data = self._collect_form_data()
        self.ai_manager.add_or_update_model(data)
        
        current_row = self.model_list_widget.currentRow()
        self._load_model_list()
        self.model_list_widget.setCurrentRow(max(0, min(current_row, self.model_list_widget.count() - 1)))
        
        QMessageBox.information(self, "Başarılı", f"'{data['name']}' modeli başarıyla kaydedildi!")

    def _create_new_model(self):
        new_data = {
            "id": f"custom_{uuid.uuid4().hex[:8]}",
            "name": "Yeni Özel Yapay Zeka",
            "type": "gemini",
            "description": "Özel eklenen model",
            "enabled": True
        }
        self.selected_model_data = new_data
        self.ai_manager.add_or_update_model(new_data)
        self._load_model_list()
        self.model_list_widget.setCurrentRow(self.model_list_widget.count() - 1)

    def _delete_selected_model(self):
        if not self.selected_model_data:
            return
        model_id = self.selected_model_data.get("id")
        if model_id in ("builtin_easy", "builtin_medium", "builtin_hard"):
            QMessageBox.warning(self, "Uyarı", "Yerleşik temel modeller silinemez.")
            return

        reply = QMessageBox.question(
            self, "Onay",
            f"'{self.selected_model_data.get('name')}' modelini silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.ai_manager.delete_model(model_id)
            self._load_model_list()

    def _test_model_connection(self):
        data = self._collect_form_data()
        temp_inst = self.ai_manager.create_ai_instance(data)
        try:
            success, msg = temp_inst.test_connection()
            temp_inst.cleanup()
            if success:
                QMessageBox.information(self, "Test Başarılı ✓", msg)
            else:
                QMessageBox.warning(self, "Test Başarısız ✗", msg)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Test sırasında hata oluştu:\n{str(e)}")
