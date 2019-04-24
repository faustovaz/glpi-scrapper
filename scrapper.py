# -*- coding: utf-8 -*-
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

def get_search_result_from_new_glpi(user, password, search_id):
    glpi_url = 'https://chamados.unila.edu.br'
    search_link = '{}/front/savedsearch.php?action=load&id={}' \
                    .format(glpi_url, search_id)
    tables = get_tables_from_glpi(glpi_url, user, password, search_link)
    return get_totals_from_glpi(tables,
                                system_index=6,
                                employee_index=8,
                                user_index=7)

def get_search_result_from_old_glpi(user, password, search_id):
    glpi_url = 'https://chamados-old.unila.edu.br'
    search_link = '{}/front/savedsearch.php?action=load&id={}' \
                    .format(glpi_url, search_id)
    tables = get_tables_from_glpi(glpi_url, user, password, search_link)
    return get_totals_from_glpi(tables,
                                system_index=4,
                                employee_index=7,
                                user_index=3)

def get_totals_from_new_glpi(user, password):
    return get_search_result_from_new_glpi(user, password, 18)

def get_closed_today_from_new_glpi(user, password):
    return get_search_result_from_new_glpi(user, password, 31)

def get_totals_from_old_glpi(user, password):
    return get_search_result_from_old_glpi(user, password, 38)

def get_closed_today_from_old_glpi(user, password):
    return get_search_result_from_old_glpi(user, password, 188)

def get_closed_yesterday_from_new_glpi(user, password):
    return get_search_result_from_new_glpi(user, password, 36)

def get_closed_yesterday_from_old_glpi(user, password):
    return get_search_result_from_old_glpi(user, password, 189)

def get_tables_from_glpi(url, user, password, savedSearchLink):
    browser = login_into_glpi(url, user, password)
    browser.get(savedSearchLink)
    tables = []
    while True:
        try:
            table = browser.find_element_by_class_name('tab_cadrehov')
            tables.append(table.get_attribute('innerHTML'))
            pager = browser.find_element_by_class_name('tab_cadre_pager')
            forward_links = pager.find_elements_by_class_name('right')
            if len(forward_links) < 2:
                break
            next_page = forward_links[0].find_element_by_tag_name('a')
            browser.get(next_page.get_property('href'))
        except NoSuchElementException:
            break
    browser.close()
    return tables

def login_into_glpi(url, user, password):
    options = webdriver.FirefoxOptions()
    options.headless = True
    browser = webdriver.Firefox(options=options)
    browser.get(url)
    browser.find_element_by_id('login_name').send_keys(user)
    browser.find_element_by_id('login_password').send_keys(password)
    browser.find_element_by_name('submit').click()
    return browser

def get_totals_from_glpi(tables, **kw):
    users, employees, systems = [{},{},{}]
    for table in tables:
        bs = BeautifulSoup(table, features="html.parser")
        trs = bs.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) > 9:
                system = get_tag_text(tds[kw.get('system_index')])
                employee = get_tag_text(tds[kw.get('employee_index')])
                user = get_tag_text(tds[kw.get('user_index')])
                users[user] = users.get(user, 0) + 1
                employees[employee] = employees.get(employee, 0) + 1
                systems[system] = systems.get(system, 0) + 1
    return [users, employees, systems]

def get_tag_text(tag):
    t = 'Não atríbuido' if tag.text == '' else next(tag.strings).strip()
    t = t[0:t.find('(') - 1].title() if t.find('(') > 0 else t.title()
    t = t[0:t.find('>') - 1].title() if t.find('>') > 0 else t
    return t[t.find('-') + 2:].title() if t.find('-') > 0 else t

def glpi_totals(old_glpi_totals, new_glpi_totals):
    totals = []
    for i,d in enumerate(old_glpi_totals):
        totals.append(get_totals(old_glpi_totals[i], new_glpi_totals[i]))
    return totals

def get_totals(old_glpi_dict, new_glpi_dict):
    keys = set(list(new_glpi_dict.keys()) + list(old_glpi_dict.keys()))
    return {k:(old_glpi_dict.get(k, 0) + new_glpi_dict.get(k, 0)) for k in keys}

if __name__ == '__main__':
    pass
