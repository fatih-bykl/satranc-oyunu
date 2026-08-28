"""
İstatistik ve Maç Kayıtları Testi.
"""
import os
import sys
from PyQt6.QtWidgets import QApplication

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.stats_manager import StatsManager
from src.ui.stats_dialog import StatsDialog

def test_stats_manager():
    test_file = os.path.join(project_root, "config", "test_stats.json")
    if os.path.exists(test_file):
        os.remove(test_file)

    print("-> 1. StatsManager Oluşturuluyor...")
    sm = StatsManager(test_file)
    assert sm.data["total_games"] == 0
    assert sm.win_rate == 0.0

    # Maç kaydet (1 Galibiyet)
    print("-> 2. Maç Kayıtları Ekleniyor...")
    sm.record_match(
        opponent_name="Stockfish",
        result="win",
        reason="Şah Mat",
        duration_seconds=125.4,
        moves_count=34,
        player_color="Beyaz"
    )
    assert sm.data["total_games"] == 1
    assert sm.data["wins"] == 1
    assert sm.data["losses"] == 0
    assert sm.win_rate == 100.0
    assert sm.data["fastest_win_seconds"] == 125.4

    # Maç kaydet (1 Mağlubiyet)
    sm.record_match(
        opponent_name="Gemini 2.5 Flash",
        result="loss",
        reason="Terk",
        duration_seconds=240.0,
        moves_count=45,
        player_color="Siyah"
    )
    assert sm.data["total_games"] == 2
    assert sm.data["wins"] == 1
    assert sm.data["losses"] == 1
    assert sm.win_rate == 50.0

    print(f"   ✓ İstatistikler doğru hesaplandı! Kazanma Oranı: %{sm.win_rate:.1f}")

    # Dialog Testi
    app = QApplication.instance() or QApplication(sys.argv)
    print("-> 3. StatsDialog Test Ediliyor...")
    dlg = StatsDialog(sm)
    assert dlg.table.rowCount() == 2, "Tabloda 2 maç satırı olmalı"
    print("   ✓ StatsDialog başarıyla oluşturuldu ve veriler listelendi!")

    # Sıfırlama Testi
    print("-> 4. İstatistik Sıfırlama Test Ediliyor...")
    sm.reset_stats()
    assert sm.data["total_games"] == 0
    assert sm.data["wins"] == 0
    assert len(sm.data["matches"]) == 0
    print("   ✓ İstatistikler başarıyla sıfırlandı!")

    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    print("========================================")
    print("İSTATİSTİK MODÜLÜ TESTİ")
    print("========================================")
    test_stats_manager()
    print("========================================")
    print("✅ TÜM İSTATİSTİK TESTLERİ BAŞARIYLA GEÇTİ!")
    print("========================================")
