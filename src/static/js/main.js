let currentShop = '';
let currentOrder = '';
let currentEmail = '';

async function startChat() {
    // URL'den shop parametresini al
    const urlParams = new URLSearchParams(window.location.search);
    const shopFromUrl = urlParams.get('shop');

    // Eğer URL'de yoksa input'tan almaya çalış (fallback)
    const shopInput = shopFromUrl || document.getElementById('shop-url').value;

    const orderInput = document.getElementById('order-input').value;
    const emailInput = document.getElementById('email-input').value;
    const errorDiv = document.getElementById('login-error');
    const btn = document.querySelector('button[onclick="startChat()"]');

    if (!shopInput) {
        errorDiv.textContent = "Mağaza bilgisi bulunamadı.";
        errorDiv.style.display = 'block';
        return;
    }

    if (!orderInput || !emailInput) {
        errorDiv.textContent = "Lütfen sipariş numarası ve e-posta adresini girin.";
        errorDiv.style.display = 'block';
        return;
    }

    // Reset error and show loading state
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
    btn.disabled = true;
    btn.textContent = 'Kontrol Ediliyor...';

    try {
        const response = await fetch(`/api/validate-order?shop=${shopInput}&order_id=${orderInput}&email=${encodeURIComponent(emailInput)}`);
        const data = await response.json();

        if (data.valid) {
            currentShop = shopInput;
            currentOrder = orderInput;
            currentEmail = emailInput;

            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'flex';

            // İlk mesajı kişiselleştir
            const firstMsg = document.querySelector('.message.bot');
            if (data.customer_name) {
                firstMsg.textContent = `Merhaba ${data.customer_name}! Siparişinizle ilgili size nasıl yardımcı olabilirim?`;
            }
        } else {
            errorDiv.textContent = data.error || "Sipariş bulunamadı veya bilgiler eşleşmedi.";
            errorDiv.style.display = 'block';
        }
    } catch (e) {
        errorDiv.textContent = "Bağlantı hatası oluştu.";
        errorDiv.style.display = 'block';
        console.error(e);
    } finally {
        btn.disabled = false;
        btn.textContent = 'Sorgula ve Başla';
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const message = inputField.value.trim();

    if (!message) return;

    // Kullanıcı mesajını ekle
    addMessage(message, 'user');
    inputField.value = '';

    // Bot için boş bir mesaj balonu oluştur (Streaming için)
    const messagesDiv = document.getElementById('messages');
    const botMsgDiv = document.createElement('div');
    botMsgDiv.classList.add('message', 'bot');
    botMsgDiv.innerHTML = '<span class="typing-indicator">...</span>'; // Başlangıçta ... göster
    messagesDiv.appendChild(botMsgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    try {
        const response = await fetch(`/api/chat?shop=${currentShop}&order_id=${currentOrder}&email=${encodeURIComponent(currentEmail)}&question=${encodeURIComponent(message)}`);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let isFirstChunk = true;
        let fullText = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            if (isFirstChunk) {
                botMsgDiv.innerHTML = ''; // ... işaretini sil
                isFirstChunk = false;
            }

            // Markdown benzeri basit formatlama (yeni satırlar için)
            // Not: Streaming sırasında tam markdown parse etmek zordur, basitçe ekliyoruz.
            // Daha gelişmişi için tam metin biriktirip parse edilebilir ama şimdilik basit tutalım.
            const formattedChunk = chunk.replace(/\n/g, '<br>');
            let currentShop = '';
            let currentOrder = '';
            let currentEmail = '';

            async function startChat() {
                // URL'den shop parametresini al
                const urlParams = new URLSearchParams(window.location.search);
                const shopFromUrl = urlParams.get('shop');

                // Eğer URL'de yoksa input'tan almaya çalış (fallback)
                const shopInput = shopFromUrl || document.getElementById('shop-url').value;

                const orderInput = document.getElementById('order-input').value;
                const emailInput = document.getElementById('email-input').value;
                const errorDiv = document.getElementById('login-error');
                const btn = document.querySelector('button[onclick="startChat()"]');

                if (!shopInput) {
                    errorDiv.textContent = "Mağaza bilgisi bulunamadı.";
                    errorDiv.style.display = 'block';
                    return;
                }

                if (!orderInput || !emailInput) {
                    errorDiv.textContent = "Lütfen sipariş numarası ve e-posta adresini girin.";
                    errorDiv.style.display = 'block';
                    return;
                }

                // Reset error and show loading state
                errorDiv.style.display = 'none';
                errorDiv.textContent = '';
                btn.disabled = true;
                btn.textContent = 'Kontrol Ediliyor...';

                try {
                    const response = await fetch(`/api/validate-order?shop=${shopInput}&order_id=${orderInput}&email=${encodeURIComponent(emailInput)}`);
                    const data = await response.json();

                    if (data.valid) {
                        currentShop = shopInput;
                        currentOrder = orderInput;
                        currentEmail = emailInput;

                        document.getElementById('login-screen').style.display = 'none';
                        document.getElementById('chat-screen').style.display = 'flex';

                        // GEÇMİŞİ YÜKLE
                        loadHistory();

                        // Eğer geçmiş boşsa hoşgeldin mesajı göster
                        const messagesDiv = document.getElementById('messages');
                        if (messagesDiv.children.length === 0) {
                            const msgDiv = document.createElement('div');
                            msgDiv.classList.add('message', 'bot');
                            msgDiv.textContent = data.customer_name ? `Merhaba ${data.customer_name}! Siparişinizle ilgili size nasıl yardımcı olabilirim?` : "Merhaba! Size nasıl yardımcı olabilirim?";
                            messagesDiv.appendChild(msgDiv);
                        }

                    } else {
                        errorDiv.textContent = data.error || "Sipariş bulunamadı veya bilgiler eşleşmedi.";
                        errorDiv.style.display = 'block';
                    }
                } catch (e) {
                    errorDiv.textContent = "Bağlantı hatası oluştu.";
                    errorDiv.style.display = 'block';
                    console.error(e);
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Sorgula ve Başla';
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage() {
                const inputField = document.getElementById('user-input');
                const message = inputField.value.trim();

                if (!message) return;

                // Kullanıcı mesajını ekle
                addMessage(message, 'user');
                inputField.value = '';

                // Bot için boş bir mesaj balonu oluştur (Streaming için)
                const messagesDiv = document.getElementById('messages');
                const botMsgDiv = document.createElement('div');
                botMsgDiv.classList.add('message', 'bot');
                botMsgDiv.innerHTML = '<span class="typing-indicator">...</span>'; // Başlangıçta ... göster
                messagesDiv.appendChild(botMsgDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                try {
                    const response = await fetch(`/api/chat?shop=${currentShop}&order_id=${currentOrder}&email=${encodeURIComponent(currentEmail)}&question=${encodeURIComponent(message)}`);

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let isFirstChunk = true;
                    let fullText = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const chunk = decoder.decode(value, { stream: true });

                        if (isFirstChunk) {
                            botMsgDiv.innerHTML = ''; // ... işaretini sil
                            isFirstChunk = false;
                        }

                        // Markdown benzeri basit formatlama (yeni satırlar için)
                        // Not: Streaming sırasında tam markdown parse etmek zordur, basitçe ekliyoruz.
                        // Daha gelişmişi için tam metin biriktirip parse edilebilir ama şimdilik basit tutalım.
                        const formattedChunk = chunk.replace(/\n/g, '<br>');
                        botMsgDiv.innerHTML += formattedChunk;
                        fullText += chunk;

                        // Otomatik kaydır
                        messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    }

                    // Stream bittiğinde geçmişe kaydet
                    saveHistory();

                    // Feedback butonlarını ekle (Sadece bot mesajlarına)
                    addFeedbackButtons(botMsgDiv, fullText);

                } catch (error) {
                    botMsgDiv.textContent = "Bir bağlantı hatası oluştu.";
                    console.error(error);
                }
            }

            function addMessage(text, sender, isHistory = false) {
                const messagesDiv = document.getElementById('messages');
                const msgDiv = document.createElement('div');
                msgDiv.classList.add('message', sender);

                // Basit markdown benzeri bold desteği
                const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
                msgDiv.innerHTML = formattedText;

                messagesDiv.appendChild(msgDiv);
                messagesDiv.scrollTop = messagesDiv.scrollHeight;

                // Eğer geçmişten yüklenmiyorsa ve kullanıcı mesajıysa kaydet
                if (!isHistory && sender === 'user') {
                    saveHistory();
                }

                // Geçmişten yüklenen bot mesajları için de feedback butonu ekle
                if (isHistory && sender === 'bot') {
                    addFeedbackButtons(msgDiv, text);
                }
            }

            function addFeedbackButtons(msgDiv, messageContent) {
                // Eğer zaten buton varsa ekleme
                if (msgDiv.querySelector('.feedback-actions')) return;

                const actionsDiv = document.createElement('div');
                actionsDiv.className = 'feedback-actions';

                const upBtn = document.createElement('button');
                upBtn.className = 'feedback-btn';
                upBtn.innerHTML = '👍';
                upBtn.onclick = () => sendFeedback('up', messageContent, upBtn, downBtn);

                const downBtn = document.createElement('button');
                downBtn.className = 'feedback-btn';
                downBtn.innerHTML = '👎';
                downBtn.onclick = () => sendFeedback('down', messageContent, downBtn, upBtn);

                actionsDiv.appendChild(upBtn);
                actionsDiv.appendChild(downBtn);
                msgDiv.appendChild(actionsDiv);
            }

            async function sendFeedback(rating, message, activeBtn, otherBtn) {
                // UI Güncelle
                activeBtn.classList.add('active');
                otherBtn.classList.remove('active');

                // API'ye gönder
                try {
                    await fetch('/api/feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            shop: currentShop,
                            order_id: currentOrder,
                            rating: rating,
                            message: message
                        })
                    });
                    console.log('Feedback sent:', rating);
                } catch (e) {
                    console.error('Feedback error:', e);
                }
            }

            // --- History Functions ---

            function saveHistory() {
                if (!currentOrder) return;

                const messagesDiv = document.getElementById('messages');
                const messages = [];

                // Mesajları topla (Sadece metin içeriklerini)
                messagesDiv.querySelectorAll('.message').forEach(msg => {
                    // Feedback butonlarını ve typing indicator'ı hariç tut
                    let content = msg.innerHTML;

                    // Temizleme (Feedback butonlarını HTML'den çıkar)
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = content;
                    const feedback = tempDiv.querySelector('.feedback-actions');
                    if (feedback) feedback.remove();

                    // Typing indicator varsa kaydetme
                    if (tempDiv.querySelector('.typing-indicator')) return;

                    // <br> taglerini \n'e çevir (basitçe)
                    let text = tempDiv.innerText.trim();

                    messages.push({
                        text: text,
                        sender: msg.classList.contains('user') ? 'user' : 'bot'
                    });
                });

                const key = `chat_history_${currentShop}_${currentOrder}`;
                localStorage.setItem(key, JSON.stringify(messages));
            }

            function loadHistory() {
                const key = `chat_history_${currentShop}_${currentOrder}`;
                const history = localStorage.getItem(key);

                if (history) {
                    const messages = JSON.parse(history);
                    const messagesDiv = document.getElementById('messages');
                    messagesDiv.innerHTML = ''; // Temizle

                    messages.forEach(msg => {
                        addMessage(msg.text, msg.sender, true);
                    });
                }
            }
