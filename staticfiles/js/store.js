// سبد خرید در localStorage نگه‌داری میشه (سمت کاربر مهمان هم کار می‌کنه).
// موقع نهایی کردن خرید (checkout) کل سبد به بک‌اند فرستاده میشه.
const CART_KEY = "appliance_cart";

function getCart() {
  const raw = localStorage.getItem(CART_KEY);
  return raw ? JSON.parse(raw) : [];
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  updateCartBadge();
}

function addToCart(product, qty = 1) {
  const cart = getCart();
  const existing = cart.find(i => i.id === product.id);
  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({
      id: product.id,
      title: product.title,
      price: product.price,
      image_url: product.image_url,
      qty,
    });
  }
  saveCart(cart);
}

function updateCartItemQty(id, qty) {
  let cart = getCart();
  if (qty <= 0) {
    cart = cart.filter(i => i.id !== id);
  } else {
    const item = cart.find(i => i.id === id);
    if (item) item.qty = qty;
  }
  saveCart(cart);
}

function removeFromCart(id) {
  const cart = getCart().filter(i => i.id !== id);
  saveCart(cart);
}

function clearCart() {
  saveCart([]);
}

function cartCount() {
  return getCart().reduce((sum, i) => sum + i.qty, 0);
}

function cartTotal() {
  return getCart().reduce((sum, i) => sum + i.qty * i.price, 0);
}

function updateCartBadge() {
  const badge = document.getElementById("cart-badge");
  if (!badge) return;
  const count = cartCount();
  badge.textContent = count;
  badge.style.display = count > 0 ? "flex" : "none";
}

function formatPrice(value) {
  return new Intl.NumberFormat("fa-IR").format(value) + " تومان";
}
