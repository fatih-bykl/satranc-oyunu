# ♟️ Satranç Oyunu (Modüler Yapay Zeka Destekli)

Modern, özelleştirilebilir, çoklu yapay zeka (Heuristic, Stockfish UCI, Google Gemini, Ollama, OpenAI) entegrasyonu ve özel PNG taş seti desteği sunan masaüstü satranç uygulaması. **Windows** ve **Linux** işletim sistemleriyle tam uyumludur.

---

## 📥 İndirme Bağlantıları (Sürüm v1.0.0)

Doğrudan kullanıma hazır en güncel sürüm paketleri:

| Platform | Paket Türü | Doğrudan İndirme Bağlantısı | Açıklama |
| :--- | :--- | :--- | :--- |
| 🪟 **Windows** | **Kurulum Sihirbazı (Setup .exe)** | [**Satranc-Oyunu-Kurulum.exe**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Kurulum.exe) | **Önerilen:** Çift tıkla `C:\satrancoyunu` klasörüne kurar, masaüstü ve başlat menüsü kısayollarını ekler. Ek yazılım gerektirmez. |
| 🪟 **Windows** | **Taşınabilir Arşiv (.zip)** | [**Satranc-Oyunu-Windows-v1.0.0.zip**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Windows-v1.0.0.zip) | Kurulum yapmadan klasörden çalıştırmak için. |
| 🐧 **Linux** | **Otomatik Kurulum (.tar.gz)** | [**Satranc-Oyunu-Linux-v1.0.0.tar.gz**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Linux-v1.0.0.tar.gz) | **Önerilen:** Arşivi açıp `./install-desktop.sh` ile masaüstü ve başlat menüsüne entegre edebilirsiniz. |
| 🐧 **Linux** | **Sıkıştırılmış Arşiv (.zip)** | [**Satranc-Oyunu-Linux-v1.0.0.zip**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Linux-v1.0.0.zip) | Standart Zip formatı. |

Tüm sürümleri ve değişiklik geçmişini incelemek için: **[GitHub Releases Sayfası](https://github.com/fatih-bykl/satranc-oyunu/releases/tag/v1.0.0)**

---

## 🚀 Hızlı Başlangıç

### 🪟 Windows Kullanıcıları İçin
1. [**Satranc-Oyunu-Kurulum.exe**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Kurulum.exe) dosyasını indirin.
2. Çift tıklayarak kurulum sihirbazını başlatın ve yönergeleri takip edin.
3. Masaüstünüzdeki veya Başlat Menünüzdeki **Satranç Oyunu** kısayoluna tıklayarak hemen oynamaya başlayın.

### 🐧 Linux Kullanıcıları İçin
1. [**Satranc-Oyunu-Linux-v1.0.0.tar.gz**](https://github.com/fatih-bykl/satranc-oyunu/releases/download/v1.0.0/Satranc-Oyunu-Linux-v1.0.0.tar.gz) arşivini indirin ve açın.
2. Terminali klasörün içinde açıp şu komutla masaüstü kısayolunu oluşturun:
   ```bash
   ./install-desktop.sh
   ```
3. Ya da doğrudan terminalden çalıştırmak için:
   ```bash
   ./run.sh
   ```

### 💻 Geliştiriciler İçin (Visual Studio Code)
1. Proje klasörünü VS Code ile açın (`File -> Open Folder...`).
2. Klavyeden **`F5`** tuşuna basarak doğrudan hata ayıklama modunda çalıştırın.

---

## 🤖 Yapay Zeka (AI) Motorları ve Entegrasyonlar

Üst araç çubuğundaki **"🤖 AI Yönet"** butonu ile yapay zeka profillerini yönetebilir, yeni modeller ekleyebilirsiniz:

1. **Yerleşik Python Motoru (Heuristic AI):**
   - İnternet bağlantısı veya harici dosya gerektirmez.
   - *Kolay (Acemi)*, *Orta (Kulüp)* ve *Zor (Usta)* seviyeleri bulunur.
   - Zaman kısıtlamalı yinelemeli derinleşme (Iterative Deepening) ve kilitlenmeyen güvenlik mimarisi ile donatılmıştır.
2. **Stockfish UCI Satranç Motoru:**
   - Sisteminizdeki Stockfish motorunu (Linux'ta `/usr/bin/stockfish`, Windows'ta `stockfish.exe`) bağlayabilirsiniz.
   - Düşünme süresi, arama derinliği ve 0-20 arası yetenek seviyesi (Skill Level) ayarlanabilir.
3. **Google Gemini API:**
   - Gemini API anahtarınızı girerek persona destekli, hamle yaparken Türkçe yorum yazan yapay zeka ile oynayabilirsiniz.
4. **Ollama Yerel Modelleri:**
   - Bilgisayarınızda çalışan Ollama modellerine (`llama3`, `mistral`, `deepseek`) bağlanabilirsiniz.
5. **OpenAI / Uyumlu API'ler:**
   - OpenAI uyumlu herhangi bir API endpoint'ini (`https://api.openai.com/v1`) ve anahtarını bağlayabilirsiniz.

---

## 🎨 Kendi PNG Taşlarınızı Ekleme

Uygulama, kendi özel grafiklerinizi kullanmanıza imkan tanır. PNG formatındaki görsellerinizi `assets/pieces/` dizinine kopyalamanız yeterlidir:

| Taş Türü | Beyaz Taş Dosya Adı | Siyah Taş Dosya Adı |
| :--- | :--- | :--- |
| **Piyon** | `wP.png` veya `white_pawn.png` | `bP.png` veya `black_pawn.png` |
| **Kale** | `wR.png` veya `white_rook.png` | `bR.png` veya `black_rook.png` |
| **At** | `wN.png` veya `white_knight.png` | `bN.png` veya `black_knight.png` |
| **Fil** | `wB.png` veya `white_bishop.png` | `bB.png` veya `black_bishop.png` |
| **Vezir** | `wQ.png` veya `white_queen.png` | `bQ.png` veya `black_queen.png` |
| **Şah** | `wK.png` veya `white_king.png` | `bK.png` veya `black_king.png` |

> 💡 **Not:** Eğer PNG dosyası eklemezseniz, sistem otomatik olarak yüksek çözünürlüklü vektörel taşları çizer.

---

## ⚙️ Oyun & Tahta Özellikleri

- **Zaman Kontrolü:** Süresiz, Bullet (1+1), Blitz (3+2, 5+0), Rapid (10+0, 15+10), Klasik (30+0) ve Özel süreler.
- **Ekran Boyutları:**
  - 📱 Mini Boy (`Ctrl + 1`)
  - 💻 Standart Boy (`Ctrl + 2`)
  - 🖥️ Mega Boy (`Ctrl + 3`)
  - 🔲 Tam Ekran (`F11`)
- **İstatistik ve Maç Analizi:** Toplam maç sayısı, kazanma oranı, ortalama ve en hızlı maç süresi, hamle sayıları (`Ctrl + I`).
- **Hakkında & Künye:** Geliştirici bilgileri, sürüm ve iletişim bağlantıları (`F1` veya `Ctrl + H`).
- **Taraf Seçimi:** Beyaz, Siyah, Rastgele veya İki Kişilik Yerel Oyun (İnsan vs İnsan).
- **Tahta Temaları:** Zümrüt Yeşili, Klasik Ahşap, Okyanus Mavisi, Koyu Gece.
- **Değerlendirme Çubuğu (Eval Bar):** Pozisyon üstünlüğünü canlı olarak hesaplar ve görselleştirir.
- **PGN Notasyonu:** Tüm maç hamlelerini tek tıkla kopyalama ve dışa aktarma desteği.
- **Ses Efektleri:** Hamle, taş alma, şah çekme ve oyun sonu sesleri.

---

## 📁 Proje Dizin Yapısı

```text
satranç/
├── .vscode/                 # VS Code Başlatma (launch.json) ve Ayarlar
├── assets/
│   ├── pieces/              # PNG taş setleri
│   └── sounds/              # Oyun içi ses efektleri (.wav)
├── config/
│   └── ai_models.json       # Kayıtlı yapay zeka profilleri
├── src/
│   ├── main.py              # Uygulama başlangıç noktası
│   ├── core/                # Satranç kural ve saat motoru (python-chess)
│   ├── ai/                  # Modüler yapay zeka adaptörleri (UCI, Gemini, Ollama, OpenAI)
│   ├── ui/                  # PyQt6 arayüz bileşenleri ve pencereler
│   └── utils/               # Varlık ve ses yöneticileri
├── requirements.txt         # Gerekli Python paketleri
├── run.sh                   # Linux tek tıkla çalıştırma betiği
└── install-desktop.sh       # Linux masaüstü kısayolu oluşturma betiği
```

---

## 👨‍💻 Geliştirici & Lisans

- **Geliştirici:** Fatih Bıyıklı
- **Web Sitesi:** [internetsihirbazi.com](https://www.internetsihirbazi.com)
- **GitHub:** [github.com/fatih-bykl/satranc-oyunu](https://github.com/fatih-bykl/satranc-oyunu)
- **Lisans:** MIT
