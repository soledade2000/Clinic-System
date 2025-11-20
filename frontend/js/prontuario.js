// frontend/js/prontuario.js
const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  const pacienteIdInput = document.getElementById("pacienteId");
  const btnBuscar = document.getElementById("btnBuscar");
  const pacienteInfo = document.getElementById("pacienteInfo");
  const consultasBody = document.getElementById("consultasPacienteBody");
  const buscarMsg = document.getElementById("buscarMsg");
  const formMsg = document.getElementById("formMsg");

  const fileUpload = document.getElementById("fileUpload");
  const btnEnviarArquivo = document.getElementById("btnEnviarArquivo");
  const listaArquivos = document.getElementById("listaArquivos");

  const prontuarioForm = document.getElementById("prontuarioForm");

  function readForm() {
    return {
      nome: document.getElementById("p_nome").value,
      idade: document.getElementById("p_idade").value,
      endereco: document.getElementById("p_endereco").value,
      telefone: document.getElementById("p_telefone").value,
      email: document.getElementById("p_email").value,
      servico: document.getElementById("p_servico").value,
      forma_pagamento: document.getElementById("p_forma_pagamento").value,
      queixa: document.getElementById("q_queixa").value,
      historico: document.getElementById("h_clinico").value,
      saved_at: new Date().toISOString()
    };
  }

  function fillForm(data) {
    if (!data) return;
    document.getElementById("p_nome").value = data.nome || "";
    document.getElementById("p_idade").value = data.idade || "";
    document.getElementById("p_endereco").value = data.endereco || "";
    document.getElementById("p_telefone").value = data.telefone || "";
    document.getElementById("p_email").value = data.email || "";
    document.getElementById("p_servico").value = data.servico || "";
    document.getElementById("p_forma_pagamento").value = data.forma_pagamento || "";
    document.getElementById("q_queixa").value = data.queixa || "";
    document.getElementById("h_clinico").value = data.historico || "";
  }

  function localKey(id) {
    return `prontuario:${id}`;
  }

  function loadVersions(id) {
    const versionsList = document.getElementById("versionsList");
    const saved = JSON.parse(localStorage.getItem(localKey(id)) || "[]");
    versionsList.innerHTML = saved.length
      ? saved.map(v => `<div>📄 ${new Date(v.saved_at).toLocaleString()} — ${v.nome || "-"}</div>`).join("")
      : "<div class='small'>Sem versões locais.</div>";
  }

  async function fetchPacienteAndConsultas(id) {
    try {
      const res = await fetch(`${API_URL}/pacientes/${id}`);
      if (!res.ok) throw new Error();
      const paciente = await res.json();
      pacienteInfo.innerHTML = `<p><b>${paciente.nome}</b><br>${paciente.telefone || ""}</p>`;

      const consultasRes = await fetch(`${API_URL}/consultas/paciente/${id}`);
      const consultas = await consultasRes.json();
      consultasBody.innerHTML = consultas.map(c => `
        <tr>
          <td>${new Date(c.data_hora).toLocaleString()}</td>
          <td>${c.usuario?.nome || "-"}</td>
          <td>${c.status}</td>
          <td>
            <textarea data-id="${c.id}" class="notaSessao" style="width:100%;">${c.observacoes || ""}</textarea>
            <button class="btnSalvarNota" data-id="${c.id}">Salvar</button>
          </td>
        </tr>
      `).join("");
    } catch (err) {
      pacienteInfo.innerHTML = "<p>Erro ao carregar paciente.</p>";
    }
  }

  btnBuscar.addEventListener("click", () => {
    const id = pacienteIdInput.value;
    if (!id) return alert("Informe o ID do paciente");
    fetchPacienteAndConsultas(id);
    loadVersions(id);
  });

  document.addEventListener("click", async (e) => {
    if (e.target.classList.contains("btnSalvarNota")) {
      const id = e.target.dataset.id;
      const nota = e.target.previousElementSibling.value;
      try {
        await fetch(`${API_URL}/consultas/${id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ observacoes: nota })
        });
        alert("Anotação salva!");
      } catch {
        alert("Erro ao salvar anotação");
      }
    }
  });

  document.getElementById("btnSalvar").addEventListener("click", () => {
    const id = pacienteIdInput.value;
    if (!id) return alert("Informe o ID do paciente");
    const data = readForm();
    const arr = JSON.parse(localStorage.getItem(localKey(id)) || "[]");
    arr.push(data);
    localStorage.setItem(localKey(id), JSON.stringify(arr));
    formMsg.textContent = "Salvo localmente.";
    loadVersions(id);
  });

  btnEnviarArquivo.addEventListener("click", async () => {
    const id = pacienteIdInput.value;
    const file = fileUpload.files[0];
    if (!id || !file) return alert("Selecione paciente e arquivo");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload/`, { method: "POST", body: formData });
      const data = await res.json();
      listaArquivos.innerHTML += `<div><a href="${API_URL}/download/${data.filename}" target="_blank">${data.filename}</a></div>`;
      alert("Arquivo enviado!");
    } catch {
      alert("Erro ao enviar arquivo");
    }
  });
});
