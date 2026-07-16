// مدیریت نشست کاربر (توکن JWT که از FastAPI میاد) در localStorage
const TOKEN_KEY = "appliance_token";
const USER_KEY = "appliance_user";

function saveSession(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

function isLoggedIn() {
  return !!getToken();
}

function isAdmin() {
  const u = getUser();
  return !!(u && u.is_admin);
}

function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function logout() {
  clearSession();
  window.location.href = "index.html";
}

// اگه صفحه فقط برای کاربر لاگین‌کرده است و لاگین نکرده، بفرستش صفحه ورود
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = `login.html?next=${encodeURIComponent(window.location.pathname.split("/").pop())}`;
  }
}

// اگه صفحه فقط برای ادمینه
function requireAdmin() {
  if (!isLoggedIn() || !isAdmin()) {
    window.location.href = "login.html";
  }
}
