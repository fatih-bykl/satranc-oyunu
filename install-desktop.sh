#!/usr/bin/env bash
# ========================================================
# Satranç Oyunu - Linux Masaüstü Kısayol Kurucusu
# ========================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
RUN_SCRIPT="$DIR/run.sh"
ICON_PATH="$DIR/assets/icon.png"
DESKTOP_FILE="$HOME/.local/share/applications/satranc-oyunu.desktop"

chmod +x "$RUN_SCRIPT"

echo "🎮 Satranç Oyunu Linux Kısayolu Oluşturuluyor..."

# 1. Uygulama Menüsü Kısayolu (~/.local/share/applications)
mkdir -p "$HOME/.local/share/applications"

cat << DESKTOP_ENTRY > "$DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Type=Application
Name=Satranç Oyunu
GenericName=Satranç Oyunu
Comment=Modüler Yapay Zeka Destekli Masaüstü Satranç Oyunu
Exec="$RUN_SCRIPT"
Icon=$ICON_PATH
Terminal=false
Categories=Game;BoardGame;
Keywords=chess;satranç;game;ai;
StartupNotify=true
DESKTOP_ENTRY

chmod +x "$DESKTOP_FILE"

# 2. Masaüstü Kısayolu (Desktop / Masaüstü)
DESKTOP_DIR="$HOME/Desktop"
[ ! -d "$DESKTOP_DIR" ] && DESKTOP_DIR="$HOME/Masaüstü"

if [ -d "$DESKTOP_DIR" ]; then
    cp "$DESKTOP_FILE" "$DESKTOP_DIR/satranc-oyunu.desktop"
    chmod +x "$DESKTOP_DIR/satranc-oyunu.desktop"
    # GNOME / KDE trust shortcut
    gio set "$DESKTOP_DIR/satranc-oyunu.desktop" metadata::trusted true 2>/dev/null || true
    echo "✓ Masaüstü kısayolu oluşturuldu: $DESKTOP_DIR/satranc-oyunu.desktop"
fi

echo "✓ Uygulama menüsü kısayolu oluşturuldu: $DESKTOP_FILE"
echo ""
echo "========================================================"
echo "✅ Kurulum tamamlandı! Uygulamalar menüsünden veya"
echo "   Masaüstünden 'Satranç Oyunu' ikonuna tıklayabilirsiniz."
echo "========================================================"
