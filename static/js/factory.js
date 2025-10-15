const parts = {
  body: 1,
  head: 1,
  paws: 1,
  tail: 1
};

const maxParts = 3;

function changePart(part, direction) {
  parts[part] += direction;
  if (parts[part] < 1) parts[part] = maxParts;
  if (parts[part] > maxParts) parts[part] = 1;

  document.getElementById(part).src = `/static/pics/cat_parts/${part}/${part}${parts[part]}.png`;
}

function resetCat() {
  for (let part in parts) {
    parts[part] = 1;
    document.getElementById(part).src = `/static/pics/cat_parts/${part}/${part}1.png`;
  }
}

function addToCart() {
  let cart = JSON.parse(localStorage.getItem("cart") || "[]");

  if (cart.length >= 10) {
    showToast("Можно добавить не больше 10 котов 😿");
    return;
  }

  const catId = "cat_" + Date.now();
  const imgSrc = document.getElementById("head").src;

  const cat = {
    id: catId,
    name: `Кот №${cart.length + 1}`,
    price: Math.floor(Math.random() * 2000) + 1000,
    img: imgSrc,
    selected: false,
    parts: { ...parts }
  };

  cart.push(cat);
  localStorage.setItem("cart", JSON.stringify(cart));

  //showToast(`${cat.name} добавлен в корзину! 🐱`);
  showToast("🐾 Кот добавлен в корзину!");
}



async function sendRequest() {
  const name = document.getElementById("name").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const email = document.getElementById("email").value.trim();
  const agree = document.getElementById("agree").checked;
  const contact = document.querySelector("input[name='contact']:checked");

  if (!name || !phone || !email || !agree || !contact) {
    document.getElementById("form-message").innerText = "Заполните все поля и дайте согласие!";
    return;
  }

  const data = {
    name,
    phone,
    email,
    contact: contact.value,
    cat: { ...parts }
  };

  const res = await fetch("/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const msg = await res.text();
  document.getElementById("form-message").innerText = msg;
}

document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".add-btn");

  buttons.forEach(btn => {
    btn.addEventListener("click", () => {
      const catDiv = btn.closest(".cat");
      if (!catDiv) return;

      const cat = {
        id: catDiv.dataset.id,
        name: catDiv.dataset.name,
        price: parseInt(catDiv.dataset.price),
        img: catDiv.querySelector("img")?.src || "",
        selected: false
      };

      let cart = JSON.parse(localStorage.getItem("cart") || "[]");

      if (cart.length >= 10) {
        alert("Можно добавить не больше 10 котов 😿");
        return;
      }

      if (cart.some(c => c.id === cat.id)) {
        alert("Этот кот уже в корзине!");
        return;
      }

      cart.push(cat);
      localStorage.setItem("cart", JSON.stringify(cart));
      alert(`${cat.name} добавлен в корзину! 🐱`);
    });
  });
});

function showToast(message) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;

  container.appendChild(toast);

  requestAnimationFrame(() => toast.classList.add("show"));

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function showToast(message) {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 2300);
}
