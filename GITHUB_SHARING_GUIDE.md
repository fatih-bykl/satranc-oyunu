# 🚀 GitHub'da Paylaşma ve Yayınlama Rehberi

Bu kılavuz, projenizi GitHub hesabınızda (`https://github.com/fatih-bykl`) nasıl yayınlayacağınızı ve Windows / Linux indirme paketlerini **GitHub Releases** bölümüne nasıl yükleyeceğinizi adım adım anlatır.

---

## 1. Adım: GitHub'da Yeni Bir Depo (Repository) Oluşturun
1. [GitHub](https://github.com/new) sayfasına gidin.
2. **Repository name** kısmına `satranc-oyunu` veya `chess-game` yazın.
3. **Public** (Herkese Açık) seçeneğini işaretleyin.
4. *"Initialize this repository with a README"* seçeneğini **İŞARETLEMEYİN** (çünkü dosyalarımız zaten hazır).
5. **Create repository** butonuna tıklayın.

---

## 2. Adım: Projeyi GitHub'a Yükleyin (Push)
Terminalinizi açın ve aşağıdaki komutları sırasıyla çalıştırın:

```bash
# Proje dizinine geçin (Örn: Linux klasörü)
cd "/run/media/fatih/usb/04 - Uygulama Oluşturma/Linux/satranç"

# Git deposunu başlatın
git init
git branch -M main

# Tüm proje dosyalarını ekleyin
git add .
git commit -m "feat: Satranç Oyunu v1.0.0 (Linux & Windows Yapay Zeka Destekli)"

# Kendi GitHub deponuzun linkini ekleyin (Kullanıcı adınızı ve repo adınızı kontrol edin)
git remote add origin https://github.com/fatih-bykl/satranc-oyunu.git

# GitHub'a gönderin
git push -u origin main
```

---

## 3. Adım: Windows ve Linux İndirme Dosyalarını "Releases" Bölümüne Ekleyin

Kullanıcıların doğrudan tek tıkla `.zip` veya `.tar.gz` olarak indirebilmesi için:

1. GitHub'da oluşturduğunuz deponun ana sayfasına gidin.
2. Sağ tarafta bulunan **"Releases"** başlığı altındaki **"Create a new release"** bağlantısına tıklayın.
3. **Tag version:** `v1.0.0` yazın.
4. **Release title:** `Satranç Oyunu v1.0.0 - Windows & Linux Sürümü` yazın.
5. **Açıklama (Description)** kutusuna aşağıdaki metni yapıştırın:

```markdown
## ♟️ Satranç Oyunu v1.0.0 - İlk Kararlı Sürüm

Modüler yapay zeka entegrasyonuna (Stockfish, Gemini, Ollama), özel PNG taş desteğine, değerlendirme çubuğuna, saatlere ve kapsamlı istatistik analizlerine sahip modern satranç uygulaması.

### 📦 İndirme Seçenekleri:
- **🪟 Windows için:** `Satranc-Oyunu-Windows-v1.0.0.zip` dosyasını indirin ve içindeki `install-desktop.bat` veya `run.bat` ile başlatın.
- **🐧 Linux için:** `Satranc-Oyunu-Linux-v1.0.0.tar.gz` veya `.zip` dosyasını indirin ve `./install-desktop.sh` veya `./run.sh` ile başlatın.

### 🌟 Öne Çıkan Özellikler:
- 🤖 **Yapay Zeka:** Stockfish UCI, Google Gemini API, yerel Ollama modelleri ve çevrimdışı yerleşik yapay zeka.
- 🎨 **Özel PNG Taşlar:** Kendi PNG taş setinizi ekleyebilme.
- 📐 **Çoklu Boyut:** Mini Boy (`Ctrl+1`), Standart Boy (`Ctrl+2`), Mega Boy (`Ctrl+3`), Tam Ekran (`F11`).
- 📊 **İstatistikler:** Kazanma oranı, rekorlar, ortalama maç süresi ve geçmiş tablosu (`Ctrl+I`).
- ℹ️ **Geliştirici:** Fatih Bıyıklı (İnternet Sihirbazı)
```

6. **Attach binaries by dropping them here or selecting them** alanına şu 3 hazır dosyayı sürükleyip bırakın:
   - `releases/Satranc-Oyunu-Windows-v1.0.0.zip`
   - `releases/Satranc-Oyunu-Linux-v1.0.0.tar.gz`
   - `releases/Satranc-Oyunu-Linux-v1.0.0.zip`
7. **"Publish release"** butonuna tıklayın.

🎉 Tebrikler! Artık projeniz tüm dünyaya açık, indirme linkleri hazır ve profesyonel bir şekilde GitHub'da yayınlanmış durumdadır.
