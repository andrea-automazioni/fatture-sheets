# 🧾 Fatture PDF → Google Sheets con l'AI

Metti le fatture PDF in una cartella: **Claude** (l'AI di Anthropic) legge ogni documento, ne estrae i dati e li scrive in un foglio Google. Funziona con modelli di fattura diversi, senza regole da configurare per ogni fornitore.

> 🇬🇧 **In English:** drop PDF invoices into a folder. Claude AI extracts supplier, number, dates, net amount, VAT and total, validates them and adds a row to a Google Sheet. Built with Python, Claude API (structured outputs) and Google Sheets API.

## Esempio di risultato

| Fornitore | Numero | Data | Scadenza | Imponibile | IVA | Totale | Valuta |
|---|---|---|---|---|---|---|---|
| Cartoleria Esempio S.n.c. | FT 1093 | 2026-10-10 | 2026-12-10 | 160,00 | 17,20 | 177,20 | EUR |
| Example Cloud Inc. | INV-5521 | 2026-10-12 | | 49,00 | 0,00 | 49,00 | USD |
| Forniture Grafiche Esempio Srl | 2026/418 | 2026-10-02 | 2026-11-15 | 104,51 | 22,99 | 127,50 | EUR |
| NOVA Web Esempio | NW-77 | 2026-10-03 | 2026-11-02 | 200,00 | 44,00 | 244,00 | EUR |

*Dati inventati: i PDF di prova li crea [`esempi/genera_fatture.py`](esempi/genera_fatture.py).*

## Come funziona

```
fatture_da_leggere/ ──► estrai.py ──► controlli ──► foglio.py ──► 📊 Google Sheets
   (i tuoi PDF)         (Claude)         │          (nuova riga)
                                         ▼
                                fatture_con_errori/
                                (le controlla una persona)
```

| File | Cosa fa |
|---|---|
| `estrai.py` | Manda il PDF a Claude, che compila sempre lo stesso modulo (output strutturato), e controlla il risultato |
| `foglio.py` | Gestisce il permesso Google, crea il foglio e aggiunge le righe |
| `elabora_fatture.py` | Unisce i pezzi e sposta ogni PDF nella cartella giusta |

## Casi provati

| Caso | Comportamento |
|---|---|
| Modelli di fattura diversi | Dati estratti correttamente |
| Scadenza scritta come "entro 30 giorni" | Data calcolata |
| Due aliquote IVA | Imponibile e IVA sommati |
| Fattura in inglese e in dollari, senza scadenza | Valuta riconosciuta, scadenza lasciata vuota |
| Preventivo (non è una fattura) | Non inserito, messo da parte |
| Stessa fattura arrivata due volte | Riconosciuta, non inserita di nuovo |

## Punti di attenzione gestiti

- **Controllo dei numeri:** imponibile + IVA deve dare il totale. Se non torna, o manca un dato essenziale, il PDF va in `fatture_con_errori` invece che sul foglio.
- **Permessi minimi:** con `drive.file` il programma vede solo il foglio che ha creato, non tutto il Drive.
- **Dati non fidati:** eventuali istruzioni nascoste in un PDF vengono ignorate, e sul foglio tutto viene scritto come valore (`RAW`), quindi una formula nascosta non viene eseguita.
- **Un errore non ferma tutto:** se un PDF dà problemi, il programma passa al successivo e lo riprova la volta dopo.
- **Sicurezza:** chiavi, credenziali e fatture sono esclusi da Git tramite `.gitignore`.

**Costo:** circa 1,4 centesimi a fattura con Claude Opus 5.5 (circa 2.750 token in entrata e 150 in uscita). Il modello si cambia in una riga di `estrai.py`.

## Limiti attuali

- Il controllo dei doppioni confronta fornitore e numero esatti: confrontare la partita IVA sarebbe più robusto.
- Provato su PDF di prova generati dal programma: fatture reali e scansioni vanno verificate prima dell'uso.
- Pensato per fatture PDF. Le fatture elettroniche italiane in XML si possono leggere direttamente, senza AI.

## Installazione

Requisiti: Python 3.12 o superiore, un account Google e una chiave API di Claude.

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

1. **Google Cloud:** crea un progetto, abilita *Google Sheets API* e *Google Drive API* e crea un client OAuth di tipo *App desktop*. Salva il JSON come `credentials.json` in questa cartella.
2. **Claude:** copia `.env.example` in `.env` e inserisci la tua chiave API.
3. **PDF di prova** (usa Google Chrome per crearli; il percorso è in cima allo script):
   ```bash
   .venv\Scripts\python.exe esempi\genera_fatture.py
   ```
4. **Avvio** (la prima volta apre il browser per l'autorizzazione):
   ```bash
   .venv\Scripts\python.exe elabora_fatture.py
   ```

## Personalizzazione

Per estrarre altri dati (codice cliente, centro di costo...) basta aggiungere il campo a `SCHEMA` in `estrai.py` e alla riga in `foglio.py`. Lo stesso schema funziona anche per ricevute, ordini o bolle.

---

Realizzato da **Andrea** · [andrea-automazioni.github.io](https://andrea-automazioni.github.io)
