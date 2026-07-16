let editingId = null;

async function loadAdminProducts() {
  const tbody = document.getElementById("admin-table-body");
  tbody.innerHTML = `<tr><td colspan="6">در حال بارگذاری...</td></tr>`;
  try {
    const data = await apiRequest("/admin/products", { auth: true });
    const items = data.items ?? data;
    renderAdminTable(items);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6">خطا در دریافت لیست محصولات: ${err.message}</td></tr>`;
  }
}

function renderAdminTable(items) {
  const tbody = document.getElementById("admin-table-body");
  if (!items.length) {
    tbody.innerHTML = `<tr><td colspan="6">هنوز محصولی ثبت نشده.</td></tr>`;
    return;
  }
  tbody.innerHTML = items.map(p => `
    <tr data-id="${p.id}">
      <td>${p.id}</td>
      <td>${p.title}</td>
      <td>${p.category}</td>
      <td>${formatPrice(p.price)}</td>
      <td>${p.in_stock ? "موجود" : "ناموجود"}</td>
      <td class="row-actions">
        <button class="btn ghost sm" data-action="edit">ویرایش</button>
        <button class="btn danger sm" data-action="delete">حذف</button>
      </td>
    </tr>
  `).join("");

  tbody.querySelectorAll("tr").forEach(row => {
    const id = row.dataset.id;
    row.querySelector('[data-action="edit"]').addEventListener("click", () => openProductModal(id, items.find(p => String(p.id) === id)));
    row.querySelector('[data-action="delete"]').addEventListener("click", () => deleteProduct(id));
  });
}

function openProductModal(id, product) {
  editingId = id || null;
  document.getElementById("modal-title").textContent = id ? "ویرایش محصول" : "افزودن محصول";

  document.getElementById("p-title").value = product?.title || "";
  document.getElementById("p-category").value = product?.category || "";
  document.getElementById("p-price").value = product?.price || "";
  document.getElementById("p-image").value = product?.image_url || "";
  document.getElementById("p-instock").checked = product ? !!product.in_stock : true;
  document.getElementById("p-description").value = product?.description || "";

  document.getElementById("product-modal").classList.add("open");
}

function closeProductModal() {
  document.getElementById("product-modal").classList.remove("open");
  editingId = null;
}

async function saveProduct(e) {
  e.preventDefault();
  const payload = {
    title: document.getElementById("p-title").value.trim(),
    category: document.getElementById("p-category").value.trim(),
    price: parseInt(document.getElementById("p-price").value) || 0,
    image_url: document.getElementById("p-image").value.trim(),
    in_stock: document.getElementById("p-instock").checked,
    description: document.getElementById("p-description").value.trim(),
  };

  const errorBox = document.getElementById("modal-error");
  errorBox.style.display = "none";

  try {
    if (editingId) {
      await apiRequest(`/admin/products/${editingId}`, { method: "PUT", body: payload, auth: true });
      toast("محصول ویرایش شد");
    } else {
      await apiRequest("/admin/products", { method: "POST", body: payload, auth: true });
      toast("محصول اضافه شد");
    }
    closeProductModal();
    loadAdminProducts();
  } catch (err) {
    errorBox.textContent = err.message;
    errorBox.style.display = "block";
  }
}

async function deleteProduct(id) {
  if (!confirm("از حذف این محصول مطمئنی؟")) return;
  try {
    await apiRequest(`/admin/products/${id}`, { method: "DELETE", auth: true });
    toast("محصول حذف شد");
    loadAdminProducts();
  } catch (err) {
    toast("خطا در حذف: " + err.message);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("admin");
  requireAdmin();
  loadAdminProducts();

  document.getElementById("add-product-btn").addEventListener("click", () => openProductModal(null, null));
  document.getElementById("close-modal-btn").addEventListener("click", closeProductModal);
  document.getElementById("product-form").addEventListener("submit", saveProduct);
});
