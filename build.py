#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera combattenti.json e index.html per il sito sulle guerre d'indipendenza.

Sorgente: combattenti.tsv, trascrizione delle 140 schede del Progetto Torelli
(Album-Tabella della Torre di San Martino della Battaglia, Libro 2, Provincia
di Pavia, Comune di Gravellona, pp. 266-273, voci 10453-10592).

Uso: python3 build.py
"""

import collections
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
TSV = ROOT / "combattenti.tsv"
EMAIL = "archivio-festadellarte@outlook.it"
AGGIORNATO = "21 ottobre 2026"
SITE_URL = "https://racconti-di-gravellona.github.io/guerre-indipendenza-gravellona/"

ANNI = ["1848", "1849", "1855", "1856", "1859", "1860", "1861", "1866", "1870"]
CONTESTO = {
    "1848": "Prima guerra d'indipendenza",
    "1849": "Prima guerra d'indipendenza",
    "1855": "Guerra di Crimea",
    "1856": "Guerra di Crimea",
    "1859": "Seconda guerra d'indipendenza",
    "1860": "Campagne 1860-61",
    "1861": "Campagne 1860-61",
    "1866": "Terza guerra d'indipendenza",
    "1870": "Roma",
}

CATEGORIE_ORDINE = [
    "Fanteria",
    "Bersaglieri",
    "Cavalleria",
    "Artiglieria",
    "Granatieri",
    "Volontari",
    "Altri corpi",
]


def categoria(corpo):
    c = corpo.lower()
    if "bersaglier" in c:
        return "Bersaglieri"
    if "granatier" in c:
        return "Granatieri"
    if "cavalleria" in c or "cavalleggeri" in c:
        return "Cavalleria"
    if "artiglieria" in c:
        return "Artiglieria"
    if "volontari italiani" in c:
        return "Volontari"
    if "fanteria" in c:
        return "Fanteria"
    return "Altri corpi"


def carica():
    righe = []
    with TSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            nome = r["nome_listing"].strip()
            corpo = r["corpo"].strip()
            campagne = r["campagna"].split()
            righe.append(
                {
                    "id": int(r["id"]),
                    "album": int(r["numero"]),
                    "pagina": int(r["pagina"]),
                    "matricola": r["matricola"].strip(),
                    "nome": nome,
                    "cognome": nome.split()[0],
                    "grado": r["grado"].strip(),
                    "corpo": corpo,
                    "categoria": categoria(corpo),
                    "campagne": campagne,
                    "osservazioni": r["oss"].strip(),
                    "note": r["note"].strip(),
                }
            )
    righe.sort(key=lambda x: (x["nome"].lower(), x["album"]))
    return righe


ROWS = carica()
N = len(ROWS)
CORPI = collections.Counter(r["corpo"] for r in ROWS)
COGNOMI = collections.Counter(r["cognome"] for r in ROWS)
CATEGORIE = collections.Counter(r["categoria"] for r in ROWS)
CAMPAGNE = collections.Counter(c for r in ROWS for c in r["campagne"])
OSSERVAZIONI = [r for r in ROWS if r["osservazioni"]]
CON_OSSERVAZIONE = len(OSSERVAZIONI)
SENZA_MATRICOLA = sum(1 for r in ROWS if not r["matricola"])
PLURI_CAMPAGNA = sum(1 for r in ROWS if len(r["campagne"]) >= 4)
ENTRAMBE_1848_49 = sum(1 for r in ROWS if {"1848", "1849"} <= set(r["campagne"]))
UOMINI_1848_49 = sum(1 for r in ROWS if set(r["campagne"]) & {"1848", "1849"})

N_CORPI = len(CORPI)
N_COGNOMI = len(COGNOMI)


def pct(a, b):
    return int(100 * a / b + 0.5)


def esc(s):
    return html.escape(str(s))


def esc_attr(s):
    return html.escape(str(s), quote=True)


def table_rows(items, total, label_col="voce"):
    out = []
    for label, n in items:
        out.append(
            f"<tr><td>{esc(label)}</td><td class=\"n\">{n}</td>"
            f"<td class=\"n\">{pct(n, total)}%</td></tr>"
        )
    return "\n".join(out)


top_corpi = sorted(CORPI.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
top_cognomi = sorted(COGNOMI.items(), key=lambda kv: (-kv[1], kv[0]))[:10]

campagne_rows = "\n".join(
    f"<tr><td>{anno}</td><td>{esc(CONTESTO[anno])}</td>"
    f"<td class=\"n\">{CAMPAGNE.get(anno, 0)}</td></tr>"
    for anno in ANNI
)

categorie_rows = table_rows(
    [(c, CATEGORIE[c]) for c in CATEGORIE_ORDINE if CATEGORIE.get(c)],
    N,
)

corpi_rows = table_rows(top_corpi, N)
cognomi_rows = table_rows(top_cognomi, N)

sforzesca = [
    ("Settore della Sforzesca", 34, "Brigata Casale (11° e 12°) e altri reparti della 2ª Divisione Bes"),
    ("Settore di Mortara", 6, "Savoia Cavalleria, Granatieri, Nizza Cavalleria"),
    ("Non collocabili", 7, "Reparti non presenti nell'ordine di battaglia del 1849"),
]
sforzesca_rows = "\n".join(
    f"<tr><td>{esc(label)}</td><td class=\"n\">{n}</td>"
    f"<td class=\"n\">{pct(n, 47)}%</td><td>{esc(nota)}</td></tr>"
    for label, n, nota in sforzesca
)

custoza = [
    ("Custoza (Armata del Mincio)", 31),
    ("Trentino (Garibaldi e 61° Fanteria)", 10),
    ("Armata del Po, senza Custoza", 4),
    ("Non collocabili", 5),
]
custoza_rows = "\n".join(
    f"<tr><td>{esc(label)}</td><td class=\"n\">{n}</td>"
    f"<td class=\"n\">{pct(n, 50)}%</td></tr>"
    for label, n in custoza
)

osservazioni_rows = "\n".join(
    "<tr>"
    f"<td><strong>{esc(r['nome'])}</strong></td>"
    f"<td>{esc(r['grado'])}</td>"
    f"<td>{esc(r['corpo'])}</td>"
    f"<td>{esc(', '.join(r['campagne']))}</td>"
    f"<td>{esc(r['osservazioni'])}</td>"
    "</tr>"
    for r in OSSERVAZIONI
)


def riga_tabella(i, r):
    cerca = " ".join(
        [
            str(r["id"]),
            str(r["album"]),
            r["matricola"],
            r["nome"],
            r["grado"],
            r["corpo"],
            r["categoria"],
            " ".join(r["campagne"]),
            r["osservazioni"],
        ]
    )
    matricola = r["matricola"] if r["matricola"] else "—"
    osservazioni = r["osservazioni"] if r["osservazioni"] else ""
    return (
        f"<tr data-campagne=\"{esc_attr(' '.join(r['campagne']))}\" "
        f"data-categoria=\"{esc_attr(r['categoria'])}\" "
        f"data-cerca=\"{esc_attr(cerca)}\">"
        f"<td class=\"n\">{i}</td>"
        f"<td><strong>{esc(r['nome'])}</strong></td>"
        f"<td>{esc(r['grado'])}</td>"
        f"<td>{esc(r['corpo'])}</td>"
        f"<td class=\"campagne\">{esc(', '.join(r['campagne']))}</td>"
        f"<td class=\"oss\">{esc(osservazioni)}</td>"
        f"<td class=\"n\">{esc(matricola)}</td>"
        f"<td class=\"n\">{r['album']}</td>"
        "</tr>"
    )


elenco_rows = "\n".join(riga_tabella(i, r) for i, r in enumerate(ROWS, 1))

(ROOT / "combattenti.json").write_text(
    json.dumps(ROWS, ensure_ascii=False, indent=2), encoding="utf-8"
)

HTML = f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guerre d'indipendenza — Gravellona Lomellina</title>
<meta name="description" content="140 combattenti gravellonesi delle guerre d'indipendenza e del Risorgimento, 1848-1870: tabella, dati e ricerca.">
<link rel="canonical" href="{SITE_URL}">
<meta property="og:type" content="website">
<meta property="og:title" content="Guerre d'indipendenza — Gravellona Lomellina">
<meta property="og:description" content="140 combattenti gravellonesi del Risorgimento, 1848-1870: tabella, dati e ricerca.">
<meta property="og:url" content="{SITE_URL}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="./">Guerre d'indipendenza</a>
    <p class="motto">Gravellona Lomellina · 1848-1870</p>
  </div>
</header>

<main class="wrap">
  <h1>I gravellonesi delle guerre d'indipendenza</h1>
  <p class="lead">L'Album-Tabella della Torre di San Martino della Battaglia registra <strong>{N} gravellonesi</strong> che presero parte alle campagne militari del Risorgimento, dal 1848 al 1870. Non è un elenco di caduti: è un elenco di combattenti. Le schede dicono grado, corpo e anni di campagna; solo {CON_OSSERVAZIONE} hanno un'osservazione, e solo tre riguardano il sangue: un morto a Custoza, un ferito a Villafranca, un disperso nel 1848.</p>

  <ul class="numeri">
    <li><strong>{N}</strong><span>combattenti</span></li>
    <li><strong>{N_COGNOMI}</strong><span>cognomi</span></li>
    <li><strong>{N_CORPI}</strong><span>corpi o reparti</span></li>
    <li><strong>{len(ANNI)}</strong><span>anni di campagna</span></li>
  </ul>

  <h2 id="numeri">I numeri</h2>
  <p>La prima guerra d'indipendenza coinvolge <strong>{UOMINI_1848_49} uomini</strong> tra 1848 e 1849, <strong>{ENTRAMBE_1848_49} dei quali in entrambi gli anni</strong>. Nel 1859 sono {CAMPAGNE['1859']}, nel 1866 {CAMPAGNE['1866']}: il picco. Solo <strong>{PLURI_CAMPAGNA} uomini</strong> raggiungono quattro o più campagne; il capitano Pietro Francesco Rossi ne totalizza sei.</p>

  <p>La <strong>fanteria di linea</strong> è {CATEGORIE['Fanteria']} su {N} ({pct(CATEGORIE['Fanteria'], N)}%). L'<strong>11° Regg. Fanteria</strong> ({CORPI['11° Regg. Fanteria']}) e il <strong>12° Regg. Fanteria</strong> ({CORPI['12° Regg. Fanteria']}) da soli raccolgono {CORPI['11° Regg. Fanteria'] + CORPI['12° Regg. Fanteria']} uomini ({pct(CORPI['11° Regg. Fanteria'] + CORPI['12° Regg. Fanteria'], N)}%). Seguono cavalleria ({CATEGORIE['Cavalleria']}), bersaglieri ({CATEGORIE['Bersaglieri']}), artiglieria ({CATEGORIE['Artiglieria']}), granatieri ({CATEGORIE['Granatieri']}), volontari ({CATEGORIE['Volontari']}) e altri corpi ({CATEGORIE['Altri corpi']}).</p>

  <p>Il grado più diffuso è <strong>Soldato</strong> (103), poi Caporale (9), Sergente (5), Appuntato (5) e Luogotenente Colonnello (3); il resto sono gradi singoli. La coscrizione toccava più fratelli e cugini della stessa casata: <strong>Barbè</strong> da solo conta 17 uomini.</p>

  <div class="tabelle">
    <div>
      <h3>Le campagne</h3>
      <table>
        <thead><tr><th>anno</th><th>contesto</th><th class="n">uomini</th></tr></thead>
        <tbody>
{campagne_rows}
        </tbody>
      </table>
      <p class="nota-tabella">Un uomo può comparire in più anni: la somma della colonna supera {N}.</p>
    </div>

    <div>
      <h3>I corpi</h3>
      <table>
        <thead><tr><th>tipo</th><th class="n">n.</th><th class="n">%</th></tr></thead>
        <tbody>
{categorie_rows}
        </tbody>
      </table>
      <p class="nota-tabella">«Altri corpi» comprende servizi, genio, treno e legioni.</p>
    </div>

    <div>
      <h3>I reparti più rappresentati</h3>
      <table>
        <thead><tr><th>reparto</th><th class="n">n.</th><th class="n">%</th></tr></thead>
        <tbody>
{corpi_rows}
        </tbody>
      </table>
      <p class="nota-tabella">A parità di numero, ordine alfabetico; la coda è fatta di reparti con uno o due uomini.</p>
    </div>

    <div>
      <h3>I cognomi più frequenti</h3>
      <table>
        <thead><tr><th>cognome</th><th class="n">n.</th><th class="n">%</th></tr></thead>
        <tbody>
{cognomi_rows}
        </tbody>
      </table>
      <p class="nota-tabella">Seguono altri 69 cognomi, con uno o due uomini ciascuno.</p>
    </div>
  </div>

  <h2 id="1848">1848: la prima campagna</h2>
  <p>Nel 1848 l'Album registra <strong>42 gravellonesi</strong>. La scheda non indica la singola battaglia: l'anno di campagna comprende <strong>Santa Lucia</strong> (6 maggio), <strong>Pastrengo</strong> (30 maggio), <strong>Goito</strong> (30 maggio) e <strong>Custoza</strong> (24-25 luglio). La banca dati non permette di attribuire il singolo uomo a uno di questi scontri; solo quando l'osservazione nomina un fatto d'arme — come Pastrengo per Barbavara — il collegamento è esplicito.</p>

  <h2 id="1849">1849: Sforzesca e Mortara</h2>
  <p>Nel 1849 l'Album registra <strong>47 gravellonesi</strong>. Incrociando i reparti con gli ordini di battaglia del 21 marzo, 34 ricadono nel settore della <strong>Sforzesca</strong> e 6 in quello di <strong>Mortara</strong>; 7 non sono collocabili. La Brigata Casale (11° e 12°) da sola ne conta 30, tutti nel settore della Sforzesca.</p>

  <table>
    <thead><tr><th>settore</th><th class="n">uomini</th><th class="n">%</th><th>reparti</th></tr></thead>
    <tbody>
{sforzesca_rows}
    </tbody>
  </table>

  <p class="avvertenza">La scheda Torelli registra l'anno di campagna, non la singola battaglia: la ripartizione è una <strong>ricostruzione per reparto</strong>, non una prova individuale. Tutti i 47 possono essere stati anche a <strong>Novara (Bicocca, 23 marzo)</strong>, dove la tradizione locale vuole presenti molti gravellonesi. La Sforzesca non è un comune ma una cascina di Vigevano; Mortara è un comune autonomo. I due scontri sono del medesimo giorno, il 21 marzo 1849.</p>

  <h2 id="1859">1859: San Martino</h2>
  <p>Nel 1859 gli uomini di Gravellona con campagna militare sono <strong>33</strong>. Tutti sono ascrivibili a <strong>San Martino (24 giugno)</strong>, la sola giornata in cui combatté l'intera armata sarda. Il baricentro è la <strong>5ª Divisione Cucchiari</strong> — Brigata Casale (11°-12°) e Brigata Acqui (17°-18°) — con 11 uomini. La 3ª Divisione Mollard e la 5ª Cucchiari figurano anche nei fatti dell'avanzata sul Sesia di fine maggio. <strong>Magenta</strong> resta una tradizione dell'11°-12°, non una presenza provata dei gravellonesi.</p>

  <h2 id="1866">1866: Custoza, Trentino, Po</h2>
  <p>Il 1866 è l'anno del <strong>picco assoluto (50 uomini)</strong> e anche il più articolato: la guerra si divise in tre teatri. Il gruppo maggiore va a <strong>Custoza</strong>, ma un quinto abbondante finisce in <strong>Trentino</strong>, quasi sempre nel 61° Fanteria e nei volontari di Garibaldi.</p>

  <table>
    <thead><tr><th>fronte</th><th class="n">uomini</th><th class="n">%</th></tr></thead>
    <tbody>
{custoza_rows}
    </tbody>
  </table>

  <p class="avvertenza">Anche qui la ripartizione è ricostruita per reparto, non provata scheda per scheda. I sette del <strong>61° Fanteria</strong> sono il secondo gruppo omogeneo del paese dopo l'11°-12° del 1849-1859.</p>

  <h2 id="perdite">Perdite e decorazioni</h2>
  <p>Le perdite non hanno una colonna propria: l'Album le annota, quando le annota, nelle <em>Osservazioni</em>. Su {N} schede solo <strong>{CON_OSSERVAZIONE}</strong> hanno un'osservazione; queste sono tutte.</p>

  <div class="tabella-scroll">
    <table class="tabella-osservazioni">
      <thead><tr><th>nominativo</th><th>grado</th><th>corpo</th><th>campagne</th><th>osservazioni</th></tr></thead>
      <tbody>
{osservazioni_rows}
      </tbody>
    </table>
  </div>

  <p><strong>Colli Giuseppe</strong> di Giovanni, soldato del 1° Regg. Bersaglieri, è l'unico gravellonese che l'Album dà per <strong>caduto</strong>: morto a <strong>Custoza</strong> il 24 giugno 1866. Aveva già fatto le campagne del 1859, 1860 e 1861.</p>

  <p><strong>Barbavara di Gravellona cav. Ottavio di Costantino</strong>, luogotenente colonnello del 2° Regg. Bersaglieri, è dato <strong>ferito a Villafranca</strong>, il combattimento del 24 giugno 1866 presso Verona. Lo stesso uomo è decorato di menzione onorevole a Pastrengo, croce di Cavaliere dell'Ordine Militare di Savoia a Castelfidardo e medaglia d'argento al valor militare.</p>

  <p><strong>Deluca Pietro</strong> di Giovanni, sottocaporale dei Bersaglieri, campagna 1848, è dato <strong>disperso</strong>. Negroni (1885) lo dice anche <strong>ferito a Santa Lucia</strong> (6 maggio 1848): «disperso» e «ferito» convivono in due documenti diversi. Nell'Album-Tabella «disperso» vale «uscito dai ruoli, traccia persa», non necessariamente caduto.</p>

  <p>Le decorazioni registrate sono quattro: <strong>Sempio Giuseppe</strong> (Novara Cavalleria, medaglia d'argento a Macerone, 1860), <strong>Curti Carlo Maria</strong> (24° Fanteria, medaglia d'argento), <strong>Barbavara Gravellona cav. Ottavio Costantino Antonio Maria</strong> (49° Fanteria, croce dell'Ordine Militare di Savoia e medaglia d'argento) e il già citato <strong>Barbavara di Gravellona cav. Ottavio di Costantino</strong>.</p>

  <h2 id="elenco">L'elenco</h2>
  <p>Tabella completa dei {N} combattenti, in ordine alfabetico. Cerca per nome, grado, corpo, campagna, matricola o osservazione; filtra per anno e per tipo di corpo.</p>

  <div class="filtri">
    <div class="filtro">
      <label for="cerca">Cerca</label>
      <input type="search" id="cerca" autocomplete="off" placeholder="es. Barbè, 11° Fanteria, 1849, disperso">
    </div>
    <div class="filtro">
      <label for="campagna">Campagna</label>
      <select id="campagna">
        <option value="">tutte</option>
        {''.join(f'<option value="{a}">{a}</option>' for a in ANNI)}
      </select>
    </div>
    <div class="filtro">
      <label for="categoria">Tipo di corpo</label>
      <select id="categoria">
        <option value="">tutti</option>
        {''.join(f'<option value="{c}">{c}</option>' for c in CATEGORIE_ORDINE if CATEGORIE.get(c))}
      </select>
    </div>
    <div class="filtro filtro-azione">
      <button type="button" id="azzera">Azzera</button>
    </div>
  </div>

  <p class="esito" id="esito" role="status" aria-live="polite">{N} combattenti</p>
  <p class="scorri">Scorri la tabella per vedere tutte le colonne.</p>

  <div class="tabella-scroll">
    <table id="tabella-combattenti" class="tabella-combattenti">
      <thead>
        <tr>
          <th class="n">#</th>
          <th>Nominativo</th>
          <th>Grado</th>
          <th>Corpo</th>
          <th>Campagne</th>
          <th>Osservazioni</th>
          <th class="n">Matricola</th>
          <th class="n">Album</th>
        </tr>
      </thead>
      <tbody>
{elenco_rows}
      </tbody>
    </table>
  </div>
  <p id="nessun-risultato" hidden>Nessun risultato.</p>

  <p class="legenda"><strong>Campagne</strong>: anni di campagna, non singole battaglie. <strong>Osservazioni</strong>: solo {CON_OSSERVAZIONE} schede su {N}. <strong>Matricola</strong>: manca per {SENZA_MATRICOLA} ufficiali. <strong>Album</strong>: numero di voce nell'Album-Tabella (10453-10592). L'elenco è in ordine alfabetico.</p>

  <h2 id="fonti">Fonti e metodo</h2>
  <ul class="fonti">
    <li>Progetto Torelli (Società Solferino e San Martino), trascrizione degli <em>Album-Tabella della Torre Storica di San Martino della Battaglia</em>, Libro 2, Provincia di Pavia, Comune di Gravellona, pp. 266-273, voci n. 10453-10592, trascrizione di Niccolò Federici (2018/2019), consultato il 18 ottobre 2026. Portale: <a href="https://www.solferinoesanmartino.it/progetto-torelli/ricerca/">solferinoesanmartino.it/progetto-torelli</a>.</li>
    <li>La banca dati Torelli è una <strong>trascrizione</strong>: la fonte primaria è l'Album-Tabella cartaceo. I campi non ricavabili dalla banca dati — data e luogo di nascita, paternità estesa, note di corpo — richiedono l'originale.</li>
    <li>Ernesto Colli, <em>Gravellona Lomellina nella sua storia</em>, Novara 1960, cap. «I Caduti per la Patria», pp. 101-105, per il contesto locale del 1849 e del 1859 (occupazione, inondazione, requisizioni).</li>
    <li>Carlo Negroni, <em>Memorie storiche di Gravellona Lomellina</em>, 1885, per Pietro Deluca ferito a Santa Lucia.</li>
    <li>Ordinamenti e ricostruzioni: voci Wikipedia <em>Battaglia di Mortara</em>, <em>Battaglia della Sforzesca</em>, <em>Ordine di battaglia della battaglia di Solferino e San Martino</em>, <em>Ordine di battaglia della battaglia di Custoza (1866)</em>; storiologia.it per la composizione dell'esercito italiano del 1866.</li>
  </ul>

  <h2 id="contatti">Correzioni e contatti</h2>
  <p>Questo è un elenco di lavoro, non un albo definitivo. Se trovi un errore di trascrizione o un nome da aggiungere, scrivi a <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  <p class="ultimo-aggiornamento">Ultimo aggiornamento: {AGGIORNATO}.</p>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>Dati: Progetto Torelli, Album-Tabella di San Martino; Colli 1960 per il contesto. Testi originali <a href="https://creativecommons.org/licenses/by/4.0/deed.it">CC BY 4.0</a>, salvo diversa indicazione.</p>
    <p>Nessun cookie, nessun tracking. <a href="privacy.html">Privacy e correzioni</a>.</p>
  </div>
</footer>

<script src="cerca.js" defer></script>
</body>
</html>
"""

(ROOT / "index.html").write_text(HTML, encoding="utf-8")

print(f"index.html: {N} record, {len(HTML)} byte")
print(f"corpi distinti: {N_CORPI}; cognomi: {N_COGNOMI}; osservazioni: {CON_OSSERVAZIONE}")
print("campagne:", dict(sorted(CAMPAGNE.items())))
print("categorie:", dict(CATEGORIE))
print("top corpi:", top_corpi)
print("top cognomi:", top_cognomi)
