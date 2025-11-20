// frontend/js/commons.js
// common.js - utilitários e comportamento comum a todas as páginas
document.addEventListener("DOMContentLoaded", () => {
  // logout
  const logoutBtn = document.getElementById("logoutIcon");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", (e) => {
      e.preventDefault();
      if (window.api) window.api.logout();
    });
  }

  // preenche userInfo se houver
  (async () => {
    const userEls = document.querySelectorAll("#userInfo");
    const stored = (window.api && window.api.getUser) ? window.api.getUser() : null;

    if (!stored && window.api && window.api.getToken && window.api.getToken()) {
      try {
        const me = await window.api.apiGetMe();
        window.api.setUser(me);
        userEls.forEach(el => { if (el) el.innerText = me.nome || me.email || "Usuário"; });
      } catch {
        userEls.forEach(el => { if (el) el.innerText = "Usuário"; });
      }
    } else {
      userEls.forEach(el => { if (el) el.innerText = stored ? (stored.nome || stored.email) : "Usuário"; });
    }

    // role-based elements
    document.querySelectorAll("[data-roles]").forEach(el => {
      try {
        const attr = el.getAttribute("data-roles");
        const allowed = attr ? attr.split(",").map(s=>s.trim()) : [];
        if (!allowed.includes(window.api.getCargo())) el.style.display = "none";
      } catch (e) {}
    });
  })();

  // highlight automático do menu lateral
  try {
    const links = document.querySelectorAll(".sidebar nav a");
    const cur = location.pathname.split("/").pop() || "dashboard.html";
    links.forEach(l => {
      const href = l.getAttribute("href");
      if (!href) return;
      if (href === cur) l.classList.add("active");
      else l.classList.remove("active");
    });
  } catch (e) {}
});
