from supabase import create_client, Client
from src.config import Config

def get_supabase_client() -> Client:
    """Supabase client'ı döndürür."""
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_KEY
    
    if not url or not key:
        raise ValueError("SUPABASE_URL ve SUPABASE_KEY environment variables gerekli")
    
    # URL validation
    if not url.startswith('https://'):
        raise ValueError(f"Invalid SUPABASE_URL format: {url}. HTTPS ile başlamalı.")
    
    try:
        return create_client(url, key)
    except Exception as e:
        raise ValueError(f"Supabase client oluşturulamadı: {str(e)}")

def save_store_token(shop_url, access_token):
    """Shopify store'un access token'ını Supabase'e kaydeder."""
    supabase = get_supabase_client()
    try:
        data, error = supabase.table('stores').upsert({
            'shop_url': shop_url,
            'access_token': access_token
        }, on_conflict='shop_url').execute()
        
        if error and hasattr(error, 'message'):
            print(f"Database error: {error}")
            return False, error.message
             
        return True, None
    except Exception as e:
        print(f"Exception saving to DB: {e}")
        return False, str(e)

def get_store_token(shop_url):
    """Shopify store'un access token'ını Supabase'den getirir."""
    supabase = get_supabase_client()
    try:
        response = supabase.table('stores').select('access_token').eq('shop_url', shop_url).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['access_token']
        return None
    except Exception as e:
        print(f"Exception fetching from DB: {e}")
        return None
