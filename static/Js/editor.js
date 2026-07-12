document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("btn-inserir-imagem");
  const input = document.getElementById("input-imagem-inline");
  const textarea = document.getElementById("conteudo");
  const status = document.getElementById("upload-status");

  if (!btn || !input || !textarea) return;

  btn.addEventListener("click", () => input.click());

  input.addEventListener("change", async () => {
    const file = input.files[0];
    if (!file) return;

    status.textContent = "enviando imagem...";
    btn.disabled = true;

    const formData = new FormData();
    formData.append("imagem", file);

    try {
      const resp = await fetch("/upload-imagem", { method: "POST", body: formData });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.erro || "falha no upload");

      const trecho = `\n![${file.name}](${data.url})\n`;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      textarea.value = textarea.value.slice(0, start) + trecho + textarea.value.slice(end);
      const novaPosicao = start + trecho.length;
      textarea.focus();
      textarea.setSelectionRange(novaPosicao, novaPosicao);

      status.textContent = "imagem inserida no texto.";
    } catch (e) {
      status.textContent = "erro: " + e.message;
    } finally {
      btn.disabled = false;
      input.value = "";
    }
  });
});
