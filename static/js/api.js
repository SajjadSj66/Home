// یک لایه‌ی نازک روی fetch که همه‌ی درخواست‌ها به FastAPI از اینجا رد میشن.
async function apiRequest(path, { method = "GET", body = null, auth = false } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  let res;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== null ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new Error("اتصال به سرور برقرار نشد. مطمئن شو FastAPI روی " + API_BASE_URL + " در حال اجراست.");
  }

  let data = null;
  const text = await res.text();
  if (text) {
    try { data = JSON.parse(text); } catch (e) { data = text; }
  }

  if (res.status === 401 && auth) {
    // توکن نامعتبر/منقضی شده
    clearSession();
  }

  if (!res.ok) {
    let message = "خطایی رخ داد";
    if (data) {
      if (typeof data.detail === "string") message = data.detail;
      else if (Array.isArray(data.detail)) message = data.detail.map(d => d.msg).join(" — ");
      else if (data.message) message = data.message;
    }
    const error = new Error(message);
    error.status = res.status;
    throw error;
  }

  return data;
}
