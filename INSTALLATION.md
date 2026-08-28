# ♟️ Satranç Oyunu - Kurulum ve Kullanım Kılavuzu

Bu belge, **Satranç Oyunu** masaüstü uygulamasını **Linux** ve **Windows** işletim sistemlerinde nasıl kuracağınızı, çalıştıracağınızı ve özelleştireceğinizi detaylı olarak açıklamaktadır.

---

## 🪟 Windows Kurulum & Çalıştırma Rehberi

### 1. Yöntem: Standart Kurulum Sihirbazı (.exe) - (ÖNERİLEN)
1. **[Satranc-Oyunu-Kurulum.exe](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Kurulum.exe)** dosyasını indirin.
2. İndirdiğiniz `.exe` dosyasına çift tıklayın.
3. Kurulum sihirbazı otomatik olarak açılır ve varsayılan olarak **`C:\Satranç Oyunu`** klasörüne tüm bağımsız çalışma ortamıyla birlikte kurulumu yapar.
4. **Masaüstünüze ve Başlat Menünüze** otomatik olarak "Satranç Oyunu" kısayolu yerleştirilir.
5. Bilgisayarınızda Python veya başka hiçbir ek yazılım yüklü olmasına **gerek yoktur**, oyun doğrudan başlar!

### 2. Yöntem: Taşınabilir (Portable Zip)
1. `Satranc-Oyunu-Windows-v1.0.0.zip` dosyasını indirin ve klasöre çıkartın.
2. Klasör içindeki `SatrancOyunu.exe` veya `run.bat` ile başlatın.

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
