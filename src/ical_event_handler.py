import time
import arrow
from ics import Calendar
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

from roufianomore import main

def get_calendar_events(ical_url):
    response = requests.get(ical_url)
    response.raise_for_status()
    calendar = Calendar(response.text)
    return calendar.events

def get_today_events():
    ical_url = os.getenv("GOOGLE_CALENDAR_URL")
    events = get_calendar_events(ical_url)
    
    today = datetime.now().date()
    
    today_checkin = None
    today_checkout = None

    print(events)

    for event in events:
        if today == event.begin.date() and event.name.lower() == "checkin":
            today_checkin = event
        elif today == event.begin.date() and event.name.lower() == "checkout":
            today_checkout = event

    return today_checkin, today_checkout

def wait_and_trigger(event, check_type):
    if event:
        current_time = arrow.now(event.begin.tzinfo)
        wait_time = (event.begin - current_time).total_seconds()
        if wait_time > 0:
            time.sleep(wait_time)
            main(check_type)
        else:
            print(f"{check_type} event passed.")
    else:
        print("No events found for today.")

if __name__ == "__main__":
    today_checkin, today_checkout = get_today_events()
    
    wait_and_trigger(today_checkin, "Checkin")
    wait_and_trigger(today_checkout, "Checkout")
