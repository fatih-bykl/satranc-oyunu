"""
Ses efektleri yürütücüsü.
QSoundEffect veya sistem ses çıkışı üzerinden oyun içi sesleri (hamle, taş alma, şah, mat) çalar.
"""
import os
from typing import Optional
from PyQt6.QtCore import QObject, QUrl

try:
    from PyQt6.QtMultimedia import QSoundEffect
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False

class SoundPlayer(QObject):
    """Ses efektlerini yöneten ve çalan sınıf."""

    def __init__(self, sounds_dir: str, enabled: bool = True, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.sounds_dir = sounds_dir
        self.enabled = enabled
        self._effects = {}

        if MULTIMEDIA_AVAILABLE:
            self._load_effects()

    def _load_effects(self):
        sound_files = {
            "move": "move.wav",
            "capture": "capture.wav",
            "check": "check.wav",
            "game_over": "game_over.wav",
            "notify": "notify.wav"
        }
        for key, filename in sound_files.items():
            path = os.path.join(self.sounds_dir, filename)
            if os.path.exists(path):
                effect = QSoundEffect(self)
                effect.setSource(QUrl.fromLocalFile(path))
                effect.setVolume(0.7)
                self._effects[key] = effect

    def play(self, sound_name: str):
        """Belirtilen ses efektini çalar."""
        if not self.enabled or not MULTIMEDIA_AVAILABLE:
            return

        effect = self._effects.get(sound_name)
        if effect:
            if effect.isPlaying():
                effect.stop()
            effect.play()

    def set_enabled(self, enabled: bool):
        self.enabled = enabled
