// Ricerca locale nella tabella dei combattenti: nessun server, nessun cookie,
// nessun tracking. Filtra le righe per testo, campagna, guerra/tag, tipo di corpo e fonte.
(() => {
  const input = document.querySelector("#cerca");
  const campagna = document.querySelector("#campagna");
  const categoria = document.querySelector("#categoria");
  const tag = document.querySelector("#tag");
  const fonte = document.querySelector("#fonte");
  const azzera = document.querySelector("#azzera");
  const tabella = document.querySelector("#tabella-combattenti");
  if (!input || !tabella) return;

  const righe = [...tabella.querySelectorAll("tbody tr")];
  const esito = document.querySelector("#esito");
  const vuoto = document.querySelector("#nessun-risultato");
  const totale = righe.length;

  const norm = (s = "") =>
    s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  const aggiorna = () => {
    const q = norm(input.value.trim());
    const anno = campagna ? campagna.value : "";
    const tipo = categoria ? categoria.value : "";
    const sorgente = fonte ? fonte.value : "";
    const cartellino = tag ? tag.value : "";
    let visibili = 0;

    for (const tr of righe) {
      const testo = norm(tr.dataset.cerca || tr.textContent);
      const anni = (tr.dataset.campagne || "").split(" ");
      const cartellini = (tr.dataset.tags || "").split(" ");
      const ok =
        (!q || testo.includes(q)) &&
        (!anno || anni.includes(anno)) &&
        (!tipo || tr.dataset.categoria === tipo) &&
        (!sorgente || (tr.dataset.fonte || "").includes(sorgente)) &&
        (!cartellino || cartellini.includes(cartellino));
      tr.hidden = !ok;
      if (ok) visibili += 1;
    }

    if (esito) {
      esito.textContent =
        q || anno || tipo || sorgente || cartellino
          ? `${visibili} di ${totale} combattenti`
          : `${totale} combattenti`;
    }

    if (vuoto) {
      vuoto.hidden = visibili !== 0;
      if (visibili === 0) {
        const parti = [];
        if (q) parti.push(`«${input.value.trim()}»`);
        if (anno) parti.push(`campagna ${anno}`);
        if (tipo) parti.push(`corpo «${tipo}»`);
        if (sorgente) parti.push(`fonte «${sorgente}»`);
        if (cartellino) parti.push(`tag «${cartellino}»`);
        vuoto.textContent = `Nessun risultato per ${parti.join(" e ")}.`;
      }
    }
  };

  input.addEventListener("input", aggiorna);
  if (campagna) campagna.addEventListener("change", aggiorna);
  if (categoria) categoria.addEventListener("change", aggiorna);
  if (fonte) fonte.addEventListener("change", aggiorna);
  if (tag) tag.addEventListener("change", aggiorna);
  if (azzera) {
    azzera.addEventListener("click", () => {
      input.value = "";
      if (campagna) campagna.value = "";
      if (categoria) categoria.value = "";
      if (fonte) fonte.value = "";
      if (tag) tag.value = "";
      aggiorna();
      input.focus();
    });
  }

  aggiorna();
})();
