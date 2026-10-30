"""
Lo script completo: legge i PDF, li fa analizzare a Claude e scrive i dati sul foglio.

Ogni PDF finisce in una di due cartelle:
- fatture_elaborate:  dati scritti sul foglio (o fattura già presente)
- fatture_con_errori: non è una fattura, o i dati non convincono: la controlli tu
"""

import shutil
from pathlib import Path

from estrai import estrai_dati, trova_problemi
from foglio import (
    aggiungi_fattura, collegati_a_sheets, fatture_gia_inserite,
    indirizzo_foglio, trova_o_crea_foglio,
)

DA_LEGGERE = Path("fatture_da_leggere")
ELABORATE = Path("fatture_elaborate")
CON_ERRORI = Path("fatture_con_errori")


def sposta(pdf, cartella):
    """Sposta il PDF senza sovrascrivere un file con lo stesso nome."""
    cartella.mkdir(exist_ok=True)
    destinazione = cartella / pdf.name
    numero = 2
    while destinazione.exists():
        destinazione = cartella / f"{pdf.stem}_{numero}{pdf.suffix}"
        numero += 1
    shutil.move(pdf, destinazione)


def elabora(pdf, sheets, id_foglio, gia_inserite):
    """Gestisce un PDF e restituisce una frase che racconta com'è andata."""
    dati = estrai_dati(pdf)

    if not dati["e_una_fattura"]:
        sposta(pdf, CON_ERRORI)
        return f"DA CONTROLLARE: non sembra una fattura ({dati['descrizione']})"

    problemi = trova_problemi(dati)
    if problemi:
        sposta(pdf, CON_ERRORI)
        return "DA CONTROLLARE: " + "; ".join(problemi)

    chiave = (dati["fornitore"], dati["numero"])
    if chiave in gia_inserite:
        sposta(pdf, ELABORATE)
        return f"GIÀ PRESENTE: {dati['fornitore']} n. {dati['numero']}, non la inserisco di nuovo"

    aggiungi_fattura(sheets, id_foglio, dati, pdf.name)
    gia_inserite.add(chiave)
    sposta(pdf, ELABORATE)
    return f"INSERITA: {dati['fornitore']} n. {dati['numero']}, {dati['totale']} {dati['valuta']}"


if __name__ == "__main__":
    sheets = collegati_a_sheets()
    id_foglio = trova_o_crea_foglio(sheets)
    gia_inserite = fatture_gia_inserite(sheets, id_foglio)

    pdf_trovati = sorted(DA_LEGGERE.glob("*.pdf"))
    print(f"Ho trovato {len(pdf_trovati)} PDF.\n")

    for pdf in pdf_trovati:
        # Se un PDF dà errore, il programma passa al successivo. Il file resta
        # in fatture_da_leggere e verrà riprovato la prossima volta.
        try:
            print(f"{pdf.name} -> {elabora(pdf, sheets, id_foglio, gia_inserite)}")
        except Exception as errore:
            print(f"{pdf.name} -> ERRORE, lo riprovo la prossima volta: {errore}")

    print("\nFoglio:", indirizzo_foglio(id_foglio))
