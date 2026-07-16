// هدر و فوتر مشترک همه‌ی صفحات از اینجا رندر میشه، تا مجبور نباشیم
// در هر فایل HTML جدا نگه‌داریش کنیم.
function renderLayout(activePage) {
  const header = document.getElementById("site-header");
  const footer = document.getElementById("site-footer");

  const loggedIn = isLoggedIn();
  const admin = isAdmin();
  const user = getUser();

  const navItem = (href, label, key) =>
    `<a href="${href}" class="${activePage === key ? "active" : ""}">${label}</a>`;

  if (header) {
    header.innerHTML = `
      <div class="container bar">
        <a href="index.html" class="brand">
          <span class="mark">خ.ل</span>
          خانه لوازم
        </a>
        <nav class="nav-links">
          ${navItem("index.html", "محصولات", "home")}
          ${navItem("cart.html", "سبد خرید", "cart")}
          ${admin ? navItem("admin.html", "پنل ادمین", "admin") : ""}
        </nav>
        <div class="header-actions">
          ${
            loggedIn
              ? `<span style="font-size:.85rem;color:var(--muted)">سلام، ${user?.full_name || "کاربر"}</span>
                 <button class="btn ghost sm" onclick="logout()">خروج</button>`
              : `<a class="btn ghost sm" href="login.html">ورود</a>`
          }
          <a href="cart.html" class="icon-btn" aria-label="سبد خرید">
            🛒<span id="cart-badge" class="badge" style="display:none">0</span>
          </a>
        </div>
      </div>
    `;
  }

  if (footer) {
    footer.innerHTML = `
      <div class="container">
        © ${new Date().getFullYear()} خانه لوازم — فروشگاه لوازم خانگی
      </div>
    `;
  }

  updateCartBadge();
}

function toast(message) {
  let el = document.getElementById("toast");
  if (!el) {
    el = document.createElement("div");
    el.id = "toast";
    document.body.appendChild(el);
  }
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(el._timer);
  el._timer = setTimeout(() => el.classList.remove("show"), 2200);
}
