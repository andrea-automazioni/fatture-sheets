"""
Crea fatture PDF FINTE per provare il programma senza usare dati veri.

Le aziende, le partite IVA e gli importi sono inventati. Le fatture hanno aspetto
diverso apposta: nella realtà ogni fornitore usa il suo modello, ed è proprio
questo che rende utile l'AI rispetto a un programma con regole fisse.

Uso:  .venv\\Scripts\\python.exe esempi\\genera_fatture.py
"""

import subprocess
import tempfile
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CARTELLA = Path(__file__).resolve().parent.parent / "fatture_da_leggere"

PROVA = '<p style="color:#999;font-size:10px">Documento di prova con dati inventati</p>'


def righe(voci):
    return "".join(
        f"<tr><td>{descrizione}</td><td style='text-align:right'>{importo}</td></tr>"
        for descrizione, importo in voci
    )


# Modello 1: classico, con tabella. Tutto ben in vista.
CLASSICA = f"""
<h1 style="color:#1e3a8a">Forniture Grafiche Esempio Srl</h1>
<p>Via delle Prove 1, 00100 Roma<br>P.IVA IT00000000001</p>
<h2>FATTURA N. 2026/418</h2>
<p>Data: 02/10/2026<br>Scadenza pagamento: 15/11/2026</p>
<table border="1" cellpadding="8" style="border-collapse:collapse;width:100%">
<tr><th>Descrizione</th><th>Importo</th></tr>
{righe([("Inchiostro UV CMYK, 4 flaconi", "€ 80,00"), ("Pellicola PVC adesiva, 2 rotoli", "€ 24,51")])}
</table>
<p style="text-align:right">Imponibile: € 104,51<br>IVA 22%: € 22,99<br><b>TOTALE: € 127,50</b></p>
{PROVA}
"""

# Modello 2: stile moderno, date scritte a parole e totale in evidenza.
MODERNA = f"""
<div style="background:#111;color:#fff;padding:20px"><b style="font-size:24px">NOVA Web Esempio</b>
<br>Ditta individuale · P.IVA IT00000000002</div>
<p>Ricevuta di pagamento e fattura <b>#NW-77</b>, emessa il 3 ottobre 2026.</p>
<p>Servizio: hosting del sito per 12 mesi e dominio.</p>
<p>Compenso 200,00 euro + IVA al 22% (44,00 euro).</p>
<p style="font-size:30px;margin:20px 0"><b>Da pagare: 244,00 euro</b></p>
<p>Pagamento entro 30 giorni dalla data della fattura.</p>
{PROVA}
"""

# Modello 3: due aliquote IVA diverse, totale da leggere con attenzione.
DUE_ALIQUOTE = f"""
<h2>Cartoleria Esempio S.n.c.</h2>
<p>P.IVA IT00000000003 — Doc. FT 1093 del 10/10/2026 — scad. 10/12/2026</p>
<table border="1" cellpadding="6" style="border-collapse:collapse;width:100%">
<tr><th>Articolo</th><th>IVA</th><th>Netto</th></tr>
<tr><td>Risme carta A4 (20)</td><td>22%</td><td>60,00</td></tr>
<tr><td>Manuali tecnici (5)</td><td>4%</td><td>100,00</td></tr>
</table>
<p>IVA 22% su 60,00 = 13,20 · IVA 4% su 100,00 = 4,00</p>
<p>Totale imponibile 160,00 · Totale IVA 17,20 · <b>Totale documento 177,20 EUR</b></p>
{PROVA}
"""

# Modello 4: fornitore estero, in inglese e in dollari, senza scadenza.
INGLESE = f"""
<h1>Example Cloud Inc.</h1>
<p>1 Test Street, Testville, USA — VAT ID: EU000000000</p>
<p><b>Invoice</b> no. INV-5521 — Issued: October 12, 2026</p>
<p>AI automation platform, monthly plan: $49.00<br>Tax: $0.00</p>
<p><b>Total paid: $49.00 USD</b></p>
<p>Thank you for your business!</p>
{PROVA}
"""

# Modello 5: NON è una fattura. Il programma deve accorgersene e non inserirla.
NON_FATTURA = f"""
<h2>Preventivo n. 88</h2>
<p>Officina Esempio Srl — P.IVA IT00000000004</p>
<p>Gentile cliente, le proponiamo la riparazione del plotter a € 350,00 + IVA.</p>
<p>Il preventivo è valido 30 giorni e non costituisce fattura.</p>
{PROVA}
"""

FATTURE = {
    "forniture_grafiche.pdf": CLASSICA,
    "nova_web.pdf": MODERNA,
    "cartoleria.pdf": DUE_ALIQUOTE,
    "example_cloud.pdf": INGLESE,
    "preventivo_officina.pdf": NON_FATTURA,
}


if __name__ == "__main__":
    CARTELLA.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as cartella_temp:
        for nome, corpo in FATTURE.items():
            pagina = Path(cartella_temp) / "pagina.html"
            pagina.write_text(
                f'<!doctype html><meta charset="utf-8"><body style="font-family:Arial">{corpo}',
                encoding="utf-8",
            )
            subprocess.run(
                [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                 f"--user-data-dir={cartella_temp}\\profilo",
                 f"--print-to-pdf={CARTELLA / nome}", pagina.as_uri()],
                check=True, capture_output=True,
            )
            print("Creata:", nome)
