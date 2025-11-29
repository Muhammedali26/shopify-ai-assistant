from flask import Blueprint, request, redirect, jsonify, render_template, Response, stream_with_context
import requests
from src.config import Config
from src.services.db import save_store_token, get_store_token, get_session, create_or_update_session, get_chat_history
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

@main_bp.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    message = data.get('message')
    shop_url = data.get('shop_url')
    session_id = data.get('session_id')
    
    if not message or not shop_url or not session_id:
        return jsonify({"error": "Missing parameters"}), 400
        
    # Oturum bilgisini çek
    session_data = get_session(session_id)
    
    # Eğer session yoksa oluştur
    if not session_data:
        create_or_update_session(session_id, shop_url)
        session_data = {'session_id': session_id, 'shop_url': shop_url}

    # AI Cevabı (Streaming)
    return Response(
        stream_with_context(generate_ai_response(session_id, shop_url, message, session_data)),
        mimetype='text/plain'
    )

@main_bp.route('/api/chat/history', methods=['GET'])
def api_chat_history():
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
        
    history = get_chat_history(session_id, limit=20)
    return jsonify(history)

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
