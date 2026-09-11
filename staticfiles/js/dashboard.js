/* ========== منوی موبایل ========== */
const sidebar = document.getElementById('sidebar');
const overlay = document.getElementById('overlay');
const menuBtn = document.getElementById('menuBtn');
const sidebarClose = document.getElementById('sidebarClose');

function openSidebar(){
  sidebar?.classList.add('open');
  overlay?.classList.add('show');
  document.body.style.overflow = 'hidden';
}
function closeSidebar(){
  sidebar?.classList.remove('open');
  overlay?.classList.remove('show');
  document.body.style.overflow = '';
}

menuBtn?.addEventListener('click', openSidebar);
sidebarClose?.addEventListener('click', closeSidebar);
overlay?.addEventListener('click', closeSidebar);

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeSidebar();
});

/* ========== فیلتر سفارش‌ها ========== */
document.querySelectorAll('.filter').forEach(btn => {
  btn.addEventListener('click', () => {
    const filter = btn.dataset.filter;

    document.querySelectorAll('.filter').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.order-card').forEach(card => {
      if (filter === 'all' || card.dataset.status === filter) {
        card.style.display = '';
      } else {
        card.style.display = 'none';
      }
    });
  });
});

/* ========== توست ========== */
const toastEl = document.getElementById('toast');
let toastTimer;
function toast(msg){
  if (!toastEl) return;
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toastEl.classList.remove('show'), 2600);
}

/* ========== بستن خودکار پیام‌های Django ========== */
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity .5s, transform .5s';
    el.style.opacity = '0';
    el.style.transform = 'translateY(-10px)';
    setTimeout(() => el.remove(), 500);
  }, 4000);
});

/* ========== تأیید خروج ========== */
document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
  if (!confirm('از حساب خود خارج می‌شوید؟')) {
    e.preventDefault();
  }
});

/* ========== عملیات آدرس‌ها ========== */
document.querySelectorAll('.ac-actions .btn-del').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    if (confirm('این آدرس حذف شود؟')) {
      toast('آدرس حذف شد');
      // TODO: درخواست واقعی به سرور
    }
  });
});