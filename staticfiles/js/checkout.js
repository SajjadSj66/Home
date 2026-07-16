document.addEventListener("DOMContentLoaded", () => {
  renderLayout("cart");
  requireAuth();

  const cart = getCart();
  if (!cart.length) {
    window.location.href = "cart.html";
    return;
  }

  document.getElementById("checkout-total").textContent = formatPrice(cartTotal());

  const form = document.getElementById("checkout-form");
  const errorBox = document.getElementById("checkout-error");
  const submitBtn = document.getElementById("submit-order-btn");

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.style.display = "none";
    submitBtn.disabled = true;
    submitBtn.textContent = "در حال ثبت سفارش...";

    const payload = {
      address: document.getElementById("address").value.trim(),
      phone: document.getElementById("phone").value.trim(),
      items: getCart().map(i => ({ product_id: i.id, quantity: i.qty })),
    };

    try {
      const order = await apiRequest("/orders", { method: "POST", body: payload, auth: true });
      clearCart();
      document.getElementById("checkout-form-wrap").style.display = "none";
      document.getElementById("checkout-success").style.display = "block";
      document.getElementById("order-id").textContent = order.id ?? "—";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "ثبت نهایی سفارش";
    }
  });
});
