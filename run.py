from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from functools import reduce
from datetime import datetime
import scrapper as s
import os
from dotenv import load_dotenv


def clean_values(sheet, range):
    sheet.values().clear(spreadsheetId=os.getenv('CHAMADOS_SPREADSHEET_ID'),
                        range=range, body={}).execute()

def update_sheet(sheet, range, values):
    clean_values(sheet, range)
    body = {'values': values}
    sheet.values().update(spreadsheetId=os.getenv('CHAMADOS_SPREADSHEET_ID'),
                            range=range,
                            valueInputOption='USER_ENTERED',
                            body=body).execute()

def transform(dictionary):
    return [list(item) for item in dictionary.items()]

def update_sheets(data, sheet_name):
    total = reduce(lambda x,y:x+y, list(data.values()))
    now = datetime.now()
    updated_at = 'Atualizado em {}'.format(now.strftime('%d/%m/%Y %H:%M:%S'))
    update_sheet(sheets, '{}!B2'.format(sheet_name), [[total]])
    update_sheet(sheets, '{}!A4:B24'.format(sheet_name), transform(data))
    update_sheet(sheets, '{}!A24'.format(sheet_name), [[updated_at]])

if __name__ == '__main__':
    env_file = os.path.join(os.path.dirname(__file__), 'credentials.env')
    load_dotenv(env_file)
    glpi_user = os.getenv('GLPI_USER')
    glpi_password = os.getenv('GLPI_PASSWORD')
    cred_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_file)
    service = build('sheets', 'v4', credentials=creds)
    sheets = service.spreadsheets()

    new_glpi_totals = s.get_totals_from_new_glpi(glpi_user, glpi_password)
    old_glpi_totals = s.get_totals_from_old_glpi(glpi_user, glpi_password)
    glpi_totals = s.glpi_totals(old_glpi_totals, new_glpi_totals)

    new_closed = s.get_closed_today_from_new_glpi(glpi_user, glpi_password)
    old_closed = s.get_closed_today_from_old_glpi(glpi_user, glpi_password)
    closed_ones = s.glpi_totals(old_closed, new_closed)

    update_sheets(new_glpi_totals[1], 'NewGLPI')
    update_sheets(old_glpi_totals[1], 'OldGLPI')
    update_sheets(glpi_totals[1], 'TotalGLPI')
    update_sheets(closed_ones[1], 'FechadosHoje')

    print("Done! All sheets updated on {}!" \
            .format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
