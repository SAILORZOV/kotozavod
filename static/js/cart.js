document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("cart-list");
  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  function render() {
    container.innerHTML = "";

    if (cart.length === 0) {
      container.innerHTML = "<p>Корзина пуста 😿</p>";
      return;
    }

    cart.forEach(cat => {
      const div = document.createElement("div");
      div.className = "cat-item";
      div.innerHTML = `
        <input type="checkbox" ${cat.selected ? "checked" : ""} data-id="${cat.id}">
        <img src="${cat.img}" width="80">
        <span>${cat.name} — ${cat.price}₽</span>
        <button data-id="${cat.id}" class="remove-btn">❌</button>
      `;
      container.appendChild(div);
    });
  }

  container.addEventListener("click", e => {
    if (e.target.classList.contains("remove-btn")) {
      const id = e.target.dataset.id;
      cart = cart.filter(c => c.id !== id);
      localStorage.setItem("cart", JSON.stringify(cart));
      render();
    }
  });

  container.addEventListener("change", e => {
    if (e.target.type === "checkbox") {
      const id = e.target.dataset.id;
      const cat = cart.find(c => c.id === id);
      if (cat) cat.selected = e.target.checked;
      localStorage.setItem("cart", JSON.stringify(cart));
    }
  });

  render();
});
