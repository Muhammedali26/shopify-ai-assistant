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
