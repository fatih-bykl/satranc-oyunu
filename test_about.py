"""
Hakkında ve İletişim Penceresi Testi.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.about_dialog import AboutDialog

def test_about_dialog():
    app = QApplication.instance() or QApplication(sys.argv)
    about_path = os.path.join(project_root, "config", "about.json")
    
    print("-> 1. AboutDialog Oluşturuluyor...")
    dlg = AboutDialog(about_path)
    assert dlg.about_data.get("app_name") == "Satranç Oyunu", "Uygulama adı doğru olmalı"
    assert "developer" in dlg.about_data, "Geliştirici bilgisi bulunmalı"
    assert dlg.tabs.count() == 3, "3 sekme olmalı"
    print(f"   ✓ AboutDialog başarıyla oluşturuldu! Geliştirici: {dlg.about_data['developer'].get('name')}")

if __name__ == "__main__":
    print("========================================")
    print("HAKKINDA VE İLETİŞİM TESTİ")
    print("========================================")
    test_about_dialog()
    print("========================================")
    print("✅ HAKKINDA TESTİ BAŞARIYLA GEÇTİ!")
    print("========================================")
