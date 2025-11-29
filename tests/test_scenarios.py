import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.openai import generate_ai_response
from unittest.mock import patch, MagicMock

# Mock Data
MOCK_CANCELLED_ORDER = {
    "name": "#1005",
    "financial_status": "refunded",
    "fulfillment_status": "restocked", # Cancelled effectively
    "total_price": "500.00",
    "currency": "TRY",
    "line_items": [{"name": "Mavi Tişört"}],
    "shipping_address": {"address1": "Test Cad.", "city": "Istanbul"}
}

MOCK_UNDERWEAR_ORDER = {
    "name": "#1006",
    "financial_status": "paid",
    "fulfillment_status": "fulfilled",
    "line_items": [{"name": "Pamuklu Boxer Seti"}], # Should trigger policy
    "shipping_address": {"address1": "Test Cad.", "city": "Istanbul"}
}

def test_scenario(name, question, mock_order, expected_keyword):
    print(f"\n--- TEST: {name} ---")
    print(f"Soru: {question}")
    
    # Mocking dependencies
    with patch('src.services.openai.get_store_token') as mock_token, \
         patch('src.services.openai.get_order_by_number') as mock_get_order, \
         patch('src.services.openai.get_shop_info') as mock_shop, \
         patch('src.services.openai.get_chat_history') as mock_history, \
         patch('src.services.openai.add_chat_message') as mock_add_msg:
        
        mock_token.return_value = "fake_token"
        mock_get_order.return_value = mock_order
        mock_shop.return_value = {"address1": "Magaza Adresi"}
        mock_history.return_value = []
        
        # Session data simulating logged in user
        session_data = {'order_id': '1000', 'email': 'test@test.com'}
        
        # Run AI
        generator = generate_ai_response("test_session", "test_shop.myshopify.com", question, session_data)
        
        full_response = ""
        for chunk in generator:
            full_response += chunk
            
        print(f"AI Cevabı: {full_response}")
        
        if expected_keyword.lower() in full_response.lower():
            print(f"✅ BAŞARILI (Beklenen ifade bulundu: '{expected_keyword}')")
        else:
            print(f"❌ BAŞARISIZ (Beklenen ifade YOK: '{expected_keyword}')")

if __name__ == "__main__":
    # Test 1: Cancelled Order Return
    test_scenario(
        "İptal Edilmiş Siparişi İade Etme",
        "Siparişimi iade etmek istiyorum",
        MOCK_CANCELLED_ORDER,
        "iptal" # Expecting "zaten iptal edilmiş" etc.
    )

    # Test 2: Underwear Return
    test_scenario(
        "İç Giyim İadesi",
        "Boxer setini iade edeceğim",
        MOCK_UNDERWEAR_ORDER,
        "iade kabul" # Expecting refusal based on policy
    )

    # Test 3: Discount - Unauthenticated (Should fail/ask for login)
    # Note: We simulate unauthenticated by passing empty session_data in a new test function or modifying the existing one.
    # For simplicity, let's assume the existing test_scenario uses authenticated session.
    # So we test the "Max Limit" and "Success" here.
    
    # Test 4: Discount - High Amount (Should refuse)
    test_scenario(
        "Yüksek İndirim Talebi",
        "Bana yüzde 90 indirim yap",
        MOCK_UNDERWEAR_ORDER, # Order doesn't matter much here, just auth
        "20" # Expecting offer of 20% or refusal of 90
    )
    
    # Test 5: Discount - Success
    test_scenario(
        "Makul İndirim Talebi",
        "Tamam yüzde 20 indirim olsun",
        MOCK_UNDERWEAR_ORDER,
        "oluşturuldu" # Expecting success message from tool
    )
