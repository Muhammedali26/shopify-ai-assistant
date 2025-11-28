
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
