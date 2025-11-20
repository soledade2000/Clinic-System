// frontend/js/login.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("loginForm");
  const msg = document.getElementById("loginMsg");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (msg) msg.textContent = "Entrando...";
    const emailEl = document.getElementById("email");
    const passwordEl = document.getElementById("password");
    const email = emailEl ? emailEl.value : "";
    const password = passwordEl ? passwordEl.value : "";
    try {
      const result = await window.api.apiLogin(email, password);
      if (result && result.user) window.api.setUser(result.user);
      if (result && result.token) window.api.setToken(result.token);
      if (msg) { msg.style.color = "#064e3b"; msg.textContent = "Login bem-sucedido!"; }
      setTimeout(()=> location.href = "dashboard.html", 400);
    } catch (err) {
      console.error(err);
      if (msg) { msg.style.color = "#b91c1c"; msg.textContent = "Erro: " + (err.message || err); }
    }
  });
});
