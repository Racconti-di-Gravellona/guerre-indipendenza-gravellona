# Guerre d'indipendenza — Gravellona Lomellina

Sito statico autonomo sui **140 combattenti gravellonesi** registrati negli
Album-Tabella della Torre di San Martino della Battaglia, dal 1848 al 1870.

**URL:** <https://racconti-di-gravellona.github.io/guerre-indipendenza-gravellona/>

Il sito è separato dal blog «Racconti di Gravellona»: il blog lo linka, ma non
ne dipende.

## Cosa contiene

- Tabella completa di **140 combattenti**: nominativo, grado, corpo, campagne,
  osservazioni, matricola e numero d'album.
- Ricerca client-side per testo, campagna e tipo di corpo, senza cookie.
- Statistiche: campagne, corpi, reparti, cognomi; perdite e decorazioni.
- Ricostruzioni per reparto di **1849** (Sforzesca/Mortara) e **1866**
  (Custoza/Trentino/Po), con l'avvertenza che non sono attribuzioni individuali.

## File

| file | ruolo |
|---|---|
| `combattenti.tsv` | sorgente: 140 righe trascritte dal Progetto Torelli |
| `build.py` | legge il TSV, genera `combattenti.json` e `index.html` |
| `combattenti.json` | dati strutturati per riuso |
| `index.html` | pagina generata (non modificare a mano) |
| `style.css` | stili |
| `cerca.js` | filtro locale |
| `privacy.html` | privacy, correzioni, licenza |

## Rigenerare

```sh
python3 build.py
```

Il generatore calcola statistiche e tabelle dai dati, così non si
disallineano dal TSV.

## Fonte

Progetto Torelli (Società Solferino e San Martino), trascrizione degli
*Album-Tabella della Torre Storica di San Martino della Battaglia*, Libro 2,
Provincia di Pavia, Comune di Gravellona, pp. 266-273, voci n. 10453-10592,
trascrizione di Niccolò Federici (2018/2019), consultato il 18 ottobre 2026.
<https://www.solferinoesanmartino.it/progetto-torelli/ricerca/>

La banca dati Torelli è una trascrizione: la fonte primaria è l'Album-Tabella
cartaceo. I campi non presenti nella banca dati (data e luogo di nascita,
paternità estesa, note di corpo) richiedono l'originale.

Per il contesto locale: Ernesto Colli, *Gravellona Lomellina nella sua storia*,
Novara 1960, cap. «I Caduti per la Patria», pp. 101-105.

## Pubblicazione

GitHub Pages, branch `main`, cartella radice. Non serve alcun build lato
server: `index.html`, `style.css`, `cerca.js` e `combattenti.json` sono già
pronti.

## Licenza

Testi originali: CC BY 4.0. I dati storici sono citati dalle fonti indicate e
non sono coperti dalla licenza. Nessuna scansione di opera protetta è inclusa
nel repo.

## Correzioni

<archivio-festadellarte@outlook.it>
