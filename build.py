#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera combattenti.json e index.html per il sito sulle guerre d'indipendenza.

Sorgente: combattenti.tsv, trascrizione delle 140 schede del Progetto Torelli
(Album-Tabella della Torre di San Martino della Battaglia, Libro 2, Provincia
di Pavia, Comune di Gravellona, pp. 266-273, voci 10453-10592), più le schede
aggiunte dai ruoli matricolari dell'Archivio di Stato di Torino (colonna
`fonte`), che restano fuori dai conteggi dell'Album.

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


def intero(valore):
    valore = (valore or "").strip()
    return int(valore) if valore.isdigit() else 0


def carica():
    righe = []
    with TSV.open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            nome = r["nome_listing"].strip()
            corpo = r["corpo"].strip()
            campagne = r["campagna"].split()
            fonte = (r.get("fonte") or "Album-Tabella").strip()
            righe.append(
                {
                    "id": intero(r["id"]) if r["id"].strip().isdigit() else r["id"].strip(),
                    "album": intero(r["numero"]),
                    "pagina": intero(r["pagina"]),
                    "matricola": r["matricola"].strip(),
                    "nome": nome,
                    "cognome": nome.split()[0],
                    "grado": r["grado"].strip(),
                    "corpo": corpo,
                    "categoria": categoria(corpo),
                    "campagne": campagne,
                    "osservazioni": r["oss"].strip(),
                    "note": r["note"].strip(),
                    "fonte": fonte,
                    "fonti": [x.strip() for x in fonte.split("·") if x.strip()],
                    "as_to": "AS Torino" in fonte,
                }
            )
    righe.sort(key=lambda x: (x["nome"].lower(), x["album"]))
    return righe


ROWS = carica()
# Le statistiche raccontano l'Album-Tabella (140 schede); la tabella mostra
# anche le schede aggiunte da altre fonti, riconoscibili dal tag.
ALBUM = [r for r in ROWS if "Album-Tabella" in r["fonti"]]
N = len(ALBUM)
N_TOT = len(ROWS)
N_AS_TO = sum(1 for r in ROWS if r["as_to"])
CORPI = collections.Counter(r["corpo"] for r in ALBUM)
COGNOMI = collections.Counter(r["cognome"] for r in ALBUM)
CATEGORIE = collections.Counter(r["categoria"] for r in ALBUM)
CAMPAGNE = collections.Counter(c for r in ALBUM for c in r["campagne"])
OSSERVAZIONI = [r for r in ALBUM if r["osservazioni"]]
CON_OSSERVAZIONE = len(OSSERVAZIONI)
SENZA_MATRICOLA = sum(1 for r in ALBUM if not r["matricola"])
PLURI_CAMPAGNA = sum(1 for r in ALBUM if len(r["campagne"]) >= 4)
ENTRAMBE_1848_49 = sum(1 for r in ALBUM if {"1848", "1849"} <= set(r["campagne"]))
UOMINI_1848_49 = sum(1 for r in ALBUM if set(r["campagne"]) & {"1848", "1849"})

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
            str(r["album"]) if r["album"] else "",
            r["matricola"],
            r["nome"],
            r["grado"],
            r["corpo"],
            r["categoria"],
            " ".join(r["campagne"]),
            r["osservazioni"],
            r["note"],
            r["fonte"],
        ]
    )
    if r["album"] == 10514:
        cerca += " Delucca De Luca"
    matricola = r["matricola"] if r["matricola"] else "—"
    osservazioni = esc(r["osservazioni"]) if r["osservazioni"] else ""
    if r["note"]:
        osservazioni += f'<span class="nota-fonte">{esc(r["note"])}</span>'
    album = str(r["album"]) if r["album"] else "—"
    nome_html = f"<strong>{esc(r['nome'])}</strong>"
    if r["album"] == 10514:
        nome_html += ' <span class="rimando">→ <a href="#delucca">Pietro Delucca</a></span>'
    if r["as_to"]:
        nome_html += (
            ' <span class="tag" title="Archivio di Stato di Torino,'
            ' ruoli matricolari dei corpi volontari">AS Torino</span>'
        )
    return (
        f"<tr data-campagne=\"{esc_attr(' '.join(r['campagne']))}\" "
        f"data-categoria=\"{esc_attr(r['categoria'])}\" "
        f"data-fonte=\"{esc_attr(' '.join(r['fonti']))}\" "
        f"data-cerca=\"{esc_attr(cerca)}\">"
        f"<td class=\"n\">{i}</td>"
        f"<td>{nome_html}</td>"
        f"<td>{esc(r['grado'])}</td>"
        f"<td>{esc(r['corpo'])}</td>"
        f"<td class=\"campagne\">{esc(', '.join(r['campagne']))}</td>"
        f"<td class=\"oss\">{osservazioni}</td>"
        f"<td class=\"n\">{esc(matricola)}</td>"
        f"<td class=\"n\">{esc(album)}</td>"
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
<meta name="description" content="140 combattenti gravellonesi delle guerre d'indipendenza e del Risorgimento, 1848-1870, più un volontario dai ruoli dell'Archivio di Stato di Torino: tabella, dati e ricerca.">
<link rel="canonical" href="{SITE_URL}">
<meta property="og:type" content="website">
<meta property="og:title" content="Guerre d'indipendenza — Gravellona Lomellina">
<meta property="og:description" content="140 combattenti gravellonesi del Risorgimento, 1848-1870, più un volontario dai ruoli dell'Archivio di Stato di Torino: tabella, dati e ricerca.">
<meta property="og:url" content="{SITE_URL}">
<link rel="stylesheet" href="style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="./">Guerre d'indipendenza</a>
    <p class="motto">Gravellona Lomellina · 1848-1870</p>
  </div>
  <figure class="header-immagine">
    <img src="header-porta-pia.jpg" alt="Bersaglieri italiani all'assalto presso Porta Pia, dipinto di Michele Cammarano" width="1400" height="867">
    <figcaption>Michele Cammarano, <em>I bersaglieri alla presa di Porta Pia</em> (1871). Pubblico dominio, <a href="https://commons.wikimedia.org/wiki/File:I_bersaglieri_alla_presa_di_Porta_Pia._Autore_Michelle_Cammarano.jpg">Wikimedia Commons</a>.</figcaption>
  </figure>
</header>

<main class="wrap">
  <h1>I gravellonesi delle guerre d'indipendenza</h1>
  <p class="lead">L'Album-Tabella della Torre di San Martino della Battaglia registra <strong>{N} gravellonesi</strong> che presero parte alle campagne militari del Risorgimento, dal 1848 al 1870. Non è un elenco di caduti: è un elenco di combattenti. Le schede dicono grado, corpo e anni di campagna; solo {CON_OSSERVAZIONE} hanno un'osservazione, e solo tre riguardano il sangue: un morto a Custoza, un ferito a Villafranca, un disperso nel 1848.</p>

  <p>Ai {N} dell'Album si aggiunge <strong>Grugnetti Gaudenzio</strong> (1866), che non compare nell'Album ma nei ruoli matricolari dei corpi volontari dell'<strong>Archivio di Stato di Torino</strong>: in tabella porta il tag <span class="tag">AS Torino</span>. I conteggi e le statistiche restano quelli delle {N} schede dell'Album.</p>

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

  <p>Un volontario del 1866 non è nell'Album ma nei <strong>ruoli matricolari dell'Archivio di Stato di Torino</strong>: <strong>Grugnetti Gaudenzio</strong> di Carlo, 19 anni, del Corpo dei Volontari Italiani, <strong>prigioniero a Bezzecca il 21 luglio 1866</strong> (mazzo 122). In tabella è segnato con il tag <span class="tag">AS Torino</span>. Dallo stesso fondo viene il riscontro su <strong>Silva Giuseppe</strong> fu Giovanni, caporale del 4° Fanteria Volontari Italiani, 36 anni, madre Rigoni Anna (mazzo 119): è lo stesso uomo dell'Album n. 10587. Resta fuori <strong>Collini Giacomo</strong>, nato a <em>Gravellona Toce</em> (Novara), non a Gravellona Lomellina.</p>

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

  <p id="delucca"><strong>Deluca Pietro</strong> di Giovanni, sottocaporale dei Bersaglieri, campagna 1848, è dato <strong>disperso</strong>. Negroni (1885) lo dice anche <strong>ferito a Santa Lucia</strong> (6 maggio 1848): «disperso» e «ferito» convivono in due documenti diversi. Nell'Album-Tabella «disperso» vale «uscito dai ruoli, traccia persa», non necessariamente caduto. È lo stesso <strong>Pietro Delucca</strong> (Pietro De Luca) che la memoria locale ricorda come fondatore delle scuole elementari e a cui è intitolata la piazza (Colli 1960, pp. 97-99).</p>

  <p>Le decorazioni registrate sono quattro: <strong>Sempio Giuseppe</strong> (Novara Cavalleria, medaglia d'argento a Macerone, 1860), <strong>Curti Carlo Maria</strong> (24° Fanteria, medaglia d'argento), <strong>Barbavara Gravellona cav. Ottavio Costantino Antonio Maria</strong> (49° Fanteria, croce dell'Ordine Militare di Savoia e medaglia d'argento) e il già citato <strong>Barbavara di Gravellona cav. Ottavio di Costantino</strong>.</p>

  <h2 id="elenco">L'elenco</h2>
  <p>Tabella completa dei {N_TOT} combattenti, in ordine alfabetico. Cerca per nome, grado, corpo, campagna, matricola o osservazione; filtra per anno, tipo di corpo e fonte.</p>

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
    <div class="filtro">
      <label for="fonte">Fonte</label>
      <select id="fonte">
        <option value="">tutte</option>
        <option value="Album-Tabella">Album-Tabella</option>
        <option value="AS Torino">AS Torino (ruoli matricolari)</option>
      </select>
    </div>
    <div class="filtro filtro-azione">
      <button type="button" id="azzera">Azzera</button>
    </div>
  </div>

  <p class="esito" id="esito" role="status" aria-live="polite">{N_TOT} combattenti</p>
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

  <p class="legenda"><strong>Campagne</strong>: anni di campagna, non singole battaglie. <strong>Osservazioni</strong>: solo {CON_OSSERVAZIONE} schede su {N}. <strong>Matricola</strong>: manca per {SENZA_MATRICOLA} ufficiali. <strong>Album</strong>: numero di voce nell'Album-Tabella (10453-10592); il trattino indica una scheda che dall'Album non viene. <strong>AS Torino</strong>: riscontro o aggiunta dai ruoli matricolari dei corpi volontari (Archivio di Stato di Torino), fuori dai conteggi dell'Album. L'elenco è in ordine alfabetico.</p>

  <h2 id="fonti">Fonti e metodo</h2>
  <ul class="fonti">
    <li>Progetto Torelli (Società Solferino e San Martino), trascrizione degli <em>Album-Tabella della Torre Storica di San Martino della Battaglia</em>, Libro 2, Provincia di Pavia, Comune di Gravellona, pp. 266-273, voci n. 10453-10592, trascrizione di Niccolò Federici (2018/2019), consultato il 18 ottobre 2026. Portale: <a href="https://www.solferinoesanmartino.it/progetto-torelli/ricerca/">solferinoesanmartino.it/progetto-torelli</a>.</li>
    <li>La banca dati Torelli è una <strong>trascrizione</strong>: la fonte primaria è l'Album-Tabella cartaceo. I campi non ricavabili dalla banca dati — data e luogo di nascita, paternità estesa, note di corpo — richiedono l'originale.</li>
    <li>Archivio di Stato di Torino, <em>Alla ricerca dei garibaldini scomparsi</em>: ruoli matricolari dei corpi volontari (Spedizione dei Mille 1860; Corpo dei Volontari Italiani 1866), schede n. 62280 (Grugnetti Gaudenzio, mazzo 122) e n. 83175 (Silva Giuseppe, mazzo 119), consultate il 22 ottobre 2026. Portale: <a href="https://archiviodistatotorino.cultura.gov.it/garb_src/">archiviodistatotorino.cultura.gov.it/garb_src</a>.</li>
    <li>Ernesto Colli, <em>Gravellona Lomellina nella sua storia</em>, Novara 1960, pp. 97-99 (Pietro Delucca, scuole e piazza) e pp. 101-105 (contesto locale del 1849 e del 1859: occupazione, inondazione, requisizioni).</li>
    <li>Carlo Negroni, <em>Memorie storiche di Gravellona Lomellina</em>, 1885, per Pietro Deluca ferito a Santa Lucia.</li>
    <li>Ordinamenti e ricostruzioni: voci Wikipedia <em>Battaglia di Mortara</em>, <em>Battaglia della Sforzesca</em>, <em>Ordine di battaglia della battaglia di Solferino e San Martino</em>, <em>Ordine di battaglia della battaglia di Custoza (1866)</em>; storiologia.it per la composizione dell'esercito italiano del 1866.</li>
  </ul>

  <h2 id="contatti">Correzioni e contatti</h2>
  <p>Questo è un elenco di lavoro, non un albo definitivo. Se trovi un errore di trascrizione o un nome da aggiungere, scrivi a <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  <p class="ultimo-aggiornamento">Ultimo aggiornamento: {AGGIORNATO}.</p>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>Dati: Progetto Torelli, Album-Tabella di San Martino; Archivio di Stato di Torino, ruoli dei corpi volontari; Colli 1960 per il contesto. Testi originali <a href="https://creativecommons.org/licenses/by/4.0/deed.it">CC BY 4.0</a>, salvo diversa indicazione.</p>
    <p>Nessun cookie, nessun tracking. <a href="privacy.html">Privacy e correzioni</a>.</p>
  </div>
</footer>

<script src="cerca.js" defer></script>
</body>
</html>
"""

(ROOT / "index.html").write_text(HTML, encoding="utf-8")

print(f"index.html: {N_TOT} record ({N} Album + {N_TOT - N} aggiunta AS Torino), {len(HTML)} byte")
print(f"corpi distinti: {N_CORPI}; cognomi: {N_COGNOMI}; osservazioni: {CON_OSSERVAZIONE}")
print("campagne:", dict(sorted(CAMPAGNE.items())))
print("categorie:", dict(CATEGORIE))
print("top corpi:", top_corpi)
print("top cognomi:", top_cognomi)
