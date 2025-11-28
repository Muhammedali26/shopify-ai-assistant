import requests
from src.config import Config

def get_order_by_number(shop_url, access_token, order_number, email=None):
    """
    Shopify API üzerinden sipariş numarasına (name) göre siparişi bulur.
    Opsiyonel olarak e-posta doğrulaması yapar.
    """
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    # Sipariş numarasına göre filtrele (name=1001)
    url = f"https://{shop_url}/admin/api/2023-10/orders.json?name={order_number}&status=any"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            orders = response.json().get("orders", [])
            # Tam eşleşme kontrolü (API bazen kısmi eşleşme döndürebilir)
            for order in orders:
                if str(order.get("order_number")) == str(order_number) or order.get("name") == str(order_number) or order.get("name") == f"#{order_number}":
                    
                    # E-posta doğrulaması (Eğer email parametresi geldiyse)
                    if email:
                        order_email = order.get("email", "").lower()
                        customer_email = order.get("customer", {}).get("email", "").lower()
                        input_email = email.lower().strip()
                        
                        if input_email != order_email and input_email != customer_email:
                            print(f"Email mismatch! Order: {order_email}/{customer_email}, Input: {input_email}")
                            return None # E-posta eşleşmedi
                            
                    return order
            return None
        else:
            print(f"Shopify API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception in get_order_by_number: {e}")
        return None

def cancel_order(shop_url, access_token, order_id):
    """Shopify API üzerinden siparişi iptal eder."""
    url = f"https://{shop_url}/admin/api/2023-10/orders/{order_id}/cancel.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={})
        if response.status_code == 200:
            return {"success": True, "message": "Sipariş başarıyla iptal edildi."}
        else:
            return {"success": False, "message": f"Hata: {response.text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def check_product_stock(shop_url, access_token, product_name):
    """Ürün ismine göre stok kontrolü yapar."""
    url = f"https://{shop_url}/admin/api/2023-10/products.json?title={product_name}"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            products = response.json().get("products", [])
            if not products:
                return "Üzgünüm, bu isimde bir ürün bulamadım."
            
            stock_info = []
            for product in products:
                for variant in product['variants']:
                    stock_info.append(f"{product['title']} ({variant['title']}): {variant['inventory_quantity']} adet")
            
            return "\n".join(stock_info)
        else:
            return "Stok bilgisi alınamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

def update_shipping_address(shop_url, access_token, order_id, address_data):
    """Siparişin teslimat adresini günceller."""
    url = f"https://{shop_url}/admin/api/2023-10/orders/{order_id}.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "order": {
            "id": order_id,
            "shipping_address": address_data
        }
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 200:
            return {"success": True, "message": "Adres başarıyla güncellendi."}
        else:
            return {"success": False, "message": f"Hata: {response.text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def add_order_note(shop_url, access_token, order_id, note):
    """Siparişe not ekler."""
    # Önce mevcut notu almamız lazım ki üzerine ekleyelim, yoksa silinir.
    # Ancak basitlik için direkt note alanını güncelliyoruz.
    # Daha gelişmiş versiyonda: get_order -> current_note -> new_note = current + note
    
    url = f"https://{shop_url}/admin/api/2023-10/orders/{order_id}.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "order": {
            "id": order_id,
            "note": note
        }
    }
    
    try:
        response = requests.put(url, headers=headers, json=payload)
        if response.status_code == 200:
            return {"success": True, "message": "Not başarıyla eklendi."}
        else:
            return {"success": False, "message": f"Hata: {response.text}"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def create_discount_code(shop_url, access_token, code, amount, type="fixed_amount"):
    """
    İndirim kodu oluşturur.
    type: 'fixed_amount' (TL) veya 'percentage' (%)
    """
    # 1. Price Rule Oluştur
    rule_url = f"https://{shop_url}/admin/api/2023-10/price_rules.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    value_type = "fixed_amount" if type == "fixed_amount" else "percentage"
    target_type = "line_item"
    allocation_method = "across"
    
    # Negatif değer olmalı (indirim olduğu için)
    value = f"-{amount}"
    
    rule_payload = {
        "price_rule": {
            "title": f"AI Generated - {code}",
            "target_type": target_type,
            "target_selection": "all",
            "allocation_method": allocation_method,
            "value_type": value_type,
            "value": value,
            "customer_selection": "all",
            "starts_at": "2023-11-01T00:00:00Z" # Geçmiş tarih verelim ki hemen başlasın
        }
    }
    
    try:
        rule_response = requests.post(rule_url, headers=headers, json=rule_payload)
        if rule_response.status_code != 201:
            return {"success": False, "message": f"Kural oluşturulamadı: {rule_response.text}"}
            
        price_rule_id = rule_response.json()['price_rule']['id']
        
        # 2. Discount Code Oluştur
        code_url = f"https://{shop_url}/admin/api/2023-10/price_rules/{price_rule_id}/discount_codes.json"
        code_payload = {
            "discount_code": {
                "code": code
            }
        }
        
        code_response = requests.post(code_url, headers=headers, json=code_payload)
        if code_response.status_code == 201:
            return {"success": True, "message": f"İndirim kodu oluşturuldu: {code}"}
        else:
            return {"success": False, "message": f"Kod oluşturulamadı: {code_response.text}"}
            
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_shop_info(shop_url, access_token):
    """Mağaza bilgilerini (adres, isim vb.) getirir."""
    url = f"https://{shop_url}/admin/api/2023-10/shop.json"
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            shop = response.json().get("shop", {})
            return {
                "name": shop.get("name"),
                "email": shop.get("email"),
                "address1": shop.get("address1"),
                "city": shop.get("city"),
                "zip": shop.get("zip"),
                "country": shop.get("country"),
                "phone": shop.get("phone")
            }
        return None
    except Exception as e:
        print(f"Error fetching shop info: {e}")
        return None
