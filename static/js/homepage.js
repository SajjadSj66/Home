(() => {
  "use strict";
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const menuToggle = $("[data-menu-toggle]");
  const mobileNav = $("[data-mobile-navigation]");
  if (menuToggle && mobileNav) {
    menuToggle.addEventListener("click", () => {
      const expanded = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!expanded));
      mobileNav.classList.toggle("open", !expanded);
    });
    mobileNav.addEventListener("click", event => {
      if (event.target.closest("a")) {
        mobileNav.classList.remove("open");
        menuToggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  const toast = $("[data-toast]");
  let toastTimer;
  function notify(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("visible");
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => toast.classList.remove("visible"), 2600);
  }

  const panel = $("[data-wishlist-panel]");
  const list = $("[data-wishlist-items]");
  const empty = $(".wishlist-empty");
  const count = $("[data-wishlist-count]");
  const storageKey = "buyghaseti-wishlist";
  let wishlist = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "[]");
    wishlist = Array.isArray(saved) ? saved : [];
  } catch (_) { wishlist = []; }

  function saveWishlist() {
    try { localStorage.setItem(storageKey, JSON.stringify(wishlist)); } catch (_) {}
    renderWishlist();
  }
  function renderWishlist() {
    if (count) count.textContent = String(wishlist.length);
    if (empty) empty.hidden = wishlist.length > 0;
    if (list) {
      list.innerHTML = "";
      wishlist.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item.title;
        list.appendChild(li);
      });
    }
    $$("[data-wishlist-btn]").forEach(button => {
      const active = wishlist.some(item => item.id === button.dataset.productId);
      button.setAttribute("aria-pressed", String(active));
    });
  }
  document.addEventListener("click", event => {
    const button = event.target.closest("[data-wishlist-btn]");
    if (!button) return;
    const id = button.dataset.productId;
    const title = button.dataset.productTitle || "محصول";
    const existing = wishlist.findIndex(item => item.id === id);
    if (existing >= 0) {
      wishlist.splice(existing, 1);
      notify("از علاقه‌مندی‌ها حذف شد.");
    } else {
      wishlist.push({id, title});
      notify("به فهرست علاقه‌مندی‌ها اضافه شد.");
    }
    saveWishlist();
  });
  const panelToggle = $("[data-wishlist-toggle]");
  const closePanel = $("[data-wishlist-close]");
  if (panelToggle && panel) {
    panelToggle.addEventListener("click", () => {
      const open = !panel.hidden;
      panel.hidden = open;
      panelToggle.setAttribute("aria-expanded", String(!open));
    });
  }
  if (closePanel && panel) closePanel.addEventListener("click", () => {
    panel.hidden = true;
    panelToggle?.setAttribute("aria-expanded", "false");
  });
  renderWishlist();

  const newsletter = $("[data-newsletter-form]");
  if (newsletter) newsletter.addEventListener("submit", event => {
    event.preventDefault();
    notify("فرم نمایشی است؛ برای فعال‌سازی باید به سرویس خبرنامه متصل شود.");
  });
})();