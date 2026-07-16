function getProductIdFromURL() {
  const params = new URLSearchParams(window.location.search);
  return params.get("id");
}

async function loadProduct() {
  const id = getProductIdFromURL();
  const wrap = document.getElementById("product-view");
  if (!id) {
    wrap.innerHTML = `<div class="empty-state">محصولی مشخص نشده.</div>`;
    return;
  }

  let p;
  try {
    p = await apiRequest(`/products/${id}`);
  } catch (err) {
    p = DEMO_PRODUCTS_FULL.find(d => String(d.id) === String(id));
    if (p) toast("داده نمایشی نمایش داده می‌شود — بک‌اند وصل نیست");
  }

  if (!p) {
    wrap.innerHTML = `<div class="empty-state">این محصول پیدا نشد.</div>`;
    return;
  }

  document.title = `${p.title} — خانه لوازم`;

  const specsRows = Object.entries(p.specs || {})
    .map(([k, v]) => `<div class="row"><span>${k}</span><b>${v}</b></div>`)
    .join("");

  wrap.innerHTML = `
    <div class="product-gallery">
      <div class="thumb">
        ${p.image_url ? `<img src="${p.image_url}" alt="${p.title}">` : `<span style="color:var(--muted)">بدون تصویر</span>`}
      </div>
    </div>
    <div class="product-info">
      <span class="cat">${p.category}</span>
      <h1>${p.title}</h1>
      <div style="margin:10px 0">
        <div class="energy-rating" style="max-width:220px">
          <div class="track">
            <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
            <div class="marker" style="right:${Math.max(4, Math.min(96, ((p.rating ?? 4)/5)*100))}%"></div>
          </div>
          <span class="label">محبوبیت ${(p.rating ?? 4).toFixed(1)} / ۵</span>
        </div>
      </div>
      <div class="price-row">
        <span class="price">${formatPrice(p.price)}</span>
        <span class="stock ${p.in_stock ? "in" : "out"}">${p.in_stock ? "موجود در انبار" : "ناموجود"}</span>
      </div>

      <div class="qty-row">
        <span>تعداد:</span>
        <div class="stepper">
          <button id="qty-plus" type="button">+</button>
          <input id="qty-input" type="text" value="1" inputmode="numeric">
          <button id="qty-minus" type="button">−</button>
        </div>
      </div>

      <div class="product-actions">
        <button class="btn primary" id="add-to-cart-btn" ${p.in_stock ? "" : "disabled"}>افزودن به سبد خرید</button>
        <a class="btn ghost" href="cart.html">مشاهده‌ی سبد خرید</a>
      </div>

      ${p.description ? `<div class="desc-block">${p.description}</div>` : ""}
      ${specsRows ? `<div class="spec-sheet" style="margin-top:20px">${specsRows}</div>` : ""}
    </div>
  `;

  document.getElementById("qty-plus").addEventListener("click", () => stepQty(1));
  document.getElementById("qty-minus").addEventListener("click", () => stepQty(-1));
  document.getElementById("add-to-cart-btn").addEventListener("click", () => {
    const qty = parseInt(document.getElementById("qty-input").value) || 1;
    addToCart(p, qty);
    toast("به سبد خرید اضافه شد");
  });
}

function stepQty(delta) {
  const input = document.getElementById("qty-input");
  const val = Math.max(1, (parseInt(input.value) || 1) + delta);
  input.value = val;
}

// نمونه‌ی داده‌ی کامل‌تر برای حالت نمایشی (وقتی بک‌اند وصل نیست)
const DEMO_PRODUCTS_FULL = [
  {
    id: 1, title: "یخچال ساید بای ساید ۲۴ فوت", category: "fridge", price: 48500000,
    image_url: "", in_stock: true, rating: 4.6,
    description: "یخچال فریزر ساید بای ساید با سیستم نوفراست تمام، دیسپنسر آب و یخ و طراحی مدرن.",
    specs: { "ظرفیت": "۲۴ فوت", "رنگ": "استیل", "نوع سرمایش": "نوفراست", "گارانتی": "۱۸ ماهه" },
  },
  {
    id: 2, title: "ماشین لباسشویی ۸ کیلویی درب از جلو", category: "washer", price: 21900000,
    image_url: "", in_stock: true, rating: 4.2,
    description: "ماشین لباسشویی با موتور اینورتر، ۱۴ برنامه شستشو و مصرف انرژی رده A.",
    specs: { "ظرفیت": "۸ کیلوگرم", "کلاس انرژی": "A", "دور آبگیری": "۱۲۰۰" },
  },
];

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("home");
  loadProduct();
});
