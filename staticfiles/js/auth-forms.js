function initLoginForm() {
  const form = document.getElementById("login-form");
  const errorBox = document.getElementById("auth-error");
  const btn = document.getElementById("auth-submit-btn");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.style.display = "none";
    btn.disabled = true;
    btn.textContent = "در حال ورود...";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
      const data = await apiRequest("/auth/login", { method: "POST", body: { email, password } });
      saveSession(data.access_token, data.user ?? null);

      // اگه کاربر با اطلاعات کامل برنگشت، جدا بگیرش
      if (!data.user) {
        try {
          const me = await apiRequest("/auth/me", { auth: true });
          saveSession(data.access_token, me);
        } catch (e) {}
      }

      const params = new URLSearchParams(window.location.search);
      window.location.href = params.get("next") || "index.html";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
    } finally {
      btn.disabled = false;
      btn.textContent = "ورود";
    }
  });
}

function initRegisterForm() {
  const form = document.getElementById("register-form");
  const errorBox = document.getElementById("auth-error");
  const btn = document.getElementById("auth-submit-btn");
  if (!form) return;

  form.addEventListener("submit", async e => {
    e.preventDefault();
    errorBox.style.display = "none";
    btn.disabled = true;
    btn.textContent = "در حال ثبت‌نام...";

    const full_name = document.getElementById("full_name").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const password2 = document.getElementById("password2").value;

    if (password !== password2) {
      errorBox.textContent = "رمز عبور و تکرار آن یکسان نیستند.";
      errorBox.style.display = "block";
      btn.disabled = false;
      btn.textContent = "ثبت‌نام";
      return;
    }

    try {
      await apiRequest("/auth/register", { method: "POST", body: { full_name, email, password } });
      // بعد از ثبت‌نام موفق، مستقیم لاگین کن
      const data = await apiRequest("/auth/login", { method: "POST", body: { email, password } });
      saveSession(data.access_token, { full_name, email });
      window.location.href = "index.html";
    } catch (err) {
      errorBox.textContent = err.message;
      errorBox.style.display = "block";
    } finally {
      btn.disabled = false;
      btn.textContent = "ثبت‌نام";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("");
  initLoginForm();
  initRegisterForm();
});
