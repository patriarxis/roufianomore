import requests
from bs4 import BeautifulSoup
import logging
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_URL = 'https://ergani.softone.gr/Login/flexcar'
LOGIN_URL_HANDLER = 'https://ergani.softone.gr/Login/flexcar?handler=Login'
CHECK_IN_OUT_URL = 'https://ergani.softone.gr/CheckIn/flexcar'
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
LANG_PAYLOAD = {'SelectedLang': 'el'}

logging.basicConfig(level=logging.INFO)

def login(session):
    login_page_headers = {
        'Host': 'ergani.softone.gr',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://ergani.softone.gr/Login/flexcar',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    }
    
    try:
        login_page_response = session.get(LOGIN_URL, headers=login_page_headers, verify=False)
        login_page_response.raise_for_status()

        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        anti_forgery_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    except requests.RequestException as e:
        logging.error(f"Error during login page request: {e}")
        return login_page_response

    login_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '; '.join([f'{name}={value}' for name, value in session.cookies.items()]),
        'DNT': '1',
        'Host': 'ergani.softone.gr',
        'Origin': 'https://ergani.softone.gr',
        'Referer': 'https://ergani.softone.gr/Login/flexcar',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    }
    
    credentials_payload = {
        'username': USERNAME,
        'password': PASSWORD,
        'SelectedLang': 'el',
        'HasSSO': False,
        'RedirectMode': '',
        '__RequestVerificationToken': anti_forgery_token,
    }
    
    try:
        response = session.post(LOGIN_URL_HANDLER, data={**LANG_PAYLOAD, **credentials_payload}, headers=login_headers, verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error during login request: {e}")
    return response

def check_in_out(session, check_type, token):
    check_url = f"{CHECK_IN_OUT_URL}?handler={check_type}"
    
    check_in_out_headers = {
        'Host': 'ergani.softone.gr',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://ergani.softone.gr/CheckIn/flexcar',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://ergani.softone.gr',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Cookie': '; '.join([f'{name}={value}' for name, value in session.cookies.items()]),
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
    }
    
    data_payload = {
        'TimezoneOffset': '-120',
        'Mode': '',
        '__RequestVerificationToken': token,
    }
    
    try:
        response = session.post(check_url, data={**LANG_PAYLOAD, **data_payload}, headers=check_in_out_headers, verify=False)
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as e:
        logging.error(f"Error during check-in/out request: {e}")
        return False

def main(check_type):
    session = requests.Session()
    login_response = login(session)
    
    print(login_response)
    
    if login_response.status_code == 200:
        soup = BeautifulSoup(login_response.text, 'html.parser')
        anti_forgery_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')

        if check_in_out(session, check_type, anti_forgery_token):
            logging.info(f"{check_type} successful!")
        else:
            logging.error(f"{check_type} failed!")
    else:
        logging.error("Login failed!")
