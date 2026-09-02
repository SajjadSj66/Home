// جریان ورود: شماره موبایل → کد ۶ رقمی → داشبورد.
// فعلاً چون بک‌اند وصل نشده، کد تایید به‌صورت نمایشی همین‌جا تولید و نشون داده میشه.
// وقتی بک‌اند جنگو آماده شد، کافیه sendCode() و verifyCode() رو به fetch واقعی وصل کنی.

let currentPhone = "";
let demoCode = "";
let countdownTimer = null;
let countdownSeconds = 60;

function toPersianDigits(str) {
  const fa = ["۰", "۱", "۲", "۳", "۴", "۵", "۶", "۷", "۸", "۹"];
  return String(str).replace(/[0-9]/g, d => fa[d]);
}

function generateDemoCode() {
  demoCode = String(Math.floor(100000 + Math.random() * 900000));
  return demoCode;
}

function maskPhone(phone) {
  // 09123456789 -> 0912***6789
  return phone.slice(0, 4) + "***" + phone.slice(-4);
}

function goToStep(stepName) {
  document.querySelectorAll(".auth-step").forEach(s => s.classList.remove("active"));
  document.getElementById(`step-${stepName}`).classList.add("active");
}

function startCountdown() {
  countdownSeconds = 60;
  const resendBtn = document.getElementById("resend-btn");
  const label = document.getElementById("countdown-label");
  resendBtn.disabled = true;
  clearInterval(countdownTimer);

  const tick = () => {
    const m = String(Math.floor(countdownSeconds / 60)).padStart(2, "0");
    const s = String(countdownSeconds % 60).padStart(2, "0");
    label.textContent = toPersianDigits(`${m}:${s}`);
    if (countdownSeconds <= 0) {
      clearInterval(countdownTimer);
      resendBtn.disabled = false;
      label.textContent = "";
      return;
    }
    countdownSeconds--;
  };
  tick();
  countdownTimer = setInterval(tick, 1000);
}

function clearOtpBoxes() {
  document.querySelectorAll(".otp-box").forEach(box => {
    box.value = "";
    box.classList.remove("filled", "error", "success");
  });
}

function getOtpValue() {
  return Array.from(document.querySelectorAll(".otp-box")).map(b => b.value).join("");
}

function sendCode(phone) {
  currentPhone = phone;
  const code = generateDemoCode();

  document.getElementById("phone-display").textContent = maskPhone(phone);
  document.getElementById("demo-code-hint").textContent =
    `کد تایید (نسخه‌ی نمایشی — بعداً با پیامک واقعی جایگزین میشه): ${toPersianDigits(code)}`;

  clearOtpBoxes();
  goToStep("otp");
  startCountdown();
  setTimeout(() => document.querySelector(".otp-box").focus(), 350);
}

function verifyCode() {
  const entered = getOtpValue();
  const boxes = document.querySelectorAll(".otp-box");
  if (entered.length < boxes.length) return;

  if (entered === demoCode) {
    boxes.forEach(b => b.classList.add("success"));
    const fakeToken = "demo-token-" + Date.now();
    saveSession(fakeToken, { phone: currentPhone });
    toast("ورود موفقیت‌آمیز بود ✅");
    setTimeout(() => { window.location.href = "dashboard.html"; }, 550);
  } else {
    boxes.forEach(b => b.classList.add("error"));
    toast("کد وارد شده صحیح نیست، دوباره امتحان کن");
    setTimeout(() => {
      boxes.forEach(b => { b.classList.remove("error"); b.value = ""; });
      boxes[0].focus();
    }, 450);
  }
}

function initOtpBoxes() {
  const boxes = document.querySelectorAll(".otp-box");

  boxes.forEach((box, idx) => {
    box.addEventListener("input", () => {
      box.value = box.value.replace(/[^0-9]/g, "").slice(0, 1);
      box.classList.toggle("filled", !!box.value);
      box.classList.remove("error");
      if (box.value && idx < boxes.length - 1) boxes[idx + 1].focus();
      if (getOtpValue().length === boxes.length) verifyCode();
    });

    box.addEventListener("keydown", e => {
      if (e.key === "Backspace" && !box.value && idx > 0) boxes[idx - 1].focus();
    });

    box.addEventListener("paste", e => {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData("text").replace(/[^0-9]/g, "");
      if (!text) return;
      text.split("").slice(0, boxes.length).forEach((ch, i) => {
        boxes[i].value = ch;
        boxes[i].classList.add("filled");
      });
      const next = Math.min(text.length, boxes.length - 1);
      boxes[next].focus();
      if (getOtpValue().length === boxes.length) verifyCode();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  renderLayout("");
  initOtpBoxes();

  document.getElementById("phone-form").addEventListener("submit", e => {
    e.preventDefault();
    const raw = document.getElementById("phone-input").value.trim();
    const errorBox = document.getElementById("phone-error");
    errorBox.style.display = "none";

    if (!/^9\d{9}$/.test(raw)) {
      errorBox.textContent = "شماره موبایل معتبر نیست — باید ۹ رقم بعد از ۰۹ وارد کنی.";
      errorBox.style.display = "block";
      return;
    }
    sendCode("0" + raw);
  });

  document.getElementById("change-phone-link").addEventListener("click", e => {
    e.preventDefault();
    clearInterval(countdownTimer);
    goToStep("phone");
  });

  document.getElementById("resend-btn").addEventListener("click", () => {
    if (!currentPhone) return;
    sendCode(currentPhone);
    toast("کد جدید ارسال شد");
  });
});
