# Roufianomore
**_An automation script for Erganis check-in/check-out "roufianos" system._**

Automate your daily check-in and check-out in Erganis. This script monitors your Google Calendar events for the day and triggers actions on the Erganis platform accordingly.

> **Current Status**
> 
> [![Schedule Check-in/Check-out](https://github.com/patriarxis/roufianomore/actions/workflows/main.yml/badge.svg)](https://github.com/patriarxis/roufianomore/actions/workflows/main.yml)

## Table of Contents

- [Overview](#overview)
- [Usage](#usage)
- [Contributing](#contributing)
- [Donate](#donate)
- [License](#license)

## Overview

**Roufianomore** is a python script that is designed to automate the process of checking in and out of Erganis system. This is the so called "roufianos", that is used to track the time arrivals and departures of employees from/to the office. A system that is outdated but is unfortunatelly still in use today, to help the bosses have a leverage on you. Due to its simplicity and lack of security measures, the script is able to login and check-in/check-out of the system successfully.

> **Breaking down the steps:**  
> 1. A [GitHub action](.github/workflows/main.yml) excecutes based on a cron schedule and runs the scripts.
> 2. The first script checks todays events in Google Calendar.
> 4. Stored events are put in a countdown timer until the event starts and the specified action is triggered
> 5. When the timer ends the event triggers the second script, which handles the requests.
> 6. It starts by fetching the login page and grabbing a verification token from an input in the login form, which is needed for the request.
> 7. Then it bundles the header and the payload, with the secret credentials and token, to send a post request to the login endpoint `https://ergani.softone.gr/Login/***?handler=Login`.
> 8. The server response is the home page, so the script parses it to find the next token needed for the check-in/check-out requests, again from an input in the form.
> 9. Fortunately, the request header and payload is the same for both check types and the request is sent to the appropriate endpoint, based on the check type `https://ergani.softone.gr/CheckIn/***?handler={check_type}`.
> 
> And that's it! The "roufianos" has completed successfully.

## Usage

Follow this process to get your own script automation up and running.

1. **Fork the repository**

1. **Setup Google Calendar URL:**
   - Create a Google Calendar that you want to monitor for check-in/check-out events.
   - Add events with subjects `Checkin` and `Checkout`.
     
     > **_Important Note:_**  
     > The actions will be excecuted at the start of the events.  
     > The only available event names are `Checkin` and `Checkout` and are not case sensitive.  
     > Only the first instance of each event category will be triggered per day.

   - Obtain your calendar's `Secret address in ICAL format` (located in the calendars settings)
   - Add it as a secret named `GOOGLE_CALENDAR_URL` in your GitHub repository.

2. **Set Credentials:**
   - Create GitHub secrets for your SoftOne platform credentials:
     - `COMPANY`: The Company you work for.
     - `USERNAME`: Your SoftOne username.
     - `PASSWORD`: Your SoftOne password.

3. **Update GitHub Action's Cron Schedule (Optional):**
   - The action is configured to run automatically every day at `6:00 AM UTC`. This schedule can be adjusted to your preferences by modifying the cron expression in the [GitHub Actions workflow file](.github/workflows/main.yml).
   
   ```yml
   # main.yml
   
   on:
     schedule:
       - cron: '0 6 * * *' # Min Hour DayOfTheMonth Month DayOfTheWeek
   ```

4. **Monitor Actions:**
   - Keep track of the script's execution by visiting the [GitHub Actions page](https://github.com/patriarxis/roufianomore/actions).

**Note:** Before relying on this automation, thoroughly review and understand the script's functionality. Ensure that the Google Calendar URL, SoftOne platform credentials, and schedule meet your specific requirements.

## Contributing

Contributions are welcome! If you encounter any issues or have improvements to suggest, feel free to open an issue or submit a pull request.

## Donate

> **Buy me a coffee**  
> If you find this script helpful and would like to support the project, consider buying me a coffee!  
> [revolut.me/patriarxis](https://revolut.me/patriarxis)
> 
> [![Buy Me a Coffee](https://patriarxis.com/assets/donate-button.svg)](https://revolut.me/patriarxis)

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the script according to your needs.
