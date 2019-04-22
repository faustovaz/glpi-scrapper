from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from functools import reduce
from datetime import datetime
import scrapper as s

SPREADSHEET_ID = '1frgS8i5aqSmBn4q6J1jJfDcqOoy_3dVdGzidmbB5COI'

def clean_values(sheet, range):
    sheet.values().clear(spreadsheetId=SPREADSHEET_ID,
                        range=range, body={}).execute()

def update_sheet(sheet, range, values):
    clean_values(sheet, range)
    body = {'values': values}
    sheet.values().update(spreadsheetId=SPREADSHEET_ID,
                            range=range,
                            valueInputOption='USER_ENTERED',
                            body=body).execute()

def transform(dictionary):
    return [list(item) for item in dictionary.items()]

if __name__ == '__main__':
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json')
    service = build('sheets', 'v4', credentials=creds)
    sheets = service.spreadsheets()

    new_glpi_totals = s.get_totals_from_new_glpi('GLPI_USER', 'GLPI_PASSWORD')
    total = reduce(lambda x,y:x+y, list(new_glpi_totals[1].values()))
    update_sheet(sheets, 'NewGLPI!B2', [[total]])
    update_sheet(sheets, 'NewGLPI!A4:B24', transform(new_glpi_totals[1]))
    update_sheet(sheets,
                'NewGLPI!A24',
                [['Atualizado em {}' \
                        .format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))]])

    old_glpi_totals = s.get_totals_from_old_glpi('GLPI_USER', 'GLPI_PASSWORD')
    total = reduce(lambda x,y:x+y, list(old_glpi_totals[1].values()))
    update_sheet(sheets, 'OldGLPI!B2', [[total]])
    update_sheet(sheets, 'OldGLPI!A4:B24', transform(old_glpi_totals[1]))
    update_sheet(sheets,
                'OldGLPI!A24',
                [['Atualizado em {}' \
                        .format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))]])

    glpi_totals = s.glpi_totals(old_glpi_totals, new_glpi_totals)
    total = reduce(lambda x,y:x+y, list(glpi_totals[1].values()))
    update_sheet(sheets, 'TotalGLPI!B2', [[total]])
    update_sheet(sheets, 'TotalGLPI!A4:B24', transform(glpi_totals[1]))
    update_sheet(sheets,
                'TotalGLPI!A24',
                [['Atualizado em {}' \
                        .format(datetime.now().strftime('%d/%m/%Y %H:%M:%S'))]])
