"""
Piyon Terfisi (Promotion) ve Dialog Testi.
"""
import os
import sys
import chess
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.asset_loader import AssetLoader
from src.ui.chess_board_widget import PromotionDialog, ChessBoardWidget
from src.core.board_manager import BoardManager

def test_promotion_dialog():
    app = QApplication.instance() or QApplication(sys.argv)
    loader = AssetLoader(project_root)
    
    print("-> PromotionDialog oluşturuluyor...")
    dlg = PromotionDialog(color=chess.WHITE, asset_loader=loader)
    
    # Varsayılan seçim Vezir olmalı
    assert dlg.chosen_piece == chess.QUEEN, "Varsayılan terfi taşı Vezir olmalı"
    
    # Farklı taş seçimini simüle et
    dlg._select_piece(chess.KNIGHT)
    assert dlg.chosen_piece == chess.KNIGHT, "Seçilen taş At olmalı"
    
    print("   ✓ PromotionDialog hatasız oluşturuldu ve buton simgeleri başarıyla yüklendi!")

def test_promotion_move_flow():
    app = QApplication.instance() or QApplication(sys.argv)
    loader = AssetLoader(project_root)
    
    # 7. yatayda piyon bulunan bir tahta konumu oluştur (örneğin Beyaz piyon e7'de)
    fen = "8/4P3/8/8/8/8/8/4K2k w - - 0 1"
    bm = BoardManager(fen=fen)
    
    legal_moves = bm.get_legal_moves_from(chess.E7)
    assert len(legal_moves) == 4, f"e7'den 4 farklı terfi hamlesi olmalı (Q, R, B, N), bulunan: {len(legal_moves)}"
    
    # e7e8q hamlesini yap
    rec = bm.make_uci_move("e7e8q")
    assert rec is not None, "e7e8q hamlesi geçerli olmalı"
    assert bm.board.piece_at(chess.E8).piece_type == chess.QUEEN, "e8 karesindeki taş Vezir olmalı"
    print("   ✓ Piyon terfisi tahtada Vezir olarak başarıyla gerçekleşti!")

if __name__ == "__main__":
    print("========================================")
    print("PİYON TERFİSİ TESTİ")
    print("========================================")
    test_promotion_dialog()
    test_promotion_move_flow()
    print("========================================")
    print("✅ PİYON TERFİSİ TESTİ BAŞARIYLA GEÇTİ!")
    print("========================================")
