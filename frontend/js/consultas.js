// frontend/js/consultas.js
document.addEventListener("DOMContentLoaded", async () => {
  if (!window.api?.getToken()) return window.location.href = "login.html";

  const pacienteSelect = document.getElementById("pacienteSelect");
  const usuarioSelect = document.getElementById("usuarioSelect");
  const consultasTable = document.getElementById("consultasTable");
  const msg = document.getElementById("msg");
  const consultaForm = document.getElementById("consultaForm");

  try {
    const pacientes = await window.api.apiGetPacientes(0, 500);
    if (pacienteSelect) {
      pacienteSelect.innerHTML = (Array.isArray(pacientes) ? pacientes : []).map(
        p => `<option value="${p.id}">${p.nome_completo || p.nome}</option>`
      ).join("");
    }
  } catch (err) {
    console.error("Erro ao carregar pacientes", err);
    if (pacienteSelect) pacienteSelect.innerHTML = "<option value=''>Erro ao carregar</option>";
  }

  if (window.api?.hasRole && window.api.hasRole("ADMIN", "SECRETARIA")) {
    try {
      const usuarios = await window.api.apiListUsuarios();
      if (usuarioSelect) {
        usuarioSelect.style.display = "inline-block";
        usuarioSelect.innerHTML = (Array.isArray(usuarios) ? usuarios : []).map(
          u => `<option value="${u.id}">${u.nome || u.nome_completo || u.email} (${u.cargo || ""})</option>`
        ).join("");
      }
    } catch (err) {
      console.error("Erro ao carregar usuarios", err);
    }
  }

  async function carregarConsultas() {
    try {
      const consultas = await window.api.apiGetConsultas(0, 200);
      if (!consultasTable) return;
      const tbody = consultasTable.querySelector("tbody");
      if (!consultas || consultas.length === 0) {
        if (tbody) tbody.innerHTML = `<tr><td colspan="4">Nenhuma consulta encontrada.</td></tr>`;
        return;
      }
      if (tbody) {
        tbody.innerHTML = consultas.map(c => {
          const pacNome = c.paciente_nome || c.paciente?.nome_completo || c.paciente?.nome || "-";
          const usuarioNome = c.usuario_nome || c.usuario?.nome || "-";
          const dt = c.data_hora ? new Date(c.data_hora) : null;
          const dateStr = dt ? dt.toLocaleDateString() : "-";
          const timeStr = dt ? dt.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}) : "-";
          return `<tr>
            <td>${pacNome}</td>
            <td>${dateStr} ${timeStr}</td>
            <td>${usuarioNome}</td>
            <td>${c.status || "-"}</td>
          </tr>`;
        }).join("");
      }
    } catch (err) {
      console.error("Erro ao carregar consultas:", err);
      if (consultasTable) {
        const tbody = consultasTable.querySelector("tbody");
        if (tbody) tbody.innerHTML = `<tr><td colspan="4">Erro ao carregar consultas</td></tr>`;
      }
    }
  }

  await carregarConsultas();

  if (consultaForm) {
    consultaForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (msg) msg.textContent = "Agendando...";
      const pacienteVal = pacienteSelect ? pacienteSelect.value : null;
      if (!pacienteVal) {
        if (msg) msg.textContent = "Selecione um paciente.";
        return;
      }
      const payload = {
        paciente_id: parseInt(pacienteVal),
        data_hora: (document.getElementById("data_hora") || {}).value
      };
      if (usuarioSelect && usuarioSelect.value) payload.usuario_id = parseInt(usuarioSelect.value);
      try {
        await window.api.apiCreateConsulta(payload);
        if (msg) msg.textContent = "Consulta criada!";
        await carregarConsultas();
        consultaForm.reset();
      } catch (err) {
        console.error("Erro ao criar consulta:", err);
        if (msg) msg.textContent = `Erro: ${err.message || err}`;
      }
    });
  }

  try {
    const token = window.api.getToken();
    if (token) {
      const proto = location.protocol === "https:" ? "wss" : "ws";
      const port = location.port || "8000";
      const ws = new WebSocket(`${proto}://${location.hostname}:${port}/ws/consultas?token=${token}`);
      ws.onmessage = (ev) => { console.log("WS:", ev.data); carregarConsultas(); };
      ws.onopen = () => console.log("WS conectado");
      ws.onerror = (e) => console.log("WS erro", e);
    }
  } catch (e) {
    console.log("WS não iniciado", e);
  }
});
