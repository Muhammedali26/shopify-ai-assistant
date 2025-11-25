from supabase import create_client, Client
from src.config import Config

def get_supabase_client() -> Client:
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_KEY
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in .env")
    return create_client(url, key)

def save_store_token(shop_url, access_token):
    supabase = get_supabase_client()
    try:
        data, error = supabase.table('stores').upsert({
            'shop_url': shop_url,
            'access_token': access_token
        }, on_conflict='shop_url').execute()
        
        # Check for error message in the response if it's not a standard error object
        if error and hasattr(error, 'message'):
             print(f"Database error: {error}")
             return False, error.message
             
        return True, None
    except Exception as e:
        print(f"Exception saving to DB: {e}")
        return False, str(e)

def get_store_token(shop_url):
    supabase = get_supabase_client()
    try:
        response = supabase.table('stores').select('access_token').eq('shop_url', shop_url).execute()
        # Supabase-py v2 returns a response object with 'data' attribute
        if response.data and len(response.data) > 0:
            return response.data[0]['access_token']
        return None
    except Exception as e:
        print(f"Exception fetching from DB: {e}")
        return None
