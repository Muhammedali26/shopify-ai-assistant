import requests
from src.config import Config

def get_order_by_number(shop_url, access_token, order_number):
    """Shopify'dan belirli bir sipariş numarasını çeker."""
    api_endpoint = f"https://{shop_url}/admin/api/2025-10/orders.json"
    headers = {"X-Shopify-Access-Token": access_token}
    # Shopify'da sipariş numarasına göre arama yapmak için 'name' parametresi kullanılır
    # name=1001 şeklinde arama yapılır.
    params = {"name": order_number, "status": "any"} 
    
    try:
        response = requests.get(api_endpoint, headers=headers, params=params)
        response.raise_for_status()
        orders = response.json().get("orders", [])
        
        # Dönen siparişler içinde tam eşleşme var mı kontrol et
        # Çünkü '1001' araması '10012'yi de getirebilir.
        for order in orders:
            if str(order.get("order_number")) == str(order_number):
                return order
                
        return None
    except Exception as e:
        print(f"Shopify'dan sipariş çekilirken hata oluştu: {e}")
        return None
