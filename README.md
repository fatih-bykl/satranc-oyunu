# ♟️ Linux Modüler Yapay Zeka Satranç Oyunu

Linux ortamında **Visual Studio Code** ile geliştirilmek üzere tasarlanmış; özel PNG taş setlerini destekleyen, değerlendirme çubuğu (Eval bar), gelişmiş saat/zamanlayıcı ve **dilediğiniz yapay zeka modelini (UCI motorları + LLM modelleri)** ekleyip karşılıklı oynayabileceğiniz modern bir satranç uygulaması.

---

## 🚀 Hızlı Başlangıç

### 1. Visual Studio Code ile Çalıştırma (Önerilen)
1. **VS Code**'u açın ve `satranç` klasörünü açın (`File -> Open Folder...`).
2. Klavyeden **`F5`** tuşuna basın veya sol taraftaki **Run & Debug** sekmesinden *"Satranç Oyunu Başlat"* seçeneğini tıklayın.
3. Uygulama otomatik olarak sanal ortamı (`venv`) kullanarak başlayacaktır.

### 2. Terminal Üzerinden Çalıştırma
Proje dizinindeyken tek komutla çalıştırabilirsiniz:
```bash
./run.sh
```

---

## 🎨 Kendi PNG Taşlarınızı Ekleme

Taşlarınızın PNG görsellerini `assets/pieces/` klasörüne kopyalamanız yeterlidir. Uygulama taşları otomatik olarak algılar ve yükler.

### Dosya Adlandırma Standartları:
| Taş Türü | Beyaz Taş Dosya Adı | Siyah Taş Dosya Adı |
| :--- | :--- | :--- |
| **Piyon** | `wP.png` veya `white_pawn.png` | `bP.png` veya `black_pawn.png` |
| **Kale** | `wR.png` veya `white_rook.png` | `bR.png` veya `black_rook.png` |
| **At** | `wN.png` veya `white_knight.png` | `bN.png` veya `black_knight.png` |
| **Fil** | `wB.png` veya `white_bishop.png` | `bB.png` veya `black_bishop.png` |
| **Vezir** | `wQ.png` veya `white_queen.png` | `bQ.png` veya `black_queen.png` |
| **Şah** | `wK.png` veya `white_king.png` | `bK.png` veya `black_king.png` |

> 💡 **Not:** Eğer henüz PNG dosyalarını eklemediyseniz, uygulama çökmeyip otomatik olarak yüksek kaliteli vektörel yedek taşları çizer. PNG eklediğinizde yeni görseller otomatik olarak devreye girer.

---

## 🤖 Yapay Zeka (AI) Entegrasyonu & Yeni Model Ekleme

Uygulamanın üst çubuğundaki **"🤖 AI Yönet"** butonuna basarak istediğiniz yapay zekayı ekleyebilir, ayarlarını düzenleyebilir ve bağlantısını test edebilirsiniz.

### Desteklenen Yapay Zeka Türleri:

1. **Yerleşik Python Motoru (Built-in Heuristic AI):**
   - İnternet bağlantısı veya harici dosya gerektirmez.
   - *Kolay (Acemi)*, *Orta (Kulüp)* ve *Zor (Usta)* seviyeleri bulunur.
2. **UCI Satranç Motorları (Stockfish, LCZero, Komodo vb.):**
   - Sisteminizde yüklü olan veya derlediğiniz satranç motorunun dosya yolunu (örneğin `/usr/bin/stockfish`) göstererek ekleyebilirsiniz.
   - *Arama Derinliği (Depth)*, *Düşünme Süresi (sn)* ve *Yetenek Seviyesi (Skill Level 0-20)* ayarlanabilir.
   - *Linux'a Stockfish yüklemek için:*
     - Arch / CachyOS: `sudo pacman -S stockfish`
     - Ubuntu / Debian: `sudo apt install stockfish`
     - Fedora: `sudo dnf install stockfish`
3. **Google Gemini API (Gemini 2.5 Flash / Pro):**
   - Gemini API anahtarınızı girerek dünya standartlarında bir büyük dil modeliyle satranç oynayabilirsiniz.
   - Yapay zekaya özel **Persona (Oyun Stili ve Karakter)** verebilirsiniz. Model hem hamle yapar hem de düşüncelerini Türkçe olarak ekrana yazar.
4. **Ollama Yerel Modelleri (Llama 3, Mistral, DeepSeek vb.):**
   - Kendi bilgisayarınızda çalışan Ollama sunucusuna (`http://localhost:11434`) bağlanır.
   - Yüklü olan herhangi bir açık kaynaklı dil modeliyle internete gerek kalmadan oynayabilirsiniz.
5. **OpenAI / Uyumlu API'ler (GPT-4o Mini, DeepSeek API, Groq vb.):**
   - OpenAI uyumlu herhangi bir API uç noktası (`https://api.openai.com/v1`) ve API anahtarı ile dilediğiniz modeli ekleyebilirsiniz.

---

## ⚙️ Oyun & Tahta Özellikleri

- **Zaman Kontrolü:** Süresiz, Bullet (1+1), Blitz (3+2, 5+0), Rapid (10+0, 15+10), Klasik (30+0) ve Özel süreler.
- **Ekran Boyutları:** 📱 Mini Boy (`Ctrl+1`), 💻 Standart Boy (`Ctrl+2`), 🖥️ Mega Boy (`Ctrl+3`), 🔲 Tam Ekran (`F11`).
- **İstatistik ve Maç Geçmişi:** 📊 Toplam maç sayısı, kazanma oranı, ortalama ve en hızlı maç süresi, toplam hamle sayısı ve detaylı maç geçmişi (`Ctrl+I` veya *"📊 İstatistik"* butonu). İstenildiğinde tek tıkla sıfırlanabilir.
- **Hakkında & İletişim:** ℹ️ Oyun özellikleri, sürüm, geliştirici künyesi ve kişisel iletişim bağlantıları (`F1` veya *"ℹ️ Hakkında"* butonu).
- **Taraf Seçimi:** Beyaz, Siyah, Rastgele veya İki Kişilik Yerel Oyun (İnsan vs İnsan).
- **Tahta Temaları:** Zümrüt Yeşili, Klasik Ahşap, Okyanus Mavisi, Koyu Gece.
- **Değerlendirme Çubuğu (Eval Bar):** Pozisyon üstünlüğünü ve mat durumlarını canlı gösterir.
- **PGN Notasyonu:** Tüm hamleleri tek tıkla kopyalama ve analiz etme.
- **Ses Efektleri:** Hamle, taş alma, şah ve oyun sonu sesleri.

---

## 📁 Proje Dizin Yapısı

```text
satranç/
├── .vscode/                 # VS Code Başlatma (launch.json) ve Ayarlar (settings.json)
├── assets/
│   ├── pieces/              # Kendi PNG taşlarınızı buraya atın (wP.png, bK.png vb.)
│   └── sounds/              # Oyun içi ses efektleri (.wav)
├── config/
│   └── ai_models.json       # Kayıtlı yapay zeka profilleri
├── src/
│   ├── main.py              # Uygulama başlangıç noktası
│   ├── core/                # Satranç kural ve saat motoru (python-chess)
│   ├── ai/                  # Modüler yapay zeka adaptörleri (UCI, Gemini, Ollama, OpenAI)
│   ├── ui/                  # PyQt6 arayüz bileşenleri ve pencereler
│   └── utils/               # Varlık ve ses yöneticileri
├── requirements.txt         # Python kütüphaneleri
└── run.sh                   # Linux tek tıkla çalıştırma betiği
```
