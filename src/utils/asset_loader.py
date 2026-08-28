"""
Görsel (PNG) ve Ses Varlıklarını Yöneten Sınıf.
Kullanıcının PNG dosyalarını assets/pieces/ dizininden yükler.
Eksik PNG varsa otomatik olarak yüksek çözünürlüklü vektörel taşlar çizer.
"""
import os
import math
import struct
import wave
from typing import Dict, Optional, Tuple
import chess
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

class AssetLoader:
    """Taş PNG görselleri ve ses dosyaları yükleyicisi."""

    # Standart Taş Anahtarları: (color_bool, piece_type_int) -> Dosya adları
    PIECE_FILE_NAMES = {
        (chess.WHITE, chess.PAWN): ["wP.png", "wp.png", "white_pawn.png", "P.png", "w_pawn.png"],
        (chess.WHITE, chess.KNIGHT): ["wN.png", "wn.png", "white_knight.png", "N.png", "w_knight.png"],
        (chess.WHITE, chess.BISHOP): ["wB.png", "wb.png", "white_bishop.png", "B.png", "w_bishop.png"],
        (chess.WHITE, chess.ROOK): ["wR.png", "wr.png", "white_rook.png", "R.png", "w_rook.png"],
        (chess.WHITE, chess.QUEEN): ["wQ.png", "wq.png", "white_queen.png", "Q.png", "w_queen.png"],
        (chess.WHITE, chess.KING): ["wK.png", "wk.png", "white_king.png", "K.png", "w_king.png"],
        (chess.BLACK, chess.PAWN): ["bP.png", "bp.png", "black_pawn.png", "p.png", "b_pawn.png"],
        (chess.BLACK, chess.KNIGHT): ["bN.png", "bn.png", "black_knight.png", "n.png", "b_knight.png"],
        (chess.BLACK, chess.BISHOP): ["bB.png", "bb.png", "black_bishop.png", "b.png", "b_bishop.png"],
        (chess.BLACK, chess.ROOK): ["bR.png", "br.png", "black_rook.png", "r.png", "b_rook.png"],
        (chess.BLACK, chess.QUEEN): ["bQ.png", "bq.png", "black_queen.png", "q.png", "b_queen.png"],
        (chess.BLACK, chess.KING): ["bK.png", "bk.png", "black_king.png", "k.png", "b_king.png"],
    }

    UNICODE_GLYPHS = {
        (chess.WHITE, chess.PAWN): "♙",
        (chess.WHITE, chess.KNIGHT): "♘",
        (chess.WHITE, chess.BISHOP): "♗",
        (chess.WHITE, chess.ROOK): "♖",
        (chess.WHITE, chess.QUEEN): "♕",
        (chess.WHITE, chess.KING): "♔",
        (chess.BLACK, chess.PAWN): "♟",
        (chess.BLACK, chess.KNIGHT): "♞",
        (chess.BLACK, chess.BISHOP): "♝",
        (chess.BLACK, chess.ROOK): "♜",
        (chess.BLACK, chess.QUEEN): "♛",
        (chess.BLACK, chess.KING): "♚",
    }

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.pieces_dir = os.path.join(base_dir, "assets", "pieces")
        self.sounds_dir = os.path.join(base_dir, "assets", "sounds")
        self._pixmap_cache: Dict[Tuple[bool, int, int], QPixmap] = {}
        
        os.makedirs(self.pieces_dir, exist_ok=True)
        os.makedirs(self.sounds_dir, exist_ok=True)

        self._ensure_default_sounds()

    def get_piece_pixmap(self, color: bool, piece_type: int, size: int) -> QPixmap:
        """
        İstenen boyut ve renkteki taşın QPixmap görselini döner.
        Önce PNG dosyasını arar, yoksa şık vektörel yedek oluşturur.
        """
        cache_key = (color, piece_type, size)
        if cache_key in self._pixmap_cache:
            return self._pixmap_cache[cache_key]

        png_path = self._find_png_file(color, piece_type)
        if png_path and os.path.exists(png_path):
            pixmap = QPixmap(png_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    size, size, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self._pixmap_cache[cache_key] = scaled
                return scaled

        # PNG yoksa yüksek kaliteli yedek çizim üret
        generated = self._generate_fallback_piece(color, piece_type, size)
        self._pixmap_cache[cache_key] = generated
        return generated

    def _find_png_file(self, color: bool, piece_type: int) -> Optional[str]:
        candidates = self.PIECE_FILE_NAMES.get((color, piece_type), [])
        for name in candidates:
            p = os.path.join(self.pieces_dir, name)
            if os.path.isfile(p):
                return p
        return None

    def _generate_fallback_piece(self, color: bool, piece_type: int, size: int) -> QPixmap:
        """Yüksek kaliteli anti-aliased vektörel taş glifi çizer."""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        glyph = self.UNICODE_GLYPHS.get((color, piece_type), "?")
        font_size = int(size * 0.75)
        font = QFont("DejaVu Sans", font_size, QFont.Weight.Bold)
        if not font.exactMatch():
            font = QFont("Sans Serif", font_size, QFont.Weight.Bold)
        painter.setFont(font)

        # Renk paleti
        if color == chess.WHITE:
            main_color = QColor(245, 245, 245)
            border_color = QColor(30, 30, 30)
            shadow_color = QColor(0, 0, 0, 80)
        else:
            main_color = QColor(35, 35, 35)
            border_color = QColor(220, 220, 220)
            shadow_color = QColor(0, 0, 0, 100)

        rect = QRectF(0, 0, size, size)

        # Gölge
        painter.setPen(shadow_color)
        shadow_rect = QRectF(2, 3, size, size)
        painter.drawText(shadow_rect, Qt.AlignmentFlag.AlignCenter, glyph)

        # Ana Gövde
        painter.setPen(main_color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, glyph)

        painter.end()
        return pixmap

    def reload_cache(self):
        """Kullanıcı yeni PNG attığında önbelleği temizler."""
        self._pixmap_cache.clear()

    def _ensure_default_sounds(self):
        """Varsayılan ses efektlerini saf WAV olarak üretir."""
        sounds = {
            "move.wav": (440, 0.08, "sine"),        # Temiz ahşap tık
            "capture.wav": (280, 0.12, "wood"),     # Sert vuruş
            "check.wav": (660, 0.20, "chime"),      # Uyarı çanı
            "game_over.wav": (520, 0.35, "fanfare"),# Oyun sonu
            "notify.wav": (880, 0.10, "sine")       # Bildirim
        }

        for filename, (freq, dur, stype) in sounds.items():
            filepath = os.path.join(self.sounds_dir, filename)
            if not os.path.exists(filepath):
                try:
                    self._synthesize_wav(filepath, freq, dur, stype)
                except Exception as e:
                    print(f"Ses üretilemedi: {filename}, {e}")

    def _synthesize_wav(self, filepath: str, freq: float, duration: float, sound_type: str):
        """Python wave modülü ile sıfır bağımlılıklı saf WAV ses üretimi."""
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        
        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            
            frames = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                
                # Zarf eğrisi (Fade in / out)
                env = math.sin(math.pi * (i / num_samples))
                if sound_type == "wood":
                    # Hızlı sönümlenme
                    env = math.exp(-12 * t)
                    val = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(4 * math.pi * freq * t)
                elif sound_type == "chime":
                    env = math.exp(-4 * t)
                    val = math.sin(2 * math.pi * freq * t) + 0.5 * math.sin(2 * math.pi * (freq * 1.5) * t)
                elif sound_type == "fanfare":
                    val = math.sin(2 * math.pi * freq * t) + 0.5 * math.sin(2 * math.pi * (freq * 1.25) * t) + 0.5 * math.sin(2 * math.pi * (freq * 1.5) * t)
                else:  # sine
                    env = math.exp(-8 * t)
                    val = math.sin(2 * math.pi * freq * t)

                sample = int(val * env * 24000)
                sample = max(-32768, min(32767, sample))
                frames.extend(struct.pack("<h", sample))

            wav_file.writeframes(frames)
