const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("pacienteForm");
  const msg = document.getElementById("msgPaciente");
  const pdfInput = document.getElementById("fichaPdfInput");
  const btnEnviarPdf = document.getElementById("btnEnviarPdf");
  const btnGerarPdf = document.getElementById("btnGerarPdf");
  const pdfMsg = document.getElementById("pdfMsg");

  const dataNascimentoInput = document.getElementById("data_nascimento");
  const idadeInput = document.getElementById("idade");

  // 🔹 Atualiza automaticamente o campo de idade ao selecionar data de nascimento
  dataNascimentoInput.addEventListener("change", () => {
    const data = new Date(dataNascimentoInput.value);
    if (!isNaN(data.getTime())) {
      const hoje = new Date();
      let idade = hoje.getFullYear() - data.getFullYear();
      const m = hoje.getMonth() - data.getMonth();
      if (m < 0 || (m === 0 && hoje.getDate() < data.getDate())) {
        idade--;
      }
      idadeInput.value = idade >= 0 ? idade : 0;
    } else {
      idadeInput.value = "";
    }
  });

  // 🔹 Coleta os dados do formulário no formato que o backend espera
  function collectFormData() {
    const servico = document.getElementById("servico")?.value || "";
    const diasSelecionados = Array.from(
      document.querySelectorAll('input[name="dias"]:checked')
    ).map(i => i.value);

    const condicoesSelecionadas = Array.from(
      document.querySelectorAll('input[name="condicoes"]:checked')
    ).map(i => i.value);

    const renda = parseFloat(document.getElementById("renda")?.value.replace(",", ".") || 0);
    const idade = parseInt(document.getElementById("idade")?.value || 0);

    return {
      nome_completo: document.getElementById("nome_completo")?.value || "",
      nome_social: document.getElementById("nome_social")?.value || null,
      data_nascimento: document.getElementById("data_nascimento")?.value || null,
      idade: idade,
      cpf: document.getElementById("cpf")?.value || "00000000000",
      dependente: false,
      nome_responsavel: null,
      data_nascimento_responsavel: null,
      endereco: document.getElementById("endereco")?.value || "",
      cep: document.getElementById("cep")?.value || "",
      cidade_estado: document.getElementById("cidade_estado")?.value || "",
      email: document.getElementById("email")?.value || "sememail@exemplo.com",
      telefone: document.getElementById("telefone")?.value || "",
      escolaridade: document.getElementById("escolaridade")?.value || "Fundamental",
      religiao: document.getElementById("religiao")?.value || "Nenhuma",
      estado_civil: document.getElementById("estado_civil")?.value || "Solteiro",
      servicos: servico ? [servico] : [],
      disponibilidade_dias: diasSelecionados,
      horario_atendimento: document.getElementById("horario")?.value || "--:--",
      renda_familiar: isNaN(renda) ? 0 : renda,
      condicoes: condicoesSelecionadas,
      medicacoes: document.getElementById("medicacoes")?.value || "",
      queixa: document.getElementById("queixa")?.value || "",
      orientacao: document.getElementById("orientacao")?.value || "",
      etnia: document.getElementById("etnia")?.value || "",
    };
  }

  // 🔹 Envio do formulário principal
  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 🔹 Validação básica de campos obrigatórios
    const obrigatorios = ["nome_completo", "data_nascimento", "telefone", "endereco", "cidade_estado", "servico"];
    for (const id of obrigatorios) {
      if (!document.getElementById(id)?.value) {
        msg.style.color = "#b91c1c";
        msg.textContent = `❌ O campo ${id.replace("_", " ")} é obrigatório.`;
        return;
      }
    }

    msg.style.color = "#0369a1";
    msg.textContent = "Salvando...";

    const payload = collectFormData();
    try {
      const res = await fetch(`${API_URL}/pacientes/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.text();
        throw new Error(err);
      }

      msg.style.color = "#15803d";
      msg.textContent = "✅ Paciente cadastrado com sucesso!";
      setTimeout(() => (window.location.href = "pacientes.html"), 1000);
    } catch (err) {
      console.error(err);
      msg.style.color = "#b91c1c";
      msg.textContent = "❌ Erro: " + (err.message || err);
    }
  });

  // 🔹 Enviar PDF e associar
  btnEnviarPdf.addEventListener("click", async () => {
    const file = pdfInput.files[0];
    if (!file) return (pdfMsg.textContent = "Selecione um PDF primeiro.");

    const chosen = prompt(
      "Informe o ID do paciente para associar, ou deixe vazio para criar novo:"
    );
    let pacienteId = chosen ? Number(chosen) : null;
    if (pacienteId && isNaN(pacienteId)) pacienteId = null;

    try {
      if (!pacienteId) {
        const basePayload = {
          nome_completo: document.getElementById("nome_completo")?.value || "Paciente sem nome",
          data_nascimento: document.getElementById("data_nascimento")?.value || null,
          cpf: "00000000000",
          dependente: false,
          endereco: document.getElementById("endereco")?.value || "Não informado",
          email: document.getElementById("email")?.value || "sememail@exemplo.com",
          telefone: document.getElementById("telefone")?.value || "",
          escolaridade: document.getElementById("escolaridade")?.value || "Fundamental",
          religiao: document.getElementById("religiao")?.value || "Nenhuma",
          estado_civil: document.getElementById("estado_civil")?.value || "Solteiro",
          servicos: ["Psicologia"],
          disponibilidade_dias: ["Segunda"],
          horario_atendimento: "--:--",
          renda_familiar: 0
        };

        const res = await fetch(`${API_URL}/pacientes/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(basePayload),
        });
        const novoPaciente = await res.json();
        pacienteId = novoPaciente.id;
      }

      pdfMsg.textContent = "Enviando PDF...";
      const formData = new FormData();
      formData.append("file", file);
      formData.append("paciente_id", pacienteId);

      const resp = await fetch(`${API_URL}/pacientes/upload_pdf`, {
        method: "POST",
        body: formData,
      });

      if (!resp.ok) throw new Error("Erro ao enviar PDF");
      pdfMsg.style.color = "#15803d";
      pdfMsg.textContent = "PDF associado ao paciente ID " + pacienteId;
    } catch (err) {
      pdfMsg.style.color = "#b91c1c";
      pdfMsg.textContent = "❌ " + (err.message || err);
    }
  });

  // 🔹 Gerar PDF automático
  btnGerarPdf.addEventListener("click", async () => {
    const id = prompt("Informe o ID do paciente para gerar o PDF:");
    if (!id) return;
    try {
      const res = await fetch(`${API_URL}/pacientes/${id}/generate_pdf`);
      if (!res.ok) throw new Error("Erro ao gerar PDF");
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ficha_paciente_${id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      pdfMsg.style.color = "#15803d";
      pdfMsg.textContent = "PDF gerado com sucesso!";
    } catch (err) {
      pdfMsg.style.color = "#b91c1c";
      pdfMsg.textContent = "Erro: " + (err.message || err);
    }
  });
});
