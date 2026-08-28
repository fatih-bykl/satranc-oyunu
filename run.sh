#!/usr/bin/env bash
# Satranç Oyunu Başlatma Betiği

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Sanal ortam kontrolü ve oluşturulması
if [ ! -d "venv" ]; then
    echo "⚡ Sanal ortam (venv) oluşturuluyor..."
    python3 -m venv venv
    echo "📦 Bağımlılıklar yükleniyor..."
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install -r requirements.txt
fi

# Uygulamayı başlat
echo "🚀 Satranç oyunu başlatılıyor..."
./venv/bin/python src/main.py
