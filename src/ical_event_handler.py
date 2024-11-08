import time
import pytz
import requests
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from dateutil.rrule import rrulestr
from dotenv import load_dotenv
import os
from roufianomore import main

local_tz = pytz.timezone('Europe/Athens')
load_dotenv()

def get_calendar_events(ical_url):
    response = requests.get(ical_url)
    response.raise_for_status()
    calendar = Calendar.from_ical(response.text)
    return calendar

def get_recurrences_from_event(event, start_date, end_date):
    if not 'RRULE' in event:
        return []
    
    dtstart = event.get('DTSTART').dt.astimezone(local_tz)
    rule = rrulestr(event['RRULE'].to_ical().decode(), dtstart=dtstart)
    return [dt for dt in rule.between(start_date, end_date)]

def get_non_recurrences_from_event(event, start_date, end_date):
    dtstart = event.get('DTSTART').dt.astimezone(local_tz)
    return [dtstart] if 'DTSTART' in event and start_date <= dtstart < end_date else []

def is_occurrence_excluded(occurrence, exdates):
    exdate_list = exdates if isinstance(exdates, list) else [exdates]
    for exdate in exdate_list:
        exdate_str = exdate.to_ical().decode('utf-8')
        exdate_datetime = datetime.strptime(exdate_str, '%Y%m%dT%H%M%S')
        if occurrence.date() == exdate_datetime.date():
            return True
    return False

def get_todays_events(calendar):
    today = datetime.now().astimezone(local_tz)
    tommorow = today + timedelta(days=1)
    tommorow = tommorow.replace(hour=0, minute=0, second=1, microsecond=0)
    for component in calendar.walk():
        if component.name == "VEVENT":
            recurrences = get_recurrences_from_event(component, today, tommorow)
            non_recurrences = get_non_recurrences_from_event(component, today, tommorow)
            for occurrence in recurrences + non_recurrences:
                if 'EXDATE' in component and is_occurrence_excluded(occurrence, component['EXDATE']):
                    continue
                
                event = Event()
                event.add('DTSTART', occurrence.astimezone(local_tz))
                event.add('DTEND', (occurrence + (component.decoded('DTEND') - component.decoded('DTSTART'))).astimezone(local_tz))
                event.add('SUMMARY', component.get('SUMMARY'))
                
                if today.date() == occurrence.date():
                    summary_lower = event.get('SUMMARY', '').lower()
                    if summary_lower == "checkin":
                        return event, "Checkin"
                    elif summary_lower == "checkout":
                        return event, "Checkout"
    return None, None

def wait_and_trigger(event, check_type):
    if event:
        current_time = event.get('DTSTART').dt.astimezone(local_tz)
        wait_time = (current_time - datetime.now().astimezone(local_tz)).total_seconds()
        
        if wait_time > 0:
            print(event, check_type, wait_time)
            time.sleep(wait_time)
            main(check_type)
        else:
            print(f"{check_type} event passed.")
    else:
        print("Event doesn't exist.")

if __name__ == "__main__":
    ical_url = os.getenv("GOOGLE_CALENDAR_URL")
    calendar = get_calendar_events(ical_url)
    event, check_type = get_todays_events(calendar)
    if event and check_type:
        wait_and_trigger(event, check_type)
