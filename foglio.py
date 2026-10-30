"""
Tutto quello che riguarda Google: permesso di accesso e scrittura sul foglio.

Il programma crea da solo il foglio la prima volta e ne salva l'indirizzo in foglio_id.txt.
"""

import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# drive.file = il programma vede SOLO i file che ha creato lui, non tutto il tuo Drive
PERMESSI = ["https://www.googleapis.com/auth/drive.file"]

NOME_FOGLIO = "Fatture"
FILE_ID = "foglio_id.txt"
COLONNE = [
    "Fornitore", "Partita IVA", "Numero", "Data", "Scadenza",
    "Imponibile", "IVA", "Totale", "Valuta", "Descrizione", "File",
]


def collegati_a_sheets():
    """Restituisce un oggetto con cui parlare con Google Sheets."""
    credenziali = None
    if os.path.exists("token.json"):
        credenziali = Credentials.from_authorized_user_file("token.json", PERMESSI)

    if not credenziali or not credenziali.valid:
        if credenziali and credenziali.expired and credenziali.refresh_token:
            credenziali.refresh(Request())
        else:
            flusso = InstalledAppFlow.from_client_secrets_file("credentials.json", PERMESSI)
            credenziali = flusso.run_local_server(port=0)  # apre il browser
        with open("token.json", "w") as file:
            file.write(credenziali.to_json())

    return build("sheets", "v4", credentials=credenziali)


def trova_o_crea_foglio(sheets):
    """Restituisce l'ID del foglio. Se non esiste ancora, lo crea con le intestazioni."""
    if os.path.exists(FILE_ID):
        with open(FILE_ID) as file:
            return file.read().strip()

    foglio = sheets.spreadsheets().create(body={
        "properties": {"title": "Fatture fornitori", "locale": "it_IT"},
        "sheets": [{"properties": {"title": NOME_FOGLIO, "gridProperties": {"frozenRowCount": 1}}}],
    }).execute()
    id_foglio = foglio["spreadsheetId"]

    sheets.spreadsheets().values().append(
        spreadsheetId=id_foglio, range=NOME_FOGLIO,
        valueInputOption="RAW", body={"values": [COLONNE]},
    ).execute()

    # Intestazioni in grassetto
    id_scheda = foglio["sheets"][0]["properties"]["sheetId"]
    sheets.spreadsheets().batchUpdate(spreadsheetId=id_foglio, body={"requests": [{
        "repeatCell": {
            "range": {"sheetId": id_scheda, "startRowIndex": 0, "endRowIndex": 1},
            "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
            "fields": "userEnteredFormat.textFormat.bold",
        }
    }]}).execute()

    with open(FILE_ID, "w") as file:
        file.write(id_foglio)
    print("Foglio creato:", indirizzo_foglio(id_foglio))
    return id_foglio


def indirizzo_foglio(id_foglio):
    return f"https://docs.google.com/spreadsheets/d/{id_foglio}"


def fatture_gia_inserite(sheets, id_foglio):
    """Restituisce le coppie (fornitore, numero) già presenti, per evitare i doppioni."""
    risposta = sheets.spreadsheets().values().get(
        spreadsheetId=id_foglio, range=f"{NOME_FOGLIO}!A2:C",
    ).execute()
    return {
        (riga[0], riga[2]) for riga in risposta.get("values", []) if len(riga) >= 3
    }


def aggiungi_fattura(sheets, id_foglio, dati, nome_file):
    """Aggiunge una riga al foglio."""
    riga = [
        dati["fornitore"], dati["partita_iva"], dati["numero"], dati["data_emissione"],
        dati["data_scadenza"], dati["imponibile"], dati["iva"], dati["totale"],
        dati["valuta"], dati["descrizione"], nome_file,
    ]
    # RAW = scrivi il testo così com'è. Se un PDF contenesse qualcosa come "=FORMULA(...)",
    # resterebbe testo e non verrebbe eseguito dal foglio.
    sheets.spreadsheets().values().append(
        spreadsheetId=id_foglio, range=NOME_FOGLIO,
        valueInputOption="RAW", insertDataOption="INSERT_ROWS",
        body={"values": [["" if valore is None else valore for valore in riga]]},
    ).execute()
