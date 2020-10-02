# Make sure you are logged into your Monash student account.
# Go to: https://developers.google.com/calendar/quickstart/python
# Click on "Enable the Google Calendar API"
# Configure your OAuth client - select "Desktop app", then proceed
# Click on "Download Client Configuration" to obtain a credential.json file
# Do not share your credential.json file with anybody else, and do not commit it to your A2 git repository.
# When app is run for the first time, you will need to sign in using your Monash student account.
# Allow the "View your calendars" permission request.


# Students must have their own api key
# No test cases needed for authentication, but authentication may required for running the app very first time.
# http://googleapis.github.io/google-api-python-client/docs/dyn/calendar_v3.html


# Code adapted from https://developers.google.com/calendar/quickstart/python
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']


def get_calendar_api():
    """
    Get an object which allows you to consume the Google Calendar API.
    You do not need to worry about what this function exactly does, nor create test cases for it.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_upcoming_events(api, starting_time, number_of_events, time_Max, key_Word):
    """
    get_upcoming_events(api, starting_time, number_of_events)

    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next n events on the user's calendar.

    @param api: The build generated in get_calendar_api() function
    @type api: googleapiclient.discovery.build
    @param starting_time: The starting date/time for the event to be included. In UTC time
    @type starting_time: string in UTC format (YYYY-MM-DDT*HH:MM:SS), T* is separator between time and date
    @param number_of_events: maximum number of events to be printed
    @type number_of_events: Integer
    """

    if number_of_events <= 0:
        raise ValueError("Number of events must be at least 1.")

    events_result = api.events().list(calendarId='primary', timeMin=starting_time, timeMax=time_Max,
                                      maxResults=number_of_events, singleEvents=True, q=key_Word,
                                      orderBy='startTime').execute()
    return events_result.get('items', [])


# Add your methods here.
def sub_five_years(time_now: int) -> datetime:
    """
    Return the time 5 years before the current time recorded on the user's device to identify the appropriate time
    span of the events to be listed.

    @param time_now: The current time recorded on the user's devices
    @type time_now: datetime class object. Formatted for use in get_upcoming_events
    @return: The time 5 years before the current time
    """
    # Solution from https://stackoverflow.com/questions/5158160/python-get-datetime-for-3-years-ago-today
    num_years = 5
    return time_now.replace(time_now.year - num_years).isoformat() + 'Z'  # 'Z' indicates UTC time


def add_two_years(time_now: int) -> datetime:
    """
    Return the time 2 years after the current time recorded on the user's device to identify the appropriate time
    span of the events to be listed.

    @param time_now: The current time recorded on the user's devices
    @type time_now: datetime class object. Formatted for use in get_upcoming_events
    @return: The time 5 years before the current time
    """
    # Solution from https://stackoverflow.com/questions/5158160/python-get-datetime-for-3-years-ago-today
    num_years = 2
    return time_now.replace(time_now.year + num_years).isoformat() + 'Z'  # 'Z' indicates UTC time


def delete_event(api, event_id):
    """
        Deletes a given event by its correspodning event id

        @param api: The build generated in get_calendar_api() function
        @type api: googleapiclient.discovery.build
        @param event_id: The id corresponding to the a specific event
        @type event_id: String
        @return: No return
        """
    api.events().delete(calendarId='primary', eventId=event_id).execute()


def edit_event(api, event_id, summary):
    """
        updates a given event by its corresponding event id

        @param api: The build generated in get_calendar_api() function
        @type api: googleapiclient.discovery.build
        @param event_id: The id corresponding to the a specific event
        @type event_id: String
        @return: No return
    """
    event = api.events().get(calendarId='primary', eventId='eventId').execute()

    event['summary'] = summary

    api.events().update(calendarId='primary', eventId=event_id, body=event)


# Main Menu Function
def print_menu() -> None:
    """
    Display menu to be used to guide user to use

    :pre: Console is blank
    :Post: Console displays the list of user Items
    :Complexity: O(1)
    """
    print("\nMenu:")
    print("1. Show all events")
    print("2. Search for events")
    print("3. Delete events")
    print("4. Edit events")
    print("5. Cancel events")
    print("6. Quit")


def get_all_events(api, time_now):
    """
    Retrieve all events between 5 years ago and 2 years from now

    @param api: Api for calendar (Google) used by the user
    @type api:  googleapiclient.discovery.build
    @param time_now: The current time in utc format
    @type time_now: datetime class object
    @return: void: Will print all events
    """
    # starting_time is formatted as (YYYY-MM-DDT*HH:MM:SS), T* is separator between time and date
    starting_time = sub_five_years(time_now)
    end_time = add_two_years(time_now)
    key_word = ""

    events = get_upcoming_events(api, starting_time, 10, end_time, key_word)
    return events


def search_all_events(api, time_now, key_word):
    """
    Retrieve all events between 5 years ago and 2 years from now with specific key_word

    @param api: Api for calendar (Google) used by the user
    @type api:  googleapiclient.discovery.build
    @param time_now: The current time in utc format
    @type time_now: datetime class object
    @param key_word: Events with this key word will be returned
    @type key_word: String
    @return: void: Will print all events
    """
    # starting_time is formatted as (YYYY-MM-DDT*HH:MM:SS), T* is separator between time and date
    starting_time = sub_five_years(time_now)
    end_time = add_two_years(time_now)

    events = get_upcoming_events(api, starting_time, 10, end_time, key_word)

    return events


def cancel_event(api, event_id):
    """
           updates a given event by its corresponding event id

           @param api: The build generated in get_calendar_api() function
           @type api: googleapiclient.discovery.build
           @param event_id: The id corresponding to the a specific event
           @type event_id: String
           @return: No return
       """
    event = api.events().get(calendarId='primary', eventId=event_id).execute()

    event['status'] = "cancelled"

    api.events().update(calendarId='primary', eventId=event_id, body=event).execute()


def print_events(events):
    if not events:
        print('No upcoming events found.')
    num = 1
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(num, start, event['summary'])
        # print(event["id"])
        num += 1


def main():
    api = get_calendar_api()
    time_now = datetime.datetime.utcnow()

    # Show the main menu:
    user_exit = False
    # Global events variable
    events = []
    while not user_exit:
        print_menu()
        user_input = int(input("Input option: "))
        if user_input == 1:
            events = get_all_events(api, time_now)
            print_events(events)
        elif user_input == 2:
            key_word = input("Key words for event: ")
            events = search_all_events(api, time_now, key_word)
            print_events(events)
        elif user_input == 3:
            event_id = int(input("Select event to delete: "))
            if (events == []) or (event_id < 1) or (event_id > len(events)):
                print("Invalid input")
                continue
            else:
                # print(events[event_id - 1]["id"])
                delete_event(api, events[event_id - 1]["id"])
                events = get_all_events(api, time_now)
                print_events(events)
        elif user_input == 4:
            event_id = int(input("Select event to edit: "))
            summary = int(input("Enter your summary message: "))
            if (events == []) or (event_id < 1) or (event_id > len(events)):
                print("Invalid input")
                continue
            else:
                # print(events[event_id - 1]["id"])
                edit_event(api, events[event_id - 1]["id"], summary)
        elif user_input == 5:
            event_id = int(input("Select event to canceled: "))
            if (events == []) or (event_id < 1) or (event_id > len(events)):
                print("Invalid input")
                continue
            else:
                # print(events[event_id - 1]["id"])
                cancel_event(api, events[event_id - 1]["id"])
                print("Event has been cancelled")
        elif user_input == 6:
            user_exit = True
        # print(events)


if __name__ == "__main__":  # Prevents the main() function from being called by the test suite runner
    main()
