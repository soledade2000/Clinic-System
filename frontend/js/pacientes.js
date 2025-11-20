// frontend/js/pacientes.js
const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  const tabela = document.getElementById("tabela-pacientes").querySelector("tbody");
  const showingCount = document.getElementById("showingCount");
  const totalCount = document.getElementById("totalCount");

  const modal = document.createElement("div");
  modal.classList.add("modal");
  modal.innerHTML = `
    <div class="modal-content">
      <button class="close">×</button>
      <h3 id="pacienteNome"></h3>
      <p id="pacienteInfo"></p>

      <h4>💳 Forma de Pagamento</h4>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:12px;">
        <select id="formaPagamentoSelect">
          <option value="">Selecione...</option>
          <option value="Dinheiro">Dinheiro</option>
          <option value="Pix">Pix</option>
          <option value="Cartão de Crédito">Cartão de Crédito</option>
          <option value="Cartão de Débito">Cartão de Débito</option>
        </select>
        <button id="btnSalvarPagamento">Salvar</button>
      </div>
      <p id="pagamentoMsg" style="color:#064e3b;"></p>

      <hr style="margin:14px 0;"/>

      <h4>📎 Arquivos do Paciente</h4>
      <input type="file" id="fileInput" />
      <button id="btnUpload">Enviar</button>
      <div id="uploadMsg" style="color:#064e3b;margin-top:4px;"></div>
      <ul id="fileList"></ul>

      <hr style="margin:14px 0;"/>

      <h4>📄 Ficha do Paciente</h4>
      <div style="display:flex;gap:8px;align-items:center;margin-bottom:10px;">
        <button id="btnGerarPDF">Gerar Ficha PDF</button>
        <input type="file" id="fichaUpload" accept="application/pdf" />
        <button id="btnEnviarFicha">Enviar PDF Manual</button>
      </div>
      <div id="pdfMsg" style="color:#0f172a;"></div>
    </div>
  `;
  document.body.appendChild(modal);
  modal.querySelector(".close").onclick = () => modal.classList.remove("open");

  // ==========================
  // 🔹 Carregar todos os pacientes
  // ==========================
  async function carregarPacientes() {
    try {
      const res = await fetch(`${API_URL}/pacientes`);
      if (!res.ok) throw new Error(`Erro HTTP: ${res.status}`);
      const pacientes = await res.json();

      tabela.innerHTML = "";
      totalCount.textContent = pacientes.length;
      showingCount.textContent = pacientes.length;

      pacientes.forEach(p => {
        // ⚙️ Garante que o campo servicos seja string
        const servicos = Array.isArray(p.servicos) ? p.servicos.join(", ") : (p.servicos || "-");

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td class="paciente-nome" data-id="${p.id}" style="cursor:pointer; color:#007bff; text-decoration:underline;">
            ${p.nome_completo}
          </td>
          <td>${servicos}</td>
          <td>${p.telefone || "-"}</td>
          <td>${p.email || "-"}</td>
          <td>${p.endereco || "-"}</td>
          <td><span class="status ${p.ativo ? "ativo" : "inativo"}">${p.ativo ? "Ativo" : "Inativo"}</span></td>
        `;
        tabela.appendChild(tr);
      });

      document.querySelectorAll(".paciente-nome").forEach(el => {
        el.addEventListener("click", e => {
          const id = e.target.dataset.id;
          abrirPainelPaciente(id);
        });
      });

    } catch (err) {
      console.error("Erro ao carregar pacientes:", err);
      tabela.innerHTML = `<tr><td colspan="6">Erro ao carregar pacientes.</td></tr>`;
    }
  }

  // ==========================
  // 🔹 Abrir painel do paciente
  // ==========================
  async function abrirPainelPaciente(id) {
    try {
      const res = await fetch(`${API_URL}/pacientes/${id}`);
      if (!res.ok) throw new Error("Paciente não encontrado");
      const p = await res.json();

      modal.classList.add("open");
      document.getElementById("pacienteNome").textContent = p.nome_completo;

      // ⚙️ Garante formatação segura
      const servicos = Array.isArray(p.servicos) ? p.servicos.join(", ") : (p.servicos || "-");

      document.getElementById("pacienteInfo").innerHTML = `
        <b>Email:</b> ${p.email} | <b>Telefone:</b> ${p.telefone}<br/>
        <b>Serviço:</b> ${servicos}<br/>
        <b>Forma de pagamento:</b> ${p.forma_pagamento || "— não definida —"}
      `;

      document.getElementById("formaPagamentoSelect").value = p.forma_pagamento || "";

      carregarArquivos(id);

      // --- Atualizar forma de pagamento ---
      document.getElementById("btnSalvarPagamento").onclick = async () => {
        const novaForma = document.getElementById("formaPagamentoSelect").value;
        const msg = document.getElementById("pagamentoMsg");
        msg.textContent = "Salvando...";

        try {
          const resp = await fetch(`${API_URL}/pacientes/${id}/pagamento`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ forma_pagamento: novaForma })
          });
          const data = await resp.json();
          if (resp.ok) {
            msg.textContent = "Forma de pagamento atualizada!";
            carregarPacientes();
          } else {
            msg.textContent = `Erro: ${data.detail || "não foi possível salvar."}`;
          }
        } catch (err) {
          msg.textContent = "Erro na conexão com o servidor.";
        }
      };

      // --- Upload de arquivos comuns ---
      document.getElementById("btnUpload").onclick = async () => {
        const fileInput = document.getElementById("fileInput");
        const file = fileInput.files[0];
        const msg = document.getElementById("uploadMsg");
        if (!file) return alert("Selecione um arquivo");
        const formData = new FormData();
        formData.append("file", file);
        msg.textContent = "Enviando...";
        const res = await fetch(`${API_URL}/pacientes/${id}/upload`, { method: "POST", body: formData });
        if (res.ok) {
          msg.textContent = "Arquivo enviado!";
          carregarArquivos(id);
          fileInput.value = "";
        } else {
          msg.textContent = "Erro no upload.";
        }
      };

      // --- Gerar ficha PDF automaticamente ---
      document.getElementById("btnGerarPDF").onclick = async () => {
        const msg = document.getElementById("pdfMsg");
        msg.textContent = "Gerando PDF...";
        try {
          const response = await fetch(`${API_URL}/pacientes/${id}/generate_pdf`);
          if (!response.ok) {
            const txt = await response.text();
            throw new Error(txt);
          }
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          msg.innerHTML = `<a href="${url}" target="_blank">📄 Abrir ficha gerada</a>`;
        } catch (err) {
          console.error(err);
          msg.textContent = "Erro ao gerar PDF. Verifique se o paciente possui dados válidos.";
        }
      };

      // --- Enviar ficha PDF manual ---
      document.getElementById("btnEnviarFicha").onclick = async () => {
        const file = document.getElementById("fichaUpload").files[0];
        const msg = document.getElementById("pdfMsg");
        if (!file) return alert("Selecione um PDF primeiro");
        const formData = new FormData();
        formData.append("file", file);
        formData.append("paciente_id", id);
        msg.textContent = "Enviando PDF...";
        try {
          const res = await fetch(`${API_URL}/pacientes/upload_pdf`, { method: "POST", body: formData });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || "Erro ao enviar PDF");
          msg.textContent = "PDF anexado com sucesso!";
        } catch (err) {
          msg.textContent = "Falha ao enviar PDF.";
        }
      };

    } catch (err) {
      alert("Erro ao abrir paciente: " + err.message);
    }
  }

  // ==========================
  // 🔹 Listar arquivos do paciente
  // ==========================
  async function carregarArquivos(id) {
    try {
      const res = await fetch(`${API_URL}/pacientes/${id}/list`);
      const data = await res.json();
      const list = document.getElementById("fileList");
      list.innerHTML = "";
      if (!data.files || data.files.length === 0) {
        list.innerHTML = "<li>Nenhum arquivo.</li>";
        return;
      }
      data.files.forEach(f => {
        const li = document.createElement("li");
        li.innerHTML = `
          <a href="${API_URL}${f.url}" target="_blank">${f.filename}</a>
          <button data-f="${f.filename}" style="margin-left:8px;">🗑️</button>
        `;
        li.querySelector("button").onclick = async (e) => {
          if (!confirm("Excluir este arquivo?")) return;
          await fetch(`${API_URL}/pacientes/${id}/delete/${f.filename}`, { method: "DELETE" });
          carregarArquivos(id);
        };
        list.appendChild(li);
      });
    } catch (err) {
      console.error("Erro ao listar arquivos:", err);
    }
  }

  carregarPacientes();
});
