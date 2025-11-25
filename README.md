# Shopify AI Müşteri Hizmetleri Asistanı

Bu proje, Shopify mağazaları için geliştirilmiş, OpenAI destekli akıllı bir müşteri hizmetleri asistanıdır. Müşterilerin sipariş durumlarını sorgulamalarına ve sorularına anında yanıt almalarına olanak tanır.

## 🚀 Özellikler

*   **Shopify Entegrasyonu:** Mağaza sipariş verilerini otomatik çeker.
*   **Yapay Zeka (OpenAI):** Müşteri sorularını doğal dilde, sipariş bağlamına göre yanıtlar.
*   **Veritabanı (Supabase):** Mağaza erişim bilgilerini güvenli bir şekilde saklar.
*   **Modern Arayüz:** Müşteriler için şık ve kullanımı kolay bir sohbet ekranı.

## 📂 Proje Yapısı

```
shopifyApps/
├── src/
│   ├── static/          # CSS ve JavaScript dosyaları
│   ├── templates/       # HTML şablonları
│   ├── services/        # İş mantığı (Shopify, OpenAI, DB)
│   ├── routes.py        # Web yönlendirmeleri
│   └── config.py        # Ayarlar
├── legacy/              # Eski kodlar (Arşiv)
├── run.py               # Uygulama başlatıcı
├── start.bat            # Windows için hızlı başlatma betiği
├── requirements.txt     # Gerekli kütüphaneler
└── .env                 # Gizli anahtarlar (API Key vb.)
```

## 🛠 Kurulum ve Çalıştırma

1.  **Gereksinimleri Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Ayarları Yapılandırın:**
    `.env` dosyasındaki API anahtarlarını kendi bilgilerinizle güncelleyin.

3.  **Uygulamayı Başlatın:**
    Terminalden:
    ```bash
    python run.py
    ```
    Veya Windows'ta `start.bat` dosyasına çift tıklayın.

4.  **Tarayıcıda Açın:**
    [http://127.0.0.1:3000](http://127.0.0.1:3000) adresine gidin.

## 📝 Kullanım

1.  Açılan sayfada **Mağaza URL** ve **Sipariş Numarası** girin.
2.  "Sorgula ve Başla" butonuna tıklayın.
3.  Asistana "Siparişim nerede?", "İade edebilir miyim?" gibi sorular sorun.
