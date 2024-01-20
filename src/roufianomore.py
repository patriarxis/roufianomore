import requests
from bs4 import BeautifulSoup
import logging
from dotenv import load_dotenv
import os

load_dotenv()

LOGIN_URL = 'https://ergani.softone.gr/Login/flexcar'
LOGIN_URL_HANDLER = 'https://ergani.softone.gr/Login/flexcar?handler=Login'
CHECK_IN_OUT_URL = 'http://127.0.0.1:5000/CheckIn/flexcar'
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

logging.basicConfig(level=logging.INFO)

def login(session):
    lang_payload = {'SelectedLang': 'el'}
    
    header = {
        'Host': 'ergani.softone.gr',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
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
    }
    
    try:
        login_page_response = session.get(LOGIN_URL, headers=header, verify=False)
        login_page_response.raise_for_status()

        soup = BeautifulSoup(login_page_response.text, 'html.parser')
        anti_forgery_token = soup.find('input', {'name': '__RequestVerificationToken'}).get('value')
    except requests.RequestException as e:
        logging.error(f"Error during login page request: {e}")
        return False

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Content-Length': str(287),
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
        response = session.post(LOGIN_URL_HANDLER, data={**lang_payload, **credentials_payload}, headers=headers, verify=False)
        response.raise_for_status()

        # logging.info("Request Body: %s", response.request.body)
        # logging.info("Response Text: %s", response.text)
        return response.status_code == 200
    except requests.RequestException as e:
        logging.error(f"Error during login request: {e}")
        return False

def check_in_out(session, check_type):
    check_url = f"{CHECK_IN_OUT_URL}?handler={check_type}"
    
    try:
        response = session.post(check_url)
        response.raise_for_status()
        return response.status_code
    except requests.RequestException as e:
        logging.error(f"Error during check-in/out request: {e}")
        return False

def main(check_type):
    session = requests.Session()
    response = login(session)
    print(response)
    
    # if login(session):
    #     logging.info(f"Successfully logged in for {check_type} at {datetime.now()}")
    #     # Check in or out
    #     if check_in_out(session, check_type):
    #         logging.info(f"{check_type} successful!")
    #     else:
    #         logging.error(f"{check_type} failed!")
    # else:
    #     logging.error("Login failed!")
