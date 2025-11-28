(function () {
    // Konfigürasyon
    const APP_URL = "https://shopify-ai-assistant-fsgo.onrender.com";

    // 1. CSS Stillerini Ekle
    const style = document.createElement('style');
    style.innerHTML = `
        #ai-support-widget-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #2563eb;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            cursor: pointer;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.3s ease;
            font-size: 28px;
        }
        #ai-support-widget-btn:hover {
            transform: scale(1.1);
        }
        #ai-support-iframe-container {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 400px;
            height: 600px;
            max-height: 80vh;
            background: white;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            z-index: 9999;
            display: none;
            overflow: hidden;
        }
        #ai-support-iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        @media (max-width: 480px) {
            #ai-support-iframe-container {
                width: 90%;
                right: 5%;
                bottom: 90px;
            }
        }
    `;
    document.head.appendChild(style);

    // 2. Widget Butonunu Oluştur
    const btn = document.createElement('div');
    btn.id = 'ai-support-widget-btn';
    btn.textContent = '💬';
    document.body.appendChild(btn);

    // 3. Iframe Container Oluştur
    const container = document.createElement('div');
    container.id = 'ai-support-iframe-container';

    const iframe = document.createElement('iframe');
    iframe.id = 'ai-support-iframe';
    // src'yi henüz atama (Lazy Load)

    container.appendChild(iframe);
    document.body.appendChild(container);

    // 4. Tıklama Olayı
    let isOpen = false;
    let isLoaded = false;
    const shopDomain = window.Shopify ? window.Shopify.shop : window.location.hostname;

    btn.addEventListener('click', () => {
        if (!isLoaded) {
            iframe.src = `${APP_URL}?shop=${shopDomain}`;
            isLoaded = true;
        }

        isOpen = !isOpen;
        container.style.display = isOpen ? 'block' : 'none';

        // Buton ikonunu değiştir
        btn.textContent = isOpen ? '✕' : '💬';
    });

    // 5. Mesaj Dinleyici (İçeriden kapatma isteği gelirse)
    window.addEventListener('message', (event) => {
        if (event.data === 'close-chat') {
            isOpen = false;
            container.style.display = 'none';
            btn.textContent = '💬';
        }
    });

})();
