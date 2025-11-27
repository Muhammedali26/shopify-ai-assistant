let currentShop = '';
let currentOrder = '';
let currentEmail = '';

async function startChat() {
    const shopInput = document.getElementById('shop-url').value;
    const orderInput = document.getElementById('order-input').value;
    const emailInput = document.getElementById('email-input').value;
    const errorDiv = document.getElementById('login-error');
    const btn = document.querySelector('button[onclick="startChat()"]');

    if (!shopInput || !orderInput || !emailInput) {
        errorDiv.textContent = "Lütfen mağaza URL'si, sipariş numarası ve e-posta adresini girin.";
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

    // Loading göster
    const loadingEl = document.getElementById('loading');
    loadingEl.style.display = 'block';

    try {
        const response = await fetch(`/api/chat?shop=${currentShop}&order_id=${currentOrder}&email=${encodeURIComponent(currentEmail)}&question=${encodeURIComponent(message)}`);
        const data = await response.json();

        loadingEl.style.display = 'none';

        if (data.error) {
            addMessage("Hata: " + data.error, 'bot');
        } else {
            addMessage(data.ai_response, 'bot');
        }
    } catch (error) {
        loadingEl.style.display = 'none';
        addMessage("Bir bağlantı hatası oluştu.", 'bot');
        console.error(error);
    }
}

function addMessage(text, sender) {
    const messagesDiv = document.getElementById('messages');
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);

    // Basit markdown benzeri bold desteği
    const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    msgDiv.innerHTML = formattedText;

    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
