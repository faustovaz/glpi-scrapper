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

    new_glpi_searchs = {
        'new_glpi_open_totals': 18,
        'new_glpi_closed_today': 31,
        'new_glpi_closed_this_week': 37,
        'new_glpi_closed_this_month': 38
    }

    old_glpi_searchs = {
        'old_glpi_open_totals': 38,
        'old_glpi_closed_today': 188,
        'old_glpi_closed_this_week': 190,
        'old_glpi_closed_this_month': 191
    }

    news = s.get_search_results_from_glpi('https://chamados.unila.edu.br',
                                            glpi_user,
                                            glpi_password,
                                            new_glpi_searchs,
                                            system_index=6,
                                            employee_index=8,
                                            user_index=7)

    olds = s.get_search_results_from_glpi('https://chamados-old.unila.edu.br',
                                            glpi_user,
                                            glpi_password,
                                            old_glpi_searchs,
                                            system_index=4,
                                            employee_index=7,
                                            user_index=3)

    glpi_totals = s.glpi_totals(olds.get('old_glpi_open_totals'),
                                news.get('new_glpi_open_totals'))

    closed_ones = s.glpi_totals(olds.get('old_glpi_closed_today'),
                                news.get('new_glpi_closed_today'))

    closed_this_week = s.glpi_totals(olds.get('old_glpi_closed_this_week'),
                                    news.get('new_glpi_closed_this_week'))

    closed_this_month = s.glpi_totals(olds.get('old_glpi_closed_this_month'),
                                      news.get('new_glpi_closed_this_month'))

    update_sheets(glpi_totals[1], 'TotalGLPI')
    update_sheets(news.get('new_glpi_open_totals')[1], 'NewGLPI')
    update_sheets(olds.get('old_glpi_open_totals')[1], 'OldGLPI')
    update_sheets(closed_ones[1], 'FechadosHoje')
    update_sheets(closed_this_week[1], 'FechadosNaSemana')
    update_sheets(closed_this_month[1], 'FechadosNoMes')

    print("Done! All sheets updated on {}!" \
            .format(datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
