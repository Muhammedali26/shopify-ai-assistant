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
