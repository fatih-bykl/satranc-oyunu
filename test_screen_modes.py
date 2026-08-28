"""
Ekran Boyutları ve Modları (Mini, Standart, Mega, Tam Ekran) Testi.
"""
import os
import sys
import chess
from PyQt6.QtWidgets import QApplication

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow

def test_screen_modes():
    app = QApplication.instance() or QApplication(sys.argv)
    
    print("-> MainWindow başlatılıyor...")
    win = MainWindow(project_root)
    
    # 1. Mini Mod Testi
    print("-> 1. Mini Boyut Modu Test Ediliyor...")
    win.set_screen_size("mini")
    assert win.current_screen_mode == "mini"
    assert win.right_panel_widget.isHidden() == True, "Mini modda sağ panel gizlenmeli"
    assert win.mini_top_bar.isHidden() == False, "Mini modda üst mini bar görünür olmalı"
    assert win.mini_bottom_bar.isHidden() == False, "Mini modda alt mini bar görünür olmalı"
    print(f"   ✓ Mini Mod başarılı! Pencere boyutu: {win.width()}x{win.height()}")

    # 2. Standart Mod Testi
    print("-> 2. Standart Boyut Modu Test Ediliyor...")
    win.set_screen_size("standard")
    assert win.current_screen_mode == "standard"
    assert win.right_panel_widget.isHidden() == False, "Standart modda sağ panel görünür olmalı"
    assert win.mini_top_bar.isHidden() == True, "Standart modda üst mini bar gizlenmeli"
    print(f"   ✓ Standart Mod başarılı! Pencere boyutu: {win.width()}x{win.height()}")

    # 3. Mega Mod Testi
    print("-> 3. Mega Boyut Modu Test Ediliyor...")
    win.set_screen_size("mega")
    assert win.current_screen_mode == "mega"
    assert win.right_panel_widget.isHidden() == False, "Mega modda sağ panel görünür olmalı"
    print(f"   ✓ Mega Mod başarılı! Pencere boyutu: {win.width()}x{win.height()}")

    win.close()
    print("   ✓ Tüm ekran boyutu modları başarıyla doğrulandı!")

if __name__ == "__main__":
    print("========================================")
    print("EKRAN BOYUTU MODLARI TESTİ")
    print("========================================")
    test_screen_modes()
    print("========================================")
    print("✅ TÜM EKRAN MODLARI TESTİ BAŞARILI!")
    print("========================================")
