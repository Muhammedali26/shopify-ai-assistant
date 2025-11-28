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

def save_feedback(shop_url, order_id, rating, message_content=None):
    """Kullanıcı geri bildirimini kaydeder."""
    supabase = get_supabase_client()
    try:
        data = {
            'shop_url': shop_url,
            'order_id': str(order_id),
            'rating': rating, # 'up' veya 'down'
            'message_content': message_content
        }
        supabase.table('feedback').insert(data).execute()
        return True, None
    except Exception as e:
        print(f"Exception saving feedback: {e}")
        return False, str(e)

def create_or_update_session(session_id, shop_url, order_id=None, email=None):
    """Sohbet oturumunu oluşturur veya günceller."""
    supabase = get_supabase_client()
    try:
        data = {
            'session_id': session_id,
            'shop_url': shop_url,
            'updated_at': 'now()'
        }
        if order_id:
            data['order_id'] = str(order_id)
        if email:
            data['email'] = email
            
        supabase.table('chat_sessions').upsert(data, on_conflict='session_id').execute()
        return True, None
    except Exception as e:
        print(f"Exception saving session: {e}")
        return False, str(e)

def get_session(session_id):
    """Oturum bilgilerini getirir."""
    supabase = get_supabase_client()
    try:
        response = supabase.table('chat_sessions').select('*').eq('session_id', session_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Exception fetching session: {e}")
        return None

def add_chat_message(session_id, role, content):
    """Sohbet mesajını veritabanına kaydeder."""
    supabase = get_supabase_client()
    try:
        data = {
            'session_id': session_id,
            'role': role,
            'content': content
        }
        supabase.table('chat_messages').insert(data).execute()
        return True, None
    except Exception as e:
        print(f"Exception saving message: {e}")
        return False, str(e)

def get_chat_history(session_id, limit=6):
    """
    Oturumun son N mesajını getirir.
    Limit varsayılan 6 (3 soru - 3 cevap) olarak ayarlandı (Maliyet optimizasyonu).
    """
    supabase = get_supabase_client()
    try:
        # Son mesajları almak için created_at'e göre tersten sırala, sonra tekrar düzelt
        response = supabase.table('chat_messages')\
            .select('role, content')\
            .eq('session_id', session_id)\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
            
        if response.data:
            # Tersten aldığımız için listeyi düzeltelim (Eskiden yeniye)
            return response.data[::-1]
        return []
    except Exception as e:
        print(f"Exception fetching history: {e}")
        return []
