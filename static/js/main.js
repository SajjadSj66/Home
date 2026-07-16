// --- داده‌ی نمایشی: تا وقتی بک‌اند وصل نشده، صفحه با این داده کار می‌کنه ---
const DEMO_CATEGORIES = [
  { id: "fridge", name: "یخچال و فریزر" },
  { id: "washer", name: "ماشین لباسشویی" },
  { id: "oven", name: "اجاق گاز و فر" },
  { id: "vacuum", name: "جاروبرقی" },
  { id: "micro", name: "مایکروویو" },
];

const DEMO_PRODUCTS = [
  { id: 1, title: "یخچال ساید بای ساید ۲۴ فوت", category: "fridge", price: 48500000, image_url: "", in_stock: true, rating: 4.6 },
  { id: 2, title: "ماشین لباسشویی ۸ کیلویی درب از جلو", category: "washer", price: 21900000, image_url: "", in_stock: true, rating: 4.2 },
  { id: 3, title: "اجاق گاز ۵ شعله فردار", category: "oven", price: 15200000, image_url: "", in_stock: false, rating: 3.8 },
  { id: 4, title: "جاروبرقی رباتیک نقشه‌ساز", category: "vacuum", price: 9800000, image_url: "", in_stock: true, rating: 4.4 },
  { id: 5, title: "مایکروویو توکار ۳۴ لیتری", category: "micro", price: 7300000, image_url: "", in_stock: true, rating: 4.0 },
  { id: 6, title: "فریزر ایستاده ۷ کشو", category: "fridge", price: 26400000, image_url: "", in_stock: true, rating: 3.9 },
];

let usingDemoData = false;
let currentCategory = "";
let currentSearch = "";

function energyRatingHTML(rating) {
  // rating بین 0 تا 5 → درصد موقعیت روی نوار ۷ قسمتی
  const pct = Math.max(4, Math.min(96, (rating / 5) * 100));
  return `
    <div class="energy-rating">
      <div class="track">
        <span></span><span></span><span></span><span></span><span></span><span></span><span></span>
        <div class="marker" style="right:${pct}%"></div>
      </div>
      <span class="label">محبوبیت ${rating.toFixed(1)} / ۵</span>
    </div>
  `;
}

function productCardHTML(p) {
  return `
    <a class="card" href="product.html?id=${p.id}">
      <div class="thumb">
        ${p.image_url ? `<img src="${p.image_url}" alt="${p.title}">` : `<span style="color:var(--muted);font-size:.8rem">بدون تصویر</span>`}
      </div>
      <span class="cat">${categoryLabel(p.category)}</span>
      <h3>${p.title}</h3>
      ${energyRatingHTML(p.rating ?? 4)}
      <div class="bottom">
        <span class="price">${formatPrice(p.price)}</span>
        ${p.in_stock ? "" : `<span class="stock out">ناموجود</span>`}
      </div>
    </a>
  `;
}

let categoriesCache = DEMO_CATEGORIES;
function categoryLabel(id) {
  const c = categoriesCache.find(c => c.id === id);
  return c ? c.name : id;
}

async function loadCategories() {
  const strip = document.getElementById("category-strip");
  try {
    const cats = await apiRequest("/categories");
    categoriesCache = cats;
  } catch (err) {
    categoriesCache = DEMO_CATEGORIES;
    usingDemoData = true;
  }
  strip.innerHTML =
    `<button class="category-chip ${currentCategory === "" ? "active" : ""}" data-cat="">همه</button>` +
    categoriesCache.map(c => `<button class="category-chip ${currentCategory === c.id ? "active" : ""}" data-cat="${c.id}">${c.name}</button>`).join("");

  strip.querySelectorAll(".category-chip").forEach(btn => {
    btn.addEventListener("click", () => {
      currentCategory = btn.dataset.cat;
      loadProducts();
      strip.querySelectorAll(".category-chip").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    });
  });
}

async function loadProducts() {
  const grid = document.getElementById("product-grid");
  grid.innerHTML = `<div class="empty-state">در حال بارگذاری محصولات...</div>`;

  let products;
  try {
    const params = new URLSearchParams();
    if (currentCategory) params.set("category", currentCategory);
    if (currentSearch) params.set("search", currentSearch);
    const data = await apiRequest(`/products?${params.toString()}`);
    products = data.items ?? data; // بسته به اینکه بک‌اند pagination بده یا آرایه‌ی خام
  } catch (err) {
    usingDemoData = true;
    products = DEMO_PRODUCTS.filter(p => {
      const matchCat = !currentCategory || p.category === currentCategory;
      const matchSearch = !currentSearch || p.title.includes(currentSearch);
      return matchCat && matchSearch;
    });
  }

  const demoNote = document.getElementById("demo-note");
  if (demoNote) demoNote.style.display = usingDemoData ? "block" : "none";

  if (!products.length) {
    grid.innerHTML = `<div class="empty-state">محصولی با این مشخصات پیدا نشد.</div>`;
    return;
  }
  grid.innerHTML = products.map(productCardHTML).join("");
}

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("home");
  loadCategories().then(loadProducts);

  const searchInput = document.getElementById("search-input");
  let debounce;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => {
      currentSearch = searchInput.value.trim();
      loadProducts();
    }, 350);
  });
});
