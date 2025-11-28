# Shopify AI Asistanı: Yetenekler, Sınırlar ve İzinler Rehberi

Bu belge, OpenAI Function Calling ile Shopify üzerinde yapılabilecek işlemleri, teknik/etik sınırları ve gerekli API izinlerini (Scopes) referans olarak sunar. Müşteri taleplerini değerlendirirken bu rehberi kullanabilirsiniz.

## 1. Neler Yapabiliriz? (Capabilities) ✅

AI'a "Function Calling" ile aşağıdaki yetenekleri kazandırabiliriz. Her yetenek için ilgili Shopify izni (Scope) gereklidir.

| Kategori | İşlem (Aksiyon) | Açıklama | Gerekli Shopify İzni (Scope) |
| :--- | :--- | :--- | :--- |
| **Siparişler** | **Durum Sorgulama** | "Kargom nerede?", "Siparişim ne durumda?" | `read_orders` |
| | **Sipariş İptali** | "Siparişimi iptal et" (Onaylı) | `write_orders` |
| | **Adres Güncelleme** | "Teslimat adresimi değiştir" | `write_orders` |
| | **Sipariş Notu Ekleme** | "Hediye paketi olsun", "Zile basmayın" | `write_orders` |
| | **Geçmiş Siparişler** | "Daha önce ne almıştım?" (Müşteri ID ile) | `read_orders`, `read_customers` |
| **Ürünler** | **Stok/Fiyat Sorma** | "X ürünü var mı?", "Fiyatı ne kadar?" | `read_products` |
| | **Ürün Önerme** | "Yazlık elbise önerir misin?" (Koleksiyon tarama) | `read_products` |
| **Müşteriler** | **Bilgi Güncelleme** | "Telefon numaramı güncelle" | `write_customers` |
| | **Etiketleme (Tag)** | Müşteriye "VIP", "Sorunlu" gibi etiket atama | `write_customers` |
| **İndirimler** | **Kupon Oluşturma** | "Bana özel indirim kodu ver" | `write_discounts`, `write_price_rules` |

---

## 2. Neler Yapamayız? (Limitations) ❌

Teknik veya güvenlik kısıtlamaları nedeniyle yapılamayan işlemler.

*   **Ödeme Alma/İşleme:** AI sohbet penceresi üzerinden kredi kartı bilgisi alıp ödeme geçemez (PCI DSS Güvenlik Standartları gereği yasaktır). Ödeme sadece Shopify Checkout sayfasında olur.
*   **Şifre İşlemleri:** Müşterinin şifresini göremez, değiştiremez veya sıfırlayamaz.
*   **Sepete Ürün Ekleme (Doğrudan):** Admin API ile müşterinin o anki tarayıcı sepetine (Cart) müdahale etmek zordur (Storefront API gerekir, farklı bir yapıdır). Genelde "Sepete Ekle" linki verilir.
*   **Anlık Banka İadesi (Refund):** İade süreci başlatılabilir (`write_orders`) ama paranın müşterinin hesabına geçmesi bankaya bağlıdır, AI bunu garanti edemez veya hızlandıramaz.

---

## 3. Neler Yapmamalıyız? (Safety & Ethics) ⚠️

Teknik olarak mümkün olsa bile, AI'a verilmesi **riskli** olan yetkiler.

*   **Onaysız Veri Silme:** AI'a "Ürün Silme" veya "Müşteri Silme" yetkisi **asla verilmemelidir**. Yanlış anlama sonucu mağazayı boşaltabilir.
*   **Toplu İşlemler:** "Tüm siparişleri iptal et" gibi komutlar engellenmelidir.
*   **Fiyat Değiştirme:** `write_products` yetkisi ile AI ürün fiyatlarını değiştirebilir ama bu çok risklidir. Müşteri "Fiyatı 1 TL yap" derse ve AI kanarsa büyük zarar oluşur.
*   **Hassas Veri Paylaşımı:** AI, bir müşterinin bilgisini başka bir müşteriye asla göstermemelidir (Sipariş No + Email doğrulaması bu yüzden şarttır).

---

## 4. İzinler (Scopes) Nasıl Yönetilir?

Uygulamayı kurarken (`src/config.py` içinde `SHOPIFY_SCOPES`) bu izinleri baştan belirtmeniz gerekir.

**Örnek Konfigürasyon:**
```python
# Sadece okuma yapan basit bir asistan için:
SHOPIFY_SCOPES = "read_orders,read_products"

# İptal edebilen, adres değiştirebilen gelişmiş asistan için:
SHOPIFY_SCOPES = "read_orders,write_orders,read_products,read_customers,write_customers"
```

**Önemli Not:** Yeni bir özellik eklediğinizde (örneğin İndirim Kodu oluşturma), `SHOPIFY_SCOPES`'a `write_discounts` ekleyip uygulamanın mağazada **yeniden kurulması (re-install)** gerekir.
