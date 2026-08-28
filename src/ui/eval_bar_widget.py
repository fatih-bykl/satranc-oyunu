"""
Değerlendirme Çubuğu Bileşeni (Evaluation Bar).
Yapay zeka veya motorun hesapladığı tahta üstünlüğünü dikey renkli bar olarak gösterir.
"""
from typing import Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, pyqtProperty

class EvalBarWidget(QWidget):
    """Satranç değerlendirme çubuğu."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedWidth(26)
        self._score: float = 0.0          # Sentipiyon puanı (pozitif: beyaz üstün)
        self._mate_in: Optional[int] = None
        self._flipped: bool = False
        self._animated_val: float = 0.5   # 0.0 (Tamamen Siyah) ile 1.0 (Tamamen Beyaz)

    @pyqtProperty(float)
    def animated_val(self) -> float:
        return self._animated_val

    @animated_val.setter
    def animated_val(self, val: float):
        self._animated_val = max(0.02, min(0.98, val))
        self.update()

    def set_evaluation(self, eval_pawn: Optional[float], mate_in: Optional[int] = None):
        self._mate_in = mate_in
        if eval_pawn is not None:
            self._score = eval_pawn
            # Sigmoid benzeri haritalama (-10.0 ... +10.0 -> 0.02 ... 0.98)
            # score = 0 -> 0.5
            norm = 1.0 / (1.0 + 10 ** (-self._score / 4.0))
            self.animated_val = norm
        elif mate_in is not None:
            self.animated_val = 1.0 if mate_in > 0 else 0.0
        self.update()

    def set_flipped(self, flipped: bool):
        self._flipped = flipped
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        rect = QRectF(0, 0, w, h)

        # Beyaz ve Siyah renkler
        white_color = QColor(240, 240, 240)
        black_color = QColor(45, 45, 45)

        # Beyazın yüzdesi (0.0 - 1.0)
        white_pct = self._animated_val
        if self._flipped:
            white_pct = 1.0 - white_pct

        white_height = h * white_pct
        black_height = h - white_height

        # Çizim (Üst taraf Siyah, Alt taraf Beyaz veya tersi)
        if not self._flipped:
            # Siyah üstte, Beyaz altta
            painter.fillRect(QRectF(0, 0, w, black_height), black_color)
            painter.fillRect(QRectF(0, black_height, w, white_height), white_color)
        else:
            # Beyaz üstte, Siyah altta
            painter.fillRect(QRectF(0, 0, w, white_height), white_color)
            painter.fillRect(QRectF(0, white_height, w, black_height), black_color)

        # Skoru Yaz
        painter.setFont(QFont("Sans Serif", 8, QFont.Weight.Bold))
        
        if self._mate_in is not None:
            text = f"M{abs(self._mate_in)}"
        else:
            abs_score = abs(self._score)
            text = f"{abs_score:.1f}" if abs_score < 10 else f"{int(abs_score)}"

        # Skoru avantajlı tarafın içine yaz
        if self._score >= 0 or (self._mate_in and self._mate_in > 0):
            # Beyaz avantajlı
            painter.setPen(QColor(50, 50, 50))
            y_pos = h - 10 if not self._flipped else 20
            painter.drawText(QRectF(0, y_pos - 10, w, 20), Qt.AlignmentFlag.AlignCenter, text)
        else:
            # Siyah avantajlı
            painter.setPen(QColor(220, 220, 220))
            y_pos = 20 if not self._flipped else h - 10
            painter.drawText(QRectF(0, y_pos - 10, w, 20), Qt.AlignmentFlag.AlignCenter, text)

        painter.end()
