import time
import pytz
import requests
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from dateutil.rrule import rrulestr
from dotenv import load_dotenv
import os

TZ = pytz.timezone('Europe/Athens')

load_dotenv()

from roufianomore import main

def get_calendar_events(ical_url):
    response = requests.get(ical_url)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.text)
    return calendar

def get_recurrences_from_event(event, start_date, end_date):
    if not 'RRULE' in event:
        return []
    
    dtstart = event.get('DTSTART').dt.astimezone(TZ)
    rule = rrulestr(event['RRULE'].to_ical().decode(), dtstart=dtstart)
    return [dt for dt in rule.between(start_date, end_date)]

def get_non_recurrences_from_event(event, start_date, end_date):
    dtstart = event.get('DTSTART').dt.astimezone(TZ)
    return [dtstart] if 'DTSTART' in event and start_date <= dtstart < end_date else []

def get_todays_events(calendar):
    today = datetime.now().astimezone(TZ)
    tommorow = today + timedelta(days=1)
    tommorow = tommorow.replace(hour=0, minute=0, second=1, microsecond=0)

    today_checkin = None
    today_checkout = None

    for component in calendar.walk():
        if component.name == "VEVENT":
            recurrences = get_recurrences_from_event(component, today, tommorow)
            non_recurrences = get_non_recurrences_from_event(component, today, tommorow)

            for occurrence in recurrences + non_recurrences:
                if 'EXDATE' in component and occurrence.date() in component['EXDATE']:
                    continue
                
                event = Event()
                event.add('DTSTART', occurrence)
                event.add('DTEND', occurrence + (component.decoded('DTEND') - component.decoded('DTSTART')))
                event.add('SUMMARY', component.get('SUMMARY'))
                
                if today.date() == occurrence.date():
                    summary_lower = event.get('SUMMARY', '').lower()
                    if summary_lower == "checkin":
                        today_checkin = event
                    elif summary_lower == "checkout":
                        today_checkout = event

    return today_checkin, today_checkout

def wait_and_trigger(event, check_type):
    if event:
        current_time = event.get('DTSTART').dt
        wait_time = (current_time - datetime.utcnow().astimezone(TZ)).total_seconds()
        
        if wait_time > 0:
            time.sleep(wait_time)
            main(check_type)
        else:
            print(f"{check_type} event passed.")
    else:
        print("Event doesn't exist.")

if __name__ == "__main__":
    ical_url = os.getenv("GOOGLE_CALENDAR_URL")
    calendar = get_calendar_events(ical_url)

    today_checkin, today_checkout = get_todays_events(calendar)

    print(today_checkin, today_checkout)

    wait_and_trigger(today_checkin, "Checkin")
    wait_and_trigger(today_checkout, "Checkout")
