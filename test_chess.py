"""
Kapsamlı Doğrulama ve Test Betiği.
Tüm modülleri, satranç kurallarını, AI motorlarını ve varlık yükleyicilerini test eder.
"""
import os
import sys
import chess

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_board_manager():
    print("-> 1. BoardManager Test Ediliyor...")
    from src.core.board_manager import BoardManager
    bm = BoardManager()
    assert bm.turn == True, "Başlangıç sırası Beyaz olmalı"
    assert len(bm.get_legal_moves_san_list()) == 20, "Başlangıçta 20 yasal hamle olmalı"
    
    # Hamle yap
    rec1 = bm.make_uci_move("e2e4")
    assert rec1 is not None, "e2e4 geçerli olmalı"
    assert bm.turn == False, "Sıra Siyah'a geçmeli"
    
    rec2 = bm.make_uci_move("e7e5")
    assert rec2 is not None, "e7e5 geçerli olmalı"
    
    # Çoban matı testi
    bm.reset()
    bm.make_uci_move("e2e4")
    bm.make_uci_move("e7e5")
    bm.make_uci_move("d1h5")
    bm.make_uci_move("b8c6")
    bm.make_uci_move("f1c4")
    bm.make_uci_move("g8f6")
    bm.make_uci_move("h5f7") # Mat
    
    is_over, status, winner = bm.get_game_status()
    assert is_over == True, "Çoban matında oyun bitmiş olmalı"
    assert winner == "Beyaz", "Kazanan Beyaz olmalı"
    print("   ✓ BoardManager kural ve mat kontrolleri başarılı!")

def test_timer_manager():
    print("-> 2. ChessTimerManager Test Ediliyor...")
    from PyQt6.QtWidgets import QApplication
    from src.core.timer_manager import ChessTimerManager
    app = QApplication.instance() or QApplication(sys.argv)
    
    tm = ChessTimerManager(300.0, 2.0)
    assert tm.white_time == 300.0
    assert ChessTimerManager.format_time(300.0) == "05:00"
    assert ChessTimerManager.format_time(9.5) == "9.5"
    tm.switch_turn(False)
    assert tm.is_white_turn == False
    print("   ✓ ChessTimerManager kontrolleri başarılı!")

def test_heuristic_ai():
    print("-> 3. Yerleşik Heuristic AI Test Ediliyor...")
    from src.ai.heuristic_ai import HeuristicAI
    board = chess.Board()
    
    for diff in ["easy", "medium", "hard"]:
        ai = HeuristicAI({"id": f"test_{diff}", "difficulty": diff})
        result = ai.get_move(board, [])
        assert result.move_uci != "", f"{diff} modunda hamle üretilmeli"
        assert chess.Move.from_uci(result.move_uci) in board.legal_moves, f"{diff} modunda üretilen hamle yasal olmalı"
        print(f"   ✓ HeuristicAI ({diff}) hamle üretti: {result.move_san} ({result.time_spent:.3f}s)")

def test_asset_loader():
    print("-> 4. AssetLoader ve Ses Sentezi Test Ediliyor...")
    from PyQt6.QtWidgets import QApplication
    from src.utils.asset_loader import AssetLoader
    app = QApplication.instance() or QApplication(sys.argv)
    
    loader = AssetLoader(project_root)
    # 12 taşın da pixmap'ini test et
    for color in [chess.WHITE, chess.BLACK]:
        for pt in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            pix = loader.get_piece_pixmap(color, pt, 64)
            assert not pix.isNull(), f"Taş pixmap ({color}, {pt}) boş olmamalı"
    
    # Ses dosyalarını test et
    for s_file in ["move.wav", "capture.wav", "check.wav", "game_over.wav", "notify.wav"]:
        s_path = os.path.join(loader.sounds_dir, s_file)
        assert os.path.exists(s_path), f"Ses dosyası üretilmiş olmalı: {s_file}"
        assert os.path.getsize(s_path) > 100, f"Ses dosyası dolu olmalı: {s_file}"
    print("   ✓ AssetLoader ve Ses Varlıkları başarılı!")

def test_ai_manager():
    print("-> 5. AIManager ve Konfigürasyon Test Ediliyor...")
    from src.ai.ai_manager import AIManager
    config_path = os.path.join(project_root, "config", "ai_models.json")
    mgr = AIManager(config_path)
    assert len(mgr.models_data) >= 3, "En az 3 varsayılan model olmalı"
    active_info = mgr.get_active_model_info()
    assert active_info is not None, "Aktif model bilgisi alınabilmeli"
    print(f"   ✓ AIManager başarılı! Aktif Model: {active_info.get('name')}")

if __name__ == "__main__":
    print("========================================")
    print("SATRANÇ PROJESİ DOĞRULAMA TESTLERİ")
    print("========================================")
    test_board_manager()
    test_timer_manager()
    test_heuristic_ai()
    test_asset_loader()
    test_ai_manager()
    print("========================================")
    print("✅ TÜM TESTLER BAŞARIYLA GEÇTİ!")
    print("========================================")
