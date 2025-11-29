import openai
import json
from src.config import Config
from src.services.shopify import cancel_order, check_product_stock, update_shipping_address, add_order_note, create_discount_code, get_order_by_number, get_shop_info
from src.services.db import get_store_token, create_or_update_session, get_chat_history, add_chat_message

openai.api_key = Config.OPENAI_API_KEY

def generate_ai_response(session_id, shop_url, question, session_data=None):
    """
    OpenAI kullanarak cevap üretir.
    Session verisine göre bağlam (Context) değişir.
    Geçmiş konuşmaları (History) dikkate alır.
    """
    
    # 1. BAĞLAM BELİRLEME (Context)
    order_context = ""
    system_instruction = ""
    
    # Mağaza Bilgilerini Çek (Adres için)
    access_token = get_store_token(shop_url)
    shop_info = get_shop_info(shop_url, access_token)
    
    shop_address = "Adres bilgisi alınamadı."
    if shop_info:
        shop_address = f"{shop_info.get('address1', '')}, {shop_info.get('city', '')}, {shop_info.get('country', '')}"
    
    # Politikaları güncelle
    policy_returns = Config.STORE_POLICY_RETURNS.replace("{SHOP_ADDRESS}", shop_address)
    
    # Eğer oturumda doğrulanmış bir sipariş varsa, detayları çek
    if session_data and session_data.get('order_id') and session_data.get('email'):
        order = get_order_by_number(shop_url, access_token, session_data['order_id'], session_data['email'])
        
        if order:
            order_context = f"""
            --- AKTİF SİPARİŞ BİLGİSİ ---
            Sipariş No: {order.get('name')}
            Durum: {order.get('financial_status')} / {order.get('fulfillment_status') or 'Gönderilmedi'}
            Toplam: {order.get('total_price')} {order.get('currency')}
            Ürünler: {', '.join([item['name'] for item in order.get('line_items', [])])}
            Müşteri Notu: {order.get('note') or 'Yok'}
            Teslimat Adresi: {order.get('shipping_address', {}).get('address1', '')}, {order.get('shipping_address', {}).get('city', '')}
            -----------------------------
            """
            system_instruction = """
            Şu an doğrulanmış bir müşteriyle konuşuyorsun. Sipariş detaylarına tam erişimin var.
            Müşteri siparişle ilgili işlem yapmak isterse (iptal, adres vb.) yardımcı ol.
            """
        else:
            # Sipariş bulunamadıysa (belki iptal edildi veya silindi)
            system_instruction = "Kullanıcının sipariş kaydı var ama güncel veriye erişilemedi. Tekrar sipariş numarası isteyebilirsin."
    else:
        # Henüz giriş yapmamış kullanıcı
        system_instruction = """
        Şu an kimliği doğrulanmamış bir ziyaretçiyle konuşuyorsun.
        Genel sorulara (kargo ücreti, iade politikası, stok durumu) cevap verebilirsin.
        
        EĞER kullanıcı "Siparişim nerede?", "İptal et" gibi kişisel bir işlem isterse:
        "Size yardımcı olabilmem için lütfen sipariş numaranızı ve e-posta adresinizi yazar mısınız?" diye sor.
        Kullanıcı bu bilgileri verince 'authenticate_customer' fonksiyonunu kullan.
        """

    # Mantık Kuralları (Hallucination Önleme)
    logic_rules = """
    --- KARAR VERME KURALLARI (ÖNCELİKLİ) ---
    1. ÖNCE SİPARİŞ DURUMUNU KONTROL ET:
       - Eğer sipariş durumu 'cancelled' (iptal) ise, iade işlemi YAPILAMAZ. Kullanıcıya "Siparişiniz zaten iptal edilmiş." de.
       - Eğer sipariş durumu 'unfulfilled' (gönderilmedi) ise, iade değil "İptal" öner.
    
    2. ÜRÜN TÜRÜNÜ KONTROL ET:
       - İade yasağını (iç giyim/kişisel bakım) SADECE ürün adında "külot", "boxer", "sütyen", "krem", "parfüm" gibi net ifadeler varsa uygula.
       - Emin değilsen yasaklama.
       
    3. TARİHİ KONTROL ET:
       - Sipariş tarihinden 30 gün geçmişse iade alma.
       
    4. İNDİRİM KODU OLUŞTURMA VE TEKLİF ETME (SATIŞ STRATEJİSİ):
       - SADECE kullanıcı giriş yapmışsa (sipariş numarası ve e-posta doğrulanmışsa) indirim konuş.
       
       Aşağıdaki durumlarda inisiyatif al ve indirim teklif et:
       a) YÜKSEK TUTARLI SİPARİŞ: Eğer aktif sipariş tutarı 20000 TL üzerindeyse ve müşteri yeni ürün soruyorsa -> %10 İndirim teklif et.
       b) GECİKME/MEMNUNİYETSİZLİK: Eğer sipariş durumu "unfulfilled" ve müşteri şikayetçiyse -> Özür dilemek için %15 İndirim teklif et.
       c) İKİNCİ SİPARİŞ TEŞVİKİ: Müşteri sipariş durumunu sordu ve her şey yolundaysa -> "Bir sonraki siparişinizde geçerli %5 indirim ister misiniz?" diye sor.
       
       KURALLAR:
       - Maksimum indirim oranı %15'tir.
       - Kullanıcı %50 gibi yüksek oran isterse: "Maalesef o kadar yapamam ama sizin için %10 tanımlayabilirim" de.
       - İndirim kodu oluştururken 'create_discount_code' fonksiyonunu kullan.
       - ÖNEMLİ: İndirim kodu HER ZAMAN benzersiz olmalıdır. Kodun sonuna rastgele 4 hane ekle. Örn: "OZEL10" yerine "OZEL10-X9Y2".
    -----------------------------------------
    """

    system_prompt = f"""
    Sen SuDe'nin yardımsever ve profesyonel AI asistanısın.
    {policy_returns}
    {Config.STORE_POLICY_SHIPPING}
    
    {logic_rules}
    
    {order_context}
    
    {system_instruction}
    """
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "authenticate_customer",
                "description": "Kullanıcının sipariş numarası ve e-postası ile kimliğini doğrular.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "order_number": {"type": "string", "description": "Sipariş Numarası (örn: 1001)"},
                        "email": {"type": "string", "description": "Müşteri E-postası"}
                    },
                    "required": ["order_number", "email"]
                }
            }
        },
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
        },
        {
            "type": "function",
            "function": {
                "name": "update_shipping_address",
                "description": "Siparişin teslimat adresini günceller.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address1": {"type": "string", "description": "Sokak, Cadde, No"},
                        "city": {"type": "string", "description": "Şehir"},
                        "zip": {"type": "string", "description": "Posta Kodu (Opsiyonel)"},
                        "country": {"type": "string", "description": "Ülke (Varsayılan: Turkey)"}
                    },
                    "required": ["address1", "city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "add_order_note",
                "description": "Siparişe not ekler (Hediye paketi, zile basma vb).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "note": {"type": "string", "description": "Eklenecek not"}
                    },
                    "required": ["note"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_discount_code",
                "description": "Müşteriye özel indirim kodu oluşturur.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "İndirim kodu (örn: OZEL10)"},
                        "amount": {"type": "string", "description": "İndirim miktarı (Sayısal)"},
                        "type": {"type": "string", "enum": ["fixed_amount", "percentage"], "description": "İndirim tipi"}
                    },
                    "required": ["code", "amount", "type"]
                }
            }
        }
    ]

    try:
        # 2. GEÇMİŞİ ÇEK (History)
        history = get_chat_history(session_id, limit=6) # Son 6 mesaj (3 tur)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Geçmiş mesajları ekle
        for msg in history:
            messages.append({"role": msg['role'], "content": msg['content']})
            
        # Yeni soruyu ekle
        messages.append({"role": "user", "content": question})
        
        # Kullanıcı mesajını kaydet
        add_chat_message(session_id, "user", question)
        
        # 3. İLK ÇAĞRI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.7
        )
        
        response_message = response.choices[0].message
        full_ai_response = ""
        
        if response_message.tool_calls:
            messages.append(response_message)
            
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                function_response = "İşlem başarısız."
                
                access_token = get_store_token(shop_url)
                
                # --- KİMLİK DOĞRULAMA ---
                if function_name == "authenticate_customer":
                    order_num = function_args.get("order_number")
                    email = function_args.get("email")
                    
                    # Shopify'dan kontrol et
                    order = get_order_by_number(shop_url, access_token, order_num, email)
                    
                    if order:
                        # Başarılı! Oturumu güncelle
                        create_or_update_session(session_id, shop_url, order_num, email)
                        
                        # KRİTİK: Local session_data'yı güncelle ki sonraki adımlar (adres güncelleme vb.) bunu görsün
                        if session_data is None:
                            session_data = {}
                        session_data['order_id'] = str(order_num)
                        session_data['email'] = email
                        
                        function_response = f"Doğrulama başarılı! Sayın {order.get('customer', {}).get('first_name', 'Müşterimiz')}, siparişinize eriştim. Nasıl yardımcı olabilirim?"
                    else:
                        function_response = "Doğrulama başarısız. Lütfen sipariş numarası ve e-posta adresinizi kontrol edin."

                # --- DİĞER FONKSİYONLAR ---
                elif function_name == "cancel_order":
                    # Sadece oturum açmış kullanıcı yapabilir
                    if session_data and session_data.get('order_id'):
                         current_order = get_order_by_number(shop_url, access_token, session_data['order_id'], session_data['email'])
                         if current_order:
                             result = cancel_order(shop_url, access_token, current_order['id'])
                             function_response = json.dumps(result)
                         else:
                             function_response = "Sipariş verisine erişilemedi."
                    else:
                         function_response = "Bu işlem için önce kimlik doğrulaması yapmalısınız."

                elif function_name == "check_product_stock":
                    result = check_product_stock(shop_url, access_token, function_args.get("product_name"))
                    function_response = result
                    
                elif function_name == "update_shipping_address":
                    if session_data and session_data.get('order_id'):
                        current_order = get_order_by_number(shop_url, access_token, session_data['order_id'], session_data['email'])
                        if current_order:
                            address_data = {
                                "address1": function_args.get("address1"),
                                "city": function_args.get("city"),
                                "zip": function_args.get("zip", ""),
                                "country": function_args.get("country", "Turkey")
                            }
                            result = update_shipping_address(shop_url, access_token, current_order['id'], address_data)
                            function_response = json.dumps(result)
                    else:
                        function_response = "Bu işlem için önce kimlik doğrulaması yapmalısınız."
                    
                elif function_name == "add_order_note":
                    if session_data and session_data.get('order_id'):
                        current_order = get_order_by_number(shop_url, access_token, session_data['order_id'], session_data['email'])
                        if current_order:
                            result = add_order_note(shop_url, access_token, current_order['id'], function_args.get("note"))
                            function_response = json.dumps(result)
                    else:
                        function_response = "Bu işlem için önce kimlik doğrulaması yapmalısınız."
                    
                elif function_name == "create_discount_code":
                    result = create_discount_code(
                        shop_url, 
                        access_token, 
                        function_args.get("code"), 
                        function_args.get("amount"), 
                        function_args.get("type")
                    )
                    function_response = json.dumps(result)
                
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            
            second_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                stream=True 
            )
            
            for chunk in second_response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_ai_response += content
                    yield content
                    
        else:
            # Fonksiyon yoksa normal cevap (Streaming)
            full_ai_response = response_message.content
            yield full_ai_response

        # AI Mesajını kaydet
        if full_ai_response:
            add_chat_message(session_id, "assistant", full_ai_response)

    except Exception as e:
        error_msg = f"Bir hata oluştu: {e}"
        yield error_msg
        print(error_msg)
