from flask import Blueprint, request, redirect, jsonify, render_template, Response, stream_with_context
import requests
from src.config import Config
from src.services.db import save_store_token, get_store_token
from src.services.shopify import get_order_by_number
from src.services.openai import generate_ai_response

main_bp = Blueprint('main', __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/install")
def install():
    shop_url = request.args.get("shop")
    if not shop_url:
        return "Lütfen dükkan URL'sini belirtin. Örn: http://127.0.0.1:3000/install?shop=kargo-store1.myshopify.com"

    auth_url = (
        f"https://{shop_url}/admin/oauth/authorize?client_id={Config.SHOPIFY_API_KEY}"
        f"&scope={Config.SHOPIFY_SCOPES}&redirect_uri={Config.REDIRECT_URI}"
    )
    return redirect(auth_url)

@main_bp.route("/auth/callback")
def callback():
    code = request.args.get("code")
    shop_url = request.args.get("shop")

    token_url = f"https://{shop_url}/admin/oauth/access_token"
    payload = {
        "client_id": Config.SHOPIFY_API_KEY,
        "client_secret": Config.SHOPIFY_API_SECRET,
        "code": code,
    }
    
    try:
        response = requests.post(token_url, json=payload)
        response_data = response.json()

        if "access_token" in response_data:
            access_token = response_data["access_token"]
            
            success, error_msg = save_store_token(shop_url, access_token)
            
            if success:
                return "Uygulama başarıyla kuruldu ve mağaza bilgileri kaydedildi! Bu pencereyi kapatabilirsiniz."
            else:
                return f"Veritabanı hatası: {error_msg}"
        else:
            return "Access Token alınamadı. Bir hata oluştu."
            
    except Exception as e:
        return f"Beklenmedik bir hata: {e}"

@main_bp.route("/api/chat")
def api_chat():
    shop_url = request.args.get("shop")
    question = request.args.get("question")
    order_number = request.args.get("order_id") 
    email = request.args.get("email") # Email parametresi
    
    if not shop_url or not question or not order_number:
        return jsonify({"error": "Eksik parametreler: shop, question ve order_id gereklidir."}), 400
        
    # 1. Get token from DB
    access_token = get_store_token(shop_url)
    if not access_token:
        if shop_url == Config.TEST_SHOP_URL and Config.TEST_ACCESS_TOKEN:
             access_token = Config.TEST_ACCESS_TOKEN
        else:
            return jsonify({"error": "Mağaza bulunamadı veya yetkisiz."}), 401
            
    # 2. Get specific order (Email verification included if provided)
    # Not: Chat sırasında email zorunlu değilse None geçilebilir ama güvenlik için zorunlu olması iyidir.
    # Şimdilik validate_order'dan geçtiği için burada opsiyonel bırakabiliriz veya zorunlu yapabiliriz.
    # Güvenlik için burada da kontrol etmek en iyisidir.
    order = get_order_by_number(shop_url, access_token, order_number, email)
    
    if not order:
        return jsonify({"error": f"Sipariş bulunamadı veya bilgiler eşleşmedi."}), 404
        
    # 3. Generate AI response (Streaming)
    return Response(stream_with_context(generate_ai_response(order, question)), mimetype='text/plain')

@main_bp.route("/api/validate-order")
def validate_order():
    try:
        shop_url = request.args.get("shop")
        order_number = request.args.get("order_id")
        email = request.args.get("email") # Email parametresi
        
        print(f"Validating order: Shop={shop_url}, Order={order_number}, Email={email}")
        
        if not shop_url or not order_number or not email:
            return jsonify({"valid": False, "error": "Sipariş No ve E-posta gereklidir"}), 400
            
        access_token = get_store_token(shop_url)
        if not access_token:
            if shop_url == Config.TEST_SHOP_URL and Config.TEST_ACCESS_TOKEN:
                 access_token = Config.TEST_ACCESS_TOKEN
            else:
                print("Access token not found")
                return jsonify({"valid": False, "error": "Mağaza yetkisi yok"}), 401
                
        # Email ile doğrulama yap
        order = get_order_by_number(shop_url, access_token, order_number, email)
        
        if order:
            customer = order.get('customer')
            customer_name = customer.get('first_name', 'Müşteri') if customer else 'Müşteri'
            print(f"Order found and verified: {order.get('id')}, Customer: {customer_name}")
            return jsonify({"valid": True, "customer_name": customer_name})
        else:
            print("Order not found or email mismatch")
            return jsonify({"valid": False, "error": "Bilgiler eşleşmedi. Lütfen kontrol edin."})
            
    except Exception as e:
        print(f"Error in validate_order: {e}")
        return jsonify({"valid": False, "error": "Sunucu hatası"}), 500

@main_bp.route("/api/feedback", methods=["POST"])
def api_feedback():
    try:
        data = request.json
        shop_url = data.get("shop")
        order_id = data.get("order_id")
        rating = data.get("rating")
        message = data.get("message")
        
        if not shop_url or not rating:
            return jsonify({"error": "Eksik parametreler"}), 400
            
        from src.services.db import save_feedback
        success, error = save_feedback(shop_url, order_id, rating, message)
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": error}), 500
            
    except Exception as e:
        print(f"Feedback error: {e}")
        return jsonify({"error": str(e)}), 500
