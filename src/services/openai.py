import openai
import json
from src.config import Config

openai.api_key = Config.OPENAI_API_KEY

def generate_ai_response(order_data, customer_question):
    """Sipariş verisini ve müşteri sorusunu kullanarak AI cevabı üretir."""
    
    simplified_order = {
        "siparis_numarasi": order_data.get("order_number"),
        "olusturulma_tarihi": order_data.get("created_at"),
        "toplam_fiyat": f"{order_data.get('total_price')} {order_data.get('currency')}",
        "kargo_durumu": order_data.get('fulfillment_status') or 'Hazırlanıyor',
        "musteri_adi": order_data.get('customer', {}).get('first_name', 'Değerli Müşterimiz') if order_data.get('customer') else 'Değerli Müşterimiz'
    }

    prompt = f"""
    Sen bir e-ticaret mağazasının (Kargo Store) son derece yetkin, profesyonel ve çözüm odaklı Kıdemli Müşteri İlişkileri Uzmanısın.
    Amacın, müşterinin sorununu tek seferde anlamak, empati kurmak ve mağaza politikaları çerçevesinde en net çözümü sunmaktır.
    
    --- MAĞAZA POLİTİKALARI (KESİN KURALLAR) ---
    {Config.STORE_POLICY_RETURNS}
    
    {Config.STORE_POLICY_SHIPPING}
    ---------------------------------------------
    
    --- SİPARİŞ DETAYLARI ---
    {json.dumps(simplified_order, indent=2, ensure_ascii=False)}
    -------------------------
    
    --- MÜŞTERİ SORUSU ---
    "{customer_question}"
    ----------------------
    
    --- DAVRANIŞ VE YANITLAMA YÖNERGESİ ---
    
    1. **KİMLİK VE TON:**
       - İsmin "Asistan".
       - Tonun: Saygılı, yardımsever, güven verici ve kurumsal. Asla robotik olma.
       - Müşteriye ismiyle hitap et ("Sayın Ahmet Bey" veya "Ayşe Hanım" gibi). İsim yoksa "Değerli Müşterimiz" de.
    
    2. **SENARYO ANALİZİ VE AKSİYONLAR:**
    
       A) **İADE VE DEĞİŞİM TALEPLERİ:**
          - Önce sipariş tarihini ({simplified_order.get('olusturulma_tarihi')}) kontrol et. Bugünün tarihini varsayarak 30 günü geçip geçmediğini hesapla.
          - **Süre Geçmişse:** "Üzülerek belirtmek isterim ki, iade politikamız gereği 30 günlük süreyi aşmış bulunmaktayız. Bu nedenle iade işleminizi başlatamıyorum." şeklinde nazikçe reddet.
          - **Süre Geçmemişse:** "İade sürecinizi hemen başlatabiliriz. Ürünün kullanılmamış ve orijinal paketinde olması gerektiğini hatırlatmak isterim." de ve İade Kodu: **MOCK_IADE_KODU_123** bilgisini ver.
          - **İstisna:** Eğer müşteri "ürün kusurlu/yırtık/bozuk" diyorsa, 30 gün kuralını esnet ve "Kusurlu ürün teslimatı için çok özür dileriz, hemen ücretsiz değişim veya iade yapalım." de.
    
       B) **KARGO VE TESLİMAT:**
import openai
import json
from src.config import Config
from src.services.shopify import cancel_order, check_product_stock, get_store_token

openai.api_key = Config.OPENAI_API_KEY

def generate_ai_response(order, question, shop_url=None):
    """
    OpenAI kullanarak sipariş verilerine göre cevap üretir.
    Function Calling destekler.
    """
    
    # Mevcut sipariş durumu özeti
    order_summary = f"""
    Sipariş No: {order.get('name')}
    Durum: {order.get('financial_status')} / {order.get('fulfillment_status') or 'Gönderilmedi'}
    Toplam: {order.get('total_price')} {order.get('currency')}
    Ürünler: {', '.join([item['name'] for item in order.get('line_items', [])])}
    """
    
    system_prompt = f"""
    Sen yardımsever bir e-ticaret asistanısın.
    Şu anki sipariş bilgileri:
    {order_summary}
    
    Kullanıcı sipariş iptali isterse, önce mutlaka sebep sor ve onay iste.
    Onay verirse 'cancel_order' fonksiyonunu kullan.
    Ürün sorarsa 'check_product_stock' fonksiyonunu kullan.
    """
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "cancel_order",
                "description": "Mevcut siparişi iptal eder. Sadece kullanıcı açıkça onayladığında kullan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {"type": "string", "description": "İptal sebebi"}
                    },
                    "required": ["reason"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "check_product_stock",
                "description": "Bir ürünün stok durumunu kontrol eder.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {"type": "string", "description": "Aranan ürünün adı"}
                    },
                    "required": ["product_name"]
                }
            }
        }
    ]

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ]
        
        # 1. İlk çağrı (Fonksiyon kullanmak isteyecek mi?)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        
        # Eğer fonksiyon çağırmak istiyorsa
        if response_message.tool_calls:
            # Fonksiyon çağrısını mesaja ekle
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                function_response = "İşlem başarısız."
                
                # Access token al
                access_token = get_store_token(shop_url)
                
                if function_name == "cancel_order":
                    result = cancel_order(shop_url, access_token, order['id'])
                    function_response = json.dumps(result)
                    
                elif function_name == "check_product_stock":
                    result = check_product_stock(shop_url, access_token, function_args.get("product_name"))
                    function_response = result
                
                # Fonksiyon sonucunu mesaja ekle
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            
            # 2. İkinci çağrı (Sonucu yorumlayıp cevap ver)
            second_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True 
            )
            
            for chunk in second_response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        else:
            # Fonksiyon yoksa normal cevap (Streaming)
            # Not: İlk response stream=False idi, şimdi içeriğini stream gibi verelim
            yield response_message.content

    except Exception as e:
        yield f"Bir hata oluştu: {e}"
