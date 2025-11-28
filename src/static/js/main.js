let currentShop = '';
let currentOrder = '';
let currentEmail = '';

// Sayfa yüklendiğinde çalışır
document.addEventListener('DOMContentLoaded', () => {
    // URL'den shop parametresini al
    const urlParams = new URLSearchParams(window.location.search);
    const shopParam = urlParams.get('shop');

    if (shopParam) {
        document.getElementById('shopUrl').value = shopParam;
        currentShop = shopParam;
    }

    // Eğer URL'de yoksa, embed.js tarafından postMessage ile gönderilmesini bekle
    if (!currentShop) {
        window.addEventListener('message', (event) => {
            if (event.data && event.data.shop) {
                currentShop = event.data.shop;
                document.getElementById('shopUrl').value = currentShop;
            }
        });
    }

    // Enter tuşu dinleyicisi
    const input = document.getElementById('messageInput');
    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
});

function closeChat() {
    window.parent.postMessage('close-chat', '*');
}

async function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    // Session ID veya Order ID yönetimi (Basitleştirilmiş)
    // Şu anki mimaride session-based çalışıyoruz.
    // Ancak backend hala orderId bekliyor olabilir veya session_id.
    // Önceki refactor'de session_id eklemiştik ama main.js bozulduğu için o kod gitti.
    // Tekrar session mantığını ekliyorum.

    let sessionId = localStorage.getItem('chat_session_id');
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem('chat_session_id', sessionId);
    }

    if (!message) return;

    // Kullanıcı mesajını ekle
    addMessage(message, 'user');
    input.value = '';

    // Typing göster
    const typingId = showTyping();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                shop_url: currentShop,
                session_id: sessionId
            })
        });

        // Typing gizle
        removeTyping(typingId);

        // Streaming yanıtı işle
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiMessageDiv = addMessage('', 'ai'); // Boş mesaj kutusu oluştur
        let fullResponse = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            fullResponse += chunk;
            aiMessageDiv.innerHTML = marked.parse(fullResponse); // Markdown render

            // Scroll aşağı
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // Yanıt bitti
        // saveHistory(message, 'user'); // İsteğe bağlı
        // saveHistory(fullResponse, 'ai');

    } catch (error) {
        console.error('Error:', error);
        removeTyping(typingId);
        addMessage('Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.', 'ai');
    }
}

function addMessage(text, sender) {
    const messagesDiv = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'flex gap-3 ' + (sender === 'user' ? 'flex-row-reverse' : '');

    const avatar = sender === 'ai'
        ? '<div class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold shadow-sm">AI</div>'
        : '<div class="w-8 h-8 rounded-full bg-gray-200 flex-shrink-0 flex items-center justify-center text-gray-600 text-xs font-bold">Siz</div>';

    const bubbleClass = sender === 'ai'
        ? 'bg-white text-gray-700 rounded-tl-none border border-gray-100'
        : 'bg-blue-600 text-white rounded-tr-none';

    // Markdown parse if AI
    const content = sender === 'ai' ? (text ? marked.parse(text) : '') : text;

    div.innerHTML = `
        ${avatar}
        <div class="p-3 rounded-2xl shadow-sm max-w-[85%] text-sm ${bubbleClass}">
            ${content} 
        </div>
    `;

    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return div.querySelector('div.p-3');
}

function showTyping() {
    const messagesDiv = document.getElementById('messages');
    const id = 'typing-' + Date.now();
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex gap-3';
    div.innerHTML = `
        <div class="w-8 h-8 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center text-white text-xs font-bold shadow-sm">AI</div>
        <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm text-gray-500 text-sm border border-gray-100">
            <div class="flex gap-1">
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
            </div>
        </div>
    `;
    messagesDiv.appendChild(div);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    return id;
}

function removeTyping(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
