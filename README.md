# Guerre d'indipendenza — Gravellona Lomellina

Sito statico autonomo sui **140 combattenti gravellonesi** registrati negli
Album-Tabella della Torre di San Martino della Battaglia, dal 1848 al 1870,
**più un volontario del 1866** aggiunto dai ruoli matricolari dell'Archivio di
Stato di Torino (tag `AS Torino` in tabella).

**URL:** <https://racconti-di-gravellona.github.io/guerre-indipendenza-gravellona/>

Il sito è separato dal blog «Racconti di Gravellona»: il blog lo linka, ma non
ne dipende.

## Cosa contiene

- Tabella completa di **141 schede**: 140 dall'Album (nominativo, grado, corpo,
  campagne, osservazioni, matricola, numero d'album) e 1 dai ruoli AS Torino
  (Grugnetti Gaudenzio, prigioniero a Bezzecca).
- Tag `AS Torino` sulle schede con riscontro o aggiunta dai ruoli matricolari;
  filtro dedicato. Le statistiche restano calcolate sulle 140 schede dell'Album.
- Ricerca client-side per testo, campagna e tipo di corpo, senza cookie.
- Statistiche: campagne, corpi, reparti, cognomi; perdite e decorazioni.
- Rimando a **Pietro Delucca** (Deluca nell'Album, De Luca nell'atto di morte),
  fondatore delle scuole elementari e titolare della piazza principale.
- Ricostruzioni per reparto di **1849** (Sforzesca/Mortara) e **1866**
  (Custoza/Trentino/Po), con l'avvertenza che non sono attribuzioni individuali.

## File

| file | ruolo |
|---|---|
| `combattenti.tsv` | sorgente: 141 righe (140 Album + 1 AS Torino), colonna `fonte` |
| `build.py` | legge il TSV, genera `combattenti.json` e `index.html` |
| `combattenti.json` | dati strutturati per riuso |
| `index.html` | pagina generata (non modificare a mano) |
| `style.css` | stili |
| `cerca.js` | filtro locale |
| `header-porta-pia.jpg` | header: Michele Cammarano, *I bersaglieri alla presa di Porta Pia* (1871), pubblico dominio |
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

Per le schede `AS Torino`: Archivio di Stato di Torino, *Alla ricerca dei
garibaldini scomparsi*, ruoli matricolari dei corpi volontari (Corpo dei
Volontari Italiani 1866), schede n. 62280 (mazzo 122) e n. 83175 (mazzo 119),
consultate il 22 ottobre 2026.
<https://archiviodistatotorino.cultura.gov.it/garb_src/>

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
