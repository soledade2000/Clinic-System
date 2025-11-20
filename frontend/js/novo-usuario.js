// frontend/js/novo-usuario.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("usuarioForm");
  const msg = document.getElementById("msgUsuario");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      nome: (document.getElementById("nome") || {}).value,
      email: (document.getElementById("email") || {}).value,
      senha: (document.getElementById("senha") || {}).value,
      cargo: (document.getElementById("cargo") || {}).value
    };
    try {
      await window.api.apiCreateUsuario(payload);
      if (msg) { msg.style.color = "#064e3b"; msg.textContent = "Usuário criado!"; }
      setTimeout(()=> location.href = "dashboard.html", 600);
    } catch (err) {
      console.error(err);
      if (msg) { msg.style.color = "#b91c1c"; msg.textContent = "Erro: " + (err.message || err); }
    }
  });
});
