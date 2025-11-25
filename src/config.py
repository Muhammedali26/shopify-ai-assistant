import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
    SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
    SHOPIFY_SCOPES = os.getenv("SHOPIFY_SCOPES")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    # Test config
    TEST_SHOP_URL = os.getenv("TEST_SHOP_URL")
    TEST_ACCESS_TOKEN = os.getenv("TEST_ACCESS_TOKEN")

    # Store Policies
    STORE_POLICY_RETURNS = """
    - İade Süresi: Sipariş teslim tarihinden itibaren 30 gün.
    - İade Şartları: Ürün kullanılmamış, etiketi üzerinde ve orijinal ambalajında olmalıdır.
    - İade Kargo Ücreti: Müşteriye aittir (kusurlu ürünler hariç).
    - İade Edilemeyen Ürünler: İç giyim, kişisel bakım ürünleri ve indirimli ürünler.
    """
    
    STORE_POLICY_SHIPPING = """
    - Kargo Firması: Yurtiçi Kargo veya Aras Kargo.
    - Teslimat Süresi: Sipariş onaylandıktan sonra 1-3 iş günü.
    - Kargo Takip: Sipariş kargoya verildiğinde SMS ve E-posta ile takip numarası iletilir.
    - Ücretsiz Kargo: 500 TL ve üzeri siparişlerde kargo ücretsizdir.
    """
