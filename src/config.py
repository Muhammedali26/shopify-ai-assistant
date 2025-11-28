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
    # Store Policies (Concise for Token Optimization)
    STORE_POLICY_RETURNS = """
    - Süre: 30 gün.
    - Şart: Etiketli, orijinal ambalajında.
    - Kargo: Müşteriye ait (kusurlu hariç).
    - İade Yok: İç giyim, kişisel bakım.
    - Adres: {SHOP_ADDRESS}
    - Kargo Firması: Yurtiçi veya Aras Kargo.
    """
    
    STORE_POLICY_SHIPPING = """
    - Firmalar: Yurtiçi, Aras.
    - Süre: 1-3 iş günü.
    - Ücretsiz Kargo: 500 TL üzeri.
    """
