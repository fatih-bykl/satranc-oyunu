# ♟️ Satranç Oyunu - Kurulum ve Kullanım Kılavuzu

Bu belge, **Satranç Oyunu** masaüstü uygulamasını **Linux** ve **Windows** işletim sistemlerinde nasıl kuracağınızı, çalıştıracağınızı ve özelleştireceğinizi detaylı olarak açıklamaktadır.

---

## 🪟 Windows Kurulum & Çalıştırma Rehberi

### Gereksinimler:
- **Windows 10 / 11** (64-bit)
- **Python 3.10 veya daha yeni bir sürüm** ([python.org](https://www.python.org/downloads/) adresinden indirilebilir. *Kurulum sırasında "Add python.exe to PATH" seçeneğini işaretlemeyi unutmayın.*)

### 1. Yöntem: Tek Tıkla Masaüstü Kısayolu Kurulumu (Önerilen)
1. `Satranc-Oyunu-Windows-v1.0.0.zip` dosyasını bilgisayarınızda istediğiniz bir klasöre çıkartın.
2. Klasör içindeki **`install-desktop.bat`** dosyasına çift tıklayın.
3. Kurulum betiği gerekli sanal ortamı ve kütüphaneleri otomatik olarak kuracak ve **Masaüstünüze ile Başlat Menünüze "Satranç Oyunu" kısayolu** ekleyecektir.
4. Artık masaüstündeki ikona tıklayarak oyunu dilediğiniz zaman başlatabilirsiniz.

### 2. Yöntem: Taşınabilir (Portable) Çalıştırma
1. Klasör içerisindeki **`run.bat`** dosyasına çift tıklayın.
2. Oyun otomatik olarak açılacaktır.

### 3. Yöntem: Visual Studio Code ile Geliştirici Modu
1. **VS Code**'u açın ve `satranç` klasörünü seçin (`File -> Open Folder...`).
2. Klavyeden **`F5`** tuşuna basarak doğrudan hata ayıklama modunda çalıştırın.

---

## 🐧 Linux Kurulum & Çalıştırma Rehberi

### Gereksinimler:
- Herhangi bir modern 64-bit Linux dağıtımı (*CachyOS, Arch, Ubuntu, Debian, Fedora, openSUSE, Manjaro, Linux Mint vb.*)
- **Python 3.10+** ve `python3-venv` paketi.

#### Gerekli Paketlerin Yüklenmesi (Eğer Sisteminizde Yoksa):
- **Arch / CachyOS / Manjaro:**
  ```bash
  sudo pacman -S python stockfish
  ```
- **Ubuntu / Debian / Linux Mint:**
  ```bash
  sudo apt update
  sudo apt install python3 python3-venv python3-pip stockfish
  ```
- **Fedora / RHEL:**
  ```bash
  sudo dnf install python3 python3-pip stockfish
  ```

### 1. Yöntem: Masaüstü ve Uygulamalar Menüsüne Ekleme (Önerilen)
1. İndirdiğiniz `Satranc-Oyunu-Linux-v1.0.0.tar.gz` veya `.zip` arşivini açın.
2. Terminali klasörün içinde açıp şu komutu çalıştırın:
   ```bash
   ./install-desktop.sh
   ```
3. Bu işlem, sisteminizin **Uygulamalar (Başlat) Menüsüne** ve **Masaüstünüze** satranç ikonuyla birlikte kısayol ekler.

### 2. Yöntem: Terminal Üzerinden Çalıştırma
```bash
./run.sh
```

### 3. Yöntem: Visual Studio Code ile
VS Code ile `satranç` klasörünü açıp klavyeden **`F5`** tuşuna basmanız yeterlidir.

---

## 🎨 Kendi PNG Taş Setinizi Ekleme

Uygulama, kendi özel grafiklerinizi kullanmanıza imkan tanır. PNG formatındaki görsellerinizi `assets/pieces/` dizinine kopyalamanız yeterlidir:

| Taş Türü | Beyaz Taş Dosya Adı | Siyah Taş Dosya Adı |
| :--- | :--- | :--- |
| **Piyon** | `wP.png` veya `white_pawn.png` | `bP.png` veya `black_pawn.png` |
| **Kale** | `wR.png` veya `white_rook.png` | `bR.png` veya `black_rook.png` |
| **At** | `wN.png` veya `white_knight.png` | `bN.png` veya `black_knight.png` |
| **Fil** | `wB.png` veya `white_bishop.png` | `bB.png` veya `black_bishop.png` |
| **Vezir** | `wQ.png` veya `white_queen.png` | `bQ.png` veya `black_queen.png` |
| **Şah** | `wK.png` veya `white_king.png` | `bK.png` veya `black_king.png` |

> 💡 *Not: PNG dosyası eklemediğiniz durumlarda sistem çökmeyip otomatik olarak yüksek çözünürlüklü vektörel taşları çizer.*

---

## 🤖 Yapay Zeka (AI) Modellerini Yapılandırma

Üst araç çubuğundaki **"🤖 AI Yönet"** butonuna basarak:
1. **Yerleşik Motor (Heuristic AI):** İnternet veya kurulum gerektirmeden çalışan Acemi, Kulüp ve Usta seviyeleri.
2. **Stockfish UCI Motoru:** Sisteminizdeki Stockfish motorunu (ör: Linux'ta `/usr/bin/stockfish`, Windows'ta `stockfish.exe`) bağlayabilirsiniz.
3. **Google Gemini API:** Gemini API anahtarınızı girerek persona destekli, hamle yaparken Türkçe yorum yazan yapay zeka ile oynayabilirsiniz.
4. **Ollama Yerel Modeller:** Bilgisayarınızda yerel çalışan `llama3`, `mistral`, `deepseek` modellerini bağlayabilirsiniz.
5. **OpenAI Uyumlu Modeller:** OpenAI veya uyumlu herhangi bir API endpoint'ini bağlayabilirsiniz.

---

## 📊 Ek Özellikler & Kısayollar

- **Ekran Boyutları:**
  - 📱 Mini Boy (`Ctrl + 1`)
  - 💻 Standart Boy (`Ctrl + 2`)
  - 🖥️ Mega Boy (`Ctrl + 3`)
  - 🔲 Tam Ekran (`F11`)
- **İstatistik & Geçmiş:** `Ctrl + I` (Tüm maç analizleri, kazanma oranı ve süreler)
- **Hakkında & Künye:** `F1` veya `Ctrl + H`
