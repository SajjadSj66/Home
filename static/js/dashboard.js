// داده‌ی نمایشی سفارش‌ها — تا وقتی به API واقعی جنگو (GET /shop/orders/) وصل بشه
const DEMO_ORDERS = [
  { id: 1042, date: "۱۴۰۳/۰۴/۲۸", status: "delivered", total: 15800000, items: "سرخ‌کن بدون روغن، قهوه‌ساز اسپرسو" },
  { id: 1038, date: "۱۴۰۳/۰۴/۲۰", status: "shipped", total: 9200000, items: "ربات آشپزخانه چندکاره" },
  { id: 1025, date: "۱۴۰۳/۰۴/۰۵", status: "processing", total: 32500000, items: "ماشین ظرفشویی ۱۴ نفره" },
  { id: 1004, date: "۱۴۰۳/۰۳/۱۸", status: "cancelled", total: 3400000, items: "آبمیوه‌گیری استوانه‌ای" },
];

const STATUS_LABELS = {
  processing: "در حال پردازش",
  shipped: "ارسال شده",
  delivered: "تحویل شده",
  cancelled: "لغو شده",
};

function statusPillHTML(status) {
  return `<span class="status-pill ${status}">${STATUS_LABELS[status] || status}</span>`;
}

function orderCardHTML(order) {
  return `
    <div class="order-card">
      <div>
        <div style="font-weight:600">سفارش #${order.id}</div>
        <div class="order-meta">${order.date} — ${order.items}</div>
      </div>
      <div style="display:flex;align-items:center;gap:14px">
        <span class="price">${formatPrice(order.total)}</span>
        ${statusPillHTML(order.status)}
      </div>
    </div>
  `;
}

function renderOrders() {
  const list = document.getElementById("orders-list");
  if (!DEMO_ORDERS.length) {
    list.innerHTML = `<div class="empty-state">هنوز سفارشی ثبت نکردی. <a href="index.html" style="color:var(--primary)">برو به فروشگاه</a></div>`;
    return;
  }
  list.innerHTML = DEMO_ORDERS.map(orderCardHTML).join("");
}

function renderStats() {
  document.getElementById("stat-orders").textContent = DEMO_ORDERS.length;
  document.getElementById("stat-total").textContent = formatPrice(DEMO_ORDERS.reduce((s, o) => s + o.total, 0));
  document.getElementById("stat-processing").textContent = DEMO_ORDERS.filter(o => o.status === "processing").length;
}

function renderGreeting(phone) {
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "صبح بخیر ☀️" : hour < 18 ? "ظهر بخیر 🌤" : "شب بخیر 🌙";
  document.getElementById("greeting-line").textContent = `${greeting}`;
  document.getElementById("dash-phone").textContent = phone || "—";
  document.getElementById("dash-avatar").textContent = phone ? phone.slice(-2) : "کا";
}

document.addEventListener("DOMContentLoaded", () => {
  if (!isLoggedIn()) {
    window.location.href = "login.html";
    return;
  }
  renderLayout("dashboard");

  const user = getUser();
  renderGreeting(user?.phone);
  renderStats();
  renderOrders();

  document.getElementById("logout-btn").addEventListener("click", logout);
});
