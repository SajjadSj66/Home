function cartItemHTML(item) {
  return `
    <div class="cart-item" data-id="${item.id}">
      <div class="thumb">
        ${item.image_url ? `<img src="${item.image_url}" alt="${item.title}">` : ""}
      </div>
      <div>
        <h3 style="margin:0 0 4px;font-size:.95rem">${item.title}</h3>
        <span class="price">${formatPrice(item.price)}</span>
        <div class="qty-row">
          <div class="stepper">
            <button type="button" data-action="plus">+</button>
            <input type="text" value="${item.qty}" data-role="qty" inputmode="numeric">
            <button type="button" data-action="minus">−</button>
          </div>
          <a href="#" class="remove-link" data-action="remove">حذف</a>
        </div>
      </div>
      <div class="price">${formatPrice(item.price * item.qty)}</div>
    </div>
  `;
}

function renderCartPage() {
  const list = document.getElementById("cart-list");
  const cart = getCart();

  if (!cart.length) {
    list.innerHTML = `<div class="empty-state">سبد خرید شما خالیه. <a href="index.html" style="color:var(--primary)">برو به فروشگاه</a></div>`;
  } else {
    list.innerHTML = cart.map(cartItemHTML).join("");
  }

  document.getElementById("summary-subtotal").textContent = formatPrice(cartTotal());
  document.getElementById("summary-total").textContent = formatPrice(cartTotal());

  const checkoutBtn = document.getElementById("go-checkout-btn");
  checkoutBtn.disabled = cart.length === 0;

  list.querySelectorAll(".cart-item").forEach(row => {
    const id = parseInt(row.dataset.id);
    const qtyInput = row.querySelector('[data-role="qty"]');

    row.querySelector('[data-action="plus"]').addEventListener("click", () => {
      updateCartItemQty(id, (parseInt(qtyInput.value) || 1) + 1);
      renderCartPage();
    });
    row.querySelector('[data-action="minus"]').addEventListener("click", () => {
      updateCartItemQty(id, (parseInt(qtyInput.value) || 1) - 1);
      renderCartPage();
    });
    qtyInput.addEventListener("change", () => {
      updateCartItemQty(id, Math.max(1, parseInt(qtyInput.value) || 1));
      renderCartPage();
    });
    row.querySelector('[data-action="remove"]').addEventListener("click", e => {
      e.preventDefault();
      removeFromCart(id);
      renderCartPage();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("cart");
  renderCartPage();

  document.getElementById("go-checkout-btn").addEventListener("click", () => {
    window.location.href = "checkout.html";
  });
});
