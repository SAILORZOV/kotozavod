document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("cart-list");
  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  function render() {
    container.innerHTML = "";

    if (cart.length === 0) {
      container.innerHTML = "<p>Корзина пуста 😿</p>";
      document.getElementById('send-selected-btn').disabled = true;
      document.getElementById('send-form').style.display = 'none';
      return;
    }

    cart.forEach(cat => {
      const div = document.createElement("div");
      div.className = "cat-item";
      div.innerHTML = `
        <input type="checkbox" ${cat.selected ? "checked" : ""} data-id="${cat.id}" onchange="toggleCatSelection('${cat.id}')">
        <img src="${cat.img}" width="80">
        <div class="cat-info">
          <strong>${cat.name}</strong>
          <span>${cat.price}₽</span>
          <div class="cat-parts">${getCatPartsText(cat)}</div>
        </div>
        <button data-id="${cat.id}" class="remove-btn">❌</button>
      `;
      container.appendChild(div);
    });

    updateSendButton();
  }

  function getCatPartsText(cat) {
    if (cat.parts) {
      return `Тело:${cat.parts.body} Голова:${cat.parts.head} Лапы:${cat.parts.paws} Хвост:${cat.parts.tail}`;
    }
    return "Стандартный кот";
  }

  window.toggleCatSelection = function(catId) {
    const cat = cart.find(c => c.id === catId);
    if (cat) {
      cat.selected = !cat.selected;
      localStorage.setItem("cart", JSON.stringify(cart));
      updateSendButton();
    }
  };

  function updateSendButton() {
    const selectedCount = cart.filter(c => c.selected).length;
    const sendBtn = document.getElementById('send-selected-btn');

    if (selectedCount > 0) {
      sendBtn.disabled = false;
      sendBtn.textContent = `📸 Отправить выбранных котов (${selectedCount})`;
    } else {
      sendBtn.disabled = true;
      sendBtn.textContent = '📸 Отправить выбранных котов';
    }
  }

  window.showSendForm = function() {
    const selectedCount = cart.filter(c => c.selected).length;
    if (selectedCount > 0) {
      document.getElementById('send-form').style.display = 'block';
    }
  };

  window.sendSelectedCats = async function() {
    const userEmail = document.getElementById('user-email').value.trim();
    const comment = document.getElementById('email-comment').value.trim();
    const messageEl = document.getElementById('send-message');

    if (!userEmail) {
      messageEl.innerHTML = "❌ Введите ваш email адрес";
      return;
    }

    const selectedCats = cart.filter(cat => cat.selected);

    if (selectedCats.length === 0) {
      messageEl.innerHTML = "❌ Выберите котов для отправки!";
      return;
    }

    messageEl.innerHTML = "📤 Отправляем котов на почту...";

    try {
      const response = await fetch('/send_cats_email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          comment: comment,
          cats: selectedCats
        })
      });

      const result = await response.json();

      if (response.ok) {
        messageEl.innerHTML = "✅ Коты успешно отправлены на почту! Проверьте ваш email 🐾";
        showToast(`Отправлено ${selectedCats.length} котов на ${userEmail}!`);

        // Очищаем форму
        document.getElementById('user-email').value = '';
        document.getElementById('email-comment').value = '';
        document.getElementById('send-form').style.display = 'none';

        // Снимаем выделение с отправленных котов
        selectedCats.forEach(cat => cat.selected = false);
        localStorage.setItem("cart", JSON.stringify(cart));
        render();
      } else {
        messageEl.innerHTML = "❌ Ошибка при отправке: " + result.error;
        showToast("Ошибка отправки 😿");
      }
    } catch (error) {
      messageEl.innerHTML = "❌ Ошибка сети: " + error.message;
      showToast("Ошибка сети 🌐");
    }
  };

  window.clearCart = function() {
    if (confirm("Очистить всю корзину?")) {
      localStorage.setItem("cart", "[]");
      cart = [];
      render();
      showToast("Корзина очищена 🗑️");
    }
  };

  container.addEventListener("click", e => {
    if (e.target.classList.contains("remove-btn")) {
      const id = e.target.dataset.id;
      cart = cart.filter(c => c.id !== id);
      localStorage.setItem("cart", JSON.stringify(cart));
      render();
      showToast("Кот удален из корзины ❌");
    }
  });

  render();
});

function showToast(message) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("fade-out");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}