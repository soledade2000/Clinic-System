// frontend/js/dashboard.js
document.addEventListener("DOMContentLoaded", async () => {
  if (!window.api?.getToken()) return window.location.href = "login.html";

  try {
    const data = await window.api.apiGetDashboard();
    const elTotalPacientes = document.getElementById("totalPacientes");
    const elAtivos = document.getElementById("ativos");
    const elInativos = document.getElementById("inativos");
    const elPacientesAgendados = document.getElementById("pacientesAgendados");
    const tbody = document.querySelector("#tabela-consultas tbody");

    if (elTotalPacientes) elTotalPacientes.innerText = data?.total_pacientes ?? 0;
    if (elPacientesAgendados) elPacientesAgendados.innerText = (data?.proximos_agendamentos || []).length ?? 0;

    const proximas = data?.proximos_agendamentos || [];
    if (tbody) {
      if (proximas.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5">Nenhuma consulta agendada.</td></tr>`;
      } else {
        tbody.innerHTML = proximas.map(c => {
          const dt = c.data_hora ? new Date(c.data_hora) : null;
          const dateStr = dt ? dt.toLocaleDateString() : "-";
          const timeStr = dt ? dt.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'}) : "-";
          const serv = c.paciente_servico || c.servico || "-";
          const status = c.status || "Agendado";
          const statusClass = (status.toLowerCase().includes("cancel") || status.toLowerCase().includes("inativo"))
            ? "status inativo"
            : "status ativo";
          const nome = c.paciente_nome || "-";
          const initials = nome.split(" ").map(s => s[0]).slice(0, 2).join("");
          return `<tr>
            <td>
              <div class="patient-cell">
                <div class="avatar">${initials}</div>
                <div>
                  <div style="font-weight:700">${nome}</div>
                  <div class="small">${c.paciente_servico || ""}</div>
                </div>
              </div>
            </td>
            <td>${dateStr}</td>
            <td>${timeStr}</td>
            <td>${serv}</td>
            <td><span class="${statusClass}">${status}</span></td>
          </tr>`;
        }).join("");
      }
    }

    const user = window.api.getUser ? window.api.getUser() : null;
    if (user) {
      document.querySelectorAll("#userInfo").forEach(el => {
        if (el) el.innerText = user.nome || user.nome_completo || user.email;
      });
    }
  } catch (err) {
    console.error("Erro ao carregar dashboard:", err);
    const tbody = document.querySelector("#tabela-consultas tbody");
    if (tbody) tbody.innerHTML = `<tr><td colspan="5">Erro ao carregar dados.</td></tr>`;
  }
});
