"""
Satranç süre yöneticisi (Satranç Saati).
Beyaz ve Siyah için zaman takibi, artırma (increment) ve bayrak düşme (süre bitimi) kontrolü.
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from typing import Optional

class ChessTimerManager(QObject):
    """Satranç saati yönetim sınıfı."""
    
    # Sinyaller: (kalan_sure_beyaz, kalan_sure_siyah)
    time_updated = pyqtSignal(float, float)
    # Sinyal: (kaybeden_taraf_str) -> 'white' veya 'black'
    flag_dropped = pyqtSignal(str)

    def __init__(self, initial_seconds: float = 600.0, increment_seconds: float = 0.0, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.initial_seconds = initial_seconds
        self.increment_seconds = increment_seconds
        self.white_time = initial_seconds
        self.black_time = initial_seconds
        self.is_white_turn = True
        self.is_running = False
        self.is_unlimited = (initial_seconds <= 0)

        self._timer = QTimer(self)
        self._timer.setInterval(100)  # Her 100 milisaniyede bir hassas güncelleme
        self._timer.timeout.connect(self._on_tick)

    def configure(self, initial_seconds: float, increment_seconds: float = 0.0):
        """Zamanlayıcı ayarlarını günceller ve sıfırlar."""
        self.stop()
        self.initial_seconds = initial_seconds
        self.increment_seconds = increment_seconds
        self.is_unlimited = (initial_seconds <= 0)
        self.reset()

    def reset(self):
        """Saatleri başlangıç değerlerine döndürür."""
        self.stop()
        self.white_time = self.initial_seconds
        self.black_time = self.initial_seconds
        self.is_white_turn = True
        self._emit_update()

    def start(self):
        """Zamanlayıcıyı başlatır."""
        if self.is_unlimited:
            return
        self.is_running = True
        self._timer.start()

    def pause(self):
        """Zamanlayıcıyı duraklatır."""
        self.is_running = False
        self._timer.stop()

    def stop(self):
        """Zamanlayıcıyı durdurur."""
        self.pause()

    def switch_turn(self, to_white: bool):
        """
        Hamle yapıldığında sırayı değiştirir ve önceki oyuncuya artırma (increment) ekler.
        """
        if self.is_unlimited:
            self.is_white_turn = to_white
            return

        if self.is_running and self.increment_seconds > 0:
            if self.is_white_turn:
                self.white_time += self.increment_seconds
            else:
                self.black_time += self.increment_seconds

        self.is_white_turn = to_white
        self._emit_update()

    def _on_tick(self):
        """Her 100ms tetiklenen zaman azaltma."""
        if not self.is_running or self.is_unlimited:
            return

        elapsed = 0.1  # 100 ms = 0.1 saniye
        if self.is_white_turn:
            self.white_time = max(0.0, self.white_time - elapsed)
            if self.white_time <= 0.0:
                self.pause()
                self._emit_update()
                self.flag_dropped.emit("white")
                return
        else:
            self.black_time = max(0.0, self.black_time - elapsed)
            if self.black_time <= 0.0:
                self.pause()
                self._emit_update()
                self.flag_dropped.emit("black")
                return

        self._emit_update()

    def _emit_update(self):
        self.time_updated.emit(self.white_time, self.black_time)

    @staticmethod
    def format_time(seconds: float) -> str:
        """Saniyeyi mm:ss formatına dönüştürür (10 saniyenin altında salise gösterir)."""
        if seconds <= 0:
            return "00:00"
        mins = int(seconds) // 60
        secs = int(seconds) % 60
        if seconds < 10.0 and mins == 0:
            tenths = int((seconds - int(seconds)) * 10)
            return f"{secs}.{tenths}"
        return f"{mins:02d}:{secs:02d}"
