// ===== DATA =====
const products = [
  { id: 1, title: 'قابلمه نچسب ۲۴ سانتی', category: 'قابلمه', price: 450000, image: '🍲' },
  { id: 2, title: 'سرخ‌کن برقی ۳.۵ لیتری', category: 'سرخ‌کن', price: 1200000, image: '🍟' },
  { id: 3, title: 'آبمیوه‌گیری گریپ فروت', category: 'آبمیوه‌گیری', price: 780000, image: '🍊' },
  { id: 4, title: 'اجاق گاز دو شعله', category: 'اجاق', price: 2300000, image: '🔥' },
  { id: 5, title: 'مخلوط‌کن ۱۰۰۰ وات', category: 'مخلوط‌کن', price: 650000, image: '🥤' },
  { id: 6, title: 'توری کباب‌پز استیل', category: 'کباب‌پز', price: 320000, image: '🥩' },
  { id: 7, title: 'کتری برقی ۱.۷ لیتر', category: 'کتری', price: 890000, image: '☕' },
  { id: 8, title: 'ماهی‌تابه گرانیتی', category: 'تابه', price: 560000, image: '🐟' },
  { id: 9, title: 'ساندویچ‌ساز ۷۰۰ وات', category: 'ساندویچ‌ساز', price: 950000, image: '🥪' },
  { id: 10, title: 'دستگاه اسپرسو ساز', category: 'اسپرسو', price: 3400000, image: '☕' },
];

const categories = ['همه', ...new Set(products.map(p => p.category))];

// ===== STATE =====
let activeCategory = 'همه';
let searchQuery = '';
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// ===== DOM REFS =====
const grid = document.getElementById('product-grid');
const searchInput = document.getElementById('search-input');
const categoryStrip = document.getElementById('category-strip');
const cartCountEl = document.querySelector('.cart-count');

// ===== RENDER FUNCTIONS =====
function renderCategories() {
  categoryStrip.innerHTML = categories.map(cat =>
    `<span class="category-tag ${cat === activeCategory ? 'active' : ''}" data-category="${cat}">${cat}</span>`
  ).join('');

  document.querySelectorAll('.category-tag').forEach(el => {
    el.addEventListener('click', () => {
      activeCategory = el.dataset.category;
      renderCategories();
      renderProducts();
    });
  });
}

function renderProducts() {
  const filtered = products.filter(p => {
    const matchCategory = activeCategory === 'همه' || p.category === activeCategory;
    const matchSearch = p.title.includes(searchQuery) || p.category.includes(searchQuery);
    return matchCategory && matchSearch;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; padding:40px; color:#868e96;">هیچ محصولی یافت نشد.</p>`;
    return;
  }

  grid.innerHTML = filtered.map(p => `
    <div class="product-card" data-id="${p.id}">
      <div class="product-image">${p.image}</div>
      <div class="product-info">
        <div class="product-title">${p.title}</div>
        <div class="product-category">${p.category}</div>
        <div class="product-price">${p.price.toLocaleString()} تومان</div>
        <div class="product-actions">
          <button class="btn btn-add" data-id="${p.id}">افزودن به سبد</button>
          <button class="btn btn-detail" data-id="${p.id}">مشاهده</button>
        </div>
      </div>
    </div>
  `).join('');

  // Event listeners for add-to-cart
  document.querySelectorAll('.btn-add').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = parseInt(btn.dataset.id);
      addToCart(id);
      e.stopPropagation();
    });
  });

  // Detail buttons (just alert for demo)
  document.querySelectorAll('.btn-detail').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const id = parseInt(btn.dataset.id);
      const product = products.find(p => p.id === id);
      alert(`🛒 ${product.title}\n💰 ${product.price.toLocaleString()} تومان\nدسته: ${product.category}`);
      e.stopPropagation();
    });
  });
}

// ===== CART =====
function addToCart(productId) {
  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.quantity += 1;
  } else {
    cart.push({ id: productId, quantity: 1 });
  }
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartBadge();
}

function updateCartBadge() {
  const total = cart.reduce((sum, item) => sum + item.quantity, 0);
  if (cartCountEl) cartCountEl.textContent = total;
}

// ===== SEARCH =====
searchInput.addEventListener('input', (e) => {
  searchQuery = e.target.value.trim();
  renderProducts();
});

// ===== HEADER & FOOTER (dynamic) =====
function renderHeader() {
  const header = document.getElementById('site-header');
  header.innerHTML = `
    <div class="container header-inner">
      <div class="logo">خانه<span>لوازم</span></div>
      <ul class="nav-menu">
        <li><a href="#catalog">محصولات</a></li>
        <li><a href="#">تخفیف‌ها</a></li>
        <li><a href="#">تماس با ما</a></li>
      </ul>
      <div class="header-actions">
        <span class="cart-icon">🛒<span class="cart-count">0</span></span>
      </div>
    </div>
  `;
  // re-bind cart badge
  const newCartCount = document.querySelector('.cart-count');
  if (newCartCount) {
    const total = cart.reduce((sum, item) => sum + item.quantity, 0);
    newCartCount.textContent = total;
  }
}

function renderFooter() {
  const footer = document.getElementById('site-footer');
  footer.innerHTML = `
    <div class="container footer-inner">
      <div class="footer-col">
        <h4>خانه لوازم</h4>
        <p>فروشگاه تخصصی لوازم آشپزخانه با بهترین قیمت و ضمانت اصالت</p>
      </div>
      <div class="footer-col">
        <h4>دسترسی سریع</h4>
        <a href="#">محصولات</a><br>
        <a href="#">درباره ما</a><br>
        <a href="#">تماس</a>
      </div>
      <div class="footer-col">
        <h4>تماس</h4>
        <p>تلفن: ۰۲۱-۱۲۳۴۵۶۷۸</p>
        <p>ایمیل: info@khaneh-lavazem.ir</p>
      </div>
    </div>
    <div class="container footer-bottom">
      &copy; ۱۴۰۵ تمامی حقوق محفوظ است.
    </div>
  `;
}

// ===== INIT =====
function init() {
  renderHeader();
  renderFooter();
  renderCategories();
  renderProducts();
  updateCartBadge();
}

document.addEventListener('DOMContentLoaded', init);