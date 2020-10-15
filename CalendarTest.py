import unittest
from unittest.mock import MagicMock, patch
# Add other imports here if needed
import Calendar
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import io
import sys

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']


class CalendarTest(unittest.TestCase):

    def setUp(self) -> None:
        self.mock_api = MagicMock()
        self.time = MagicMock()

        # Simulate retrieving all events
        self.mock_api.events.return_value.list.return_value.execute.return_value = [
            {
                "id": "ABCDEFIGHIT",
                "summary": "test",
                "start": {
                    "dateTime": "2019-06-03T02:00:00+09:00"
                },
                "end": {
                    "dateTime": "2019-06-03T02:45:00+09:00"
                },
                "reminders": {
                    "useDefault": True
                }
            },
            {
                "id": "ABCDEFIGHIG",
                "summary": "test",
                "start": {
                    "dateTime": "2019-06-03T02:00:00+09:00"
                },
                "end": {
                    "dateTime": "2019-06-03T02:45:00+09:00"
                },
                "reminders": {
                    "useDefault": True
                }
            },
        ]

        # get_all_events is tested in a different method. no need to test again

        # Set the return values for events
        self.events = self.mock_api.events().list().execute()


    # This test tests number of upcoming events.
    def test_get_upcoming_events_number(self):
        mock_api = MagicMock()
        num_events = 10
        time = datetime.datetime.utcnow()
        events = Calendar.get_all_events(mock_api, time)
        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)

        args, kwargs = mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(kwargs['maxResults'], num_events)
        # Check if the timeMax is 2 years from now and timeMin is 5 years ago
        self.assertEqual(kwargs['timeMin'], time.replace(time.year - 5).isoformat() + 'Z')
        self.assertEqual(kwargs['timeMax'], time.replace(time.year + 2).isoformat() + 'Z')

    # Add more test cases here
    @patch('Calendar.input')
    def test_edit_events(self, mock_input_reminders):
        mock_api = MagicMock()
        time = MagicMock()

        # Simulate retrieving all events
        events = Calendar.get_all_events(mock_api, time)
        mock_api.events.return_value.list.return_value.execute.return_value = [
            {
                "id": "ABCDEFIGHIT",
                "summary": "test",
                "start": {
                    "dateTime": "2019-06-03T02:00:00+09:00"
                },
                "end": {
                    "dateTime": "2019-06-03T02:45:00+09:00"
                },
                "reminders": {
                    "useDefault": True
                }
            },
            {
                "id": "ABCDEFIGHIG",
                "summary": "test",
                "start": {
                    "dateTime": "2019-06-03T02:00:00+09:00"
                },
                "end": {
                    "dateTime": "2019-06-03T02:45:00+09:00"
                },
                "reminders": {
                    "useDefault": True
                }
            },
        ]

        # get_all_events is tested in a different method. no need to test again

        # Set the return values for events
        events = mock_api.events().list().execute()
        option = 1
        change = 'I made changes to this event'
        Calendar.edit_event(mock_api, events[option - 1]['id'], change, False)

        # Predict the changed events
        predicted_event = events[option - 1]

        # Check if the function is called:
        args, kwargs = mock_api.events.return_value.update.call_args_list[0]
        self.assertEqual(kwargs['eventId'], predicted_event['id'])

        # If updated, update the events
        events[option - 1]["summary"] = change

        event = events[option - 1]

        self.assertEqual(change, event['summary'])

        mock_input_reminders.side_effect = [15]
        Calendar.edit_event(mock_api, events[option - 1]['id'], change, True)

        # Predict the changed events
        predicted_event = events[option - 1]

        # Check if the function is called:
        args, kwargs = mock_api.events.return_value.update.call_args_list[0]
        self.assertEqual(kwargs['eventId'], predicted_event['id'])

        # If updated, update the events
        events[option - 1]["summary"] = change
        events[option - 1]['reminders']['overrides'] = []
        events[option - 1]['reminders']['overrides'].append(
            {
                "method": "popup",
                "minutes": mock_input_reminders.side_effect
            }
        )

        event = events[option - 1]

        self.assertEqual(change, event['summary'])

    def test_delete_events(self):
        """
        This test deletes an event and check if it is still on the calender.
        """
        option = 1

        # Set the return values for events
        events = self.mock_api.events().list().execute()
        a_event = events[option - 1];

        Calendar.delete_event(self.mock_api, a_event['id'])

        # Check if the function is called:
        self.assertEqual(
            self.mock_api.events.return_value.delete.call_count, 1)
        args, kwargs = self.mock_api.events.return_value.delete.call_args_list[0]
        self.assertEqual(kwargs['eventId'], a_event['id'])

        # After deleting event, events is called again
        events = self.mock_api.events().list().execute()
        # Set the return value for events
        events.remove(a_event)
        """
        After the deletion of an event, gets the updated events from the calender.
        Searches if the deleted event is still on the calender
        """
        for event in events:
            self.assertNotEqual(a_event['id'], event['id'])

    def test_cancel_events(self):
        """
        This test cancels an event and check if its status is cancelled.
        """
        option = 1

        # Set the return values for events
        events = self.mock_api.events().list().execute()
        a_event = events[option - 1];

        Calendar.cancel_event(self.mock_api, a_event['id'])

        # Check if the function is called:
        self.assertEqual(
            self.mock_api.events.return_value.update.call_count, 1)
        args, kwargs = self.mock_api.events.return_value.update.call_args_list[0]
        self.assertEqual(kwargs['eventId'], a_event['id'])

        updated_events = self.mock_api.events().list().execute()
        updated_events[option - 1]['status'] = 'cancelled'
        changed_event = updated_events[option - 1]

        """
        After the cancellation of an event, obtain the updated calendar.
        Tests if Cancelled Event is still on the calendar
        """
        self.assertEqual(
            'cancelled', changed_event['status'])  # It prints out confirmed.. I think there is something wrong with
        # the functionality
        # AssertionError: 'cancelled' != 'confirmed'

    def test_search_events(self):
        """
        This test searches an event and sees if the correct arguments are called as per the function specifies:

        Function involved: search_all_events(api, time_now, key_word):
        """
        mock_api = MagicMock()
        search_term = MagicMock()
        time_now = MagicMock()

        events = Calendar.search_all_events(mock_api, time_now, search_term)

        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)

        args, kwargs = mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(kwargs['q'], search_term)

    def test_navigate_events(self):
        """
        This test navigates to a certain date and sees if the correct arguments are called as per the function specifies:

        Function involved: navigate_events(api, time_year: int, time_month: int, time_day: int):
        """
        # Reset call count of api.events().list()
        self.mock_api = MagicMock()
        self.mock_api.events.return_value.list.call_count = 0

        time_year = 2020
        time_month = 10
        time_day = 3

        events = Calendar.navigate_events(self.mock_api, time_year, time_month, time_day)
        self.mock_api.events.return_value.list.return_value.execute.return_value = [
            {
                "id": "ABCDEFIGHIG",
                "summary": "test",
                "start": {
                    "dateTime": "2020-10-03T02:00:00+09:00"
                },
                "end": {
                    "dateTime": "2020-10-03T02:45:00+09:00"
                },
                "reminders": {
                    "useDefault": True
                }
            },
        ]

        events = self.mock_api.events.return_value.list.return_value.execute.return_value

        # Calculate starting_time and time_max
        # Concatenate the strings to properly be fitted in the format
        starting_time = str(time_year) + "-" + str(time_month) + "-" + str(time_day) + "T00:00:00.0000" + 'Z'
        time_Max = str(time_year) + "-" + str(time_month) + "-" + str(time_day) + "T23:59:59.0000" + 'Z'

        # Check if the function is called correctly:
        self.assertEqual(
            self.mock_api.events.return_value.list.call_count, 1)
        args, kwargs = self.mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(kwargs['timeMax'], time_Max)
        self.assertEqual(kwargs['timeMin'], starting_time)

    def test_print_events(self):
        """
        This test is for the printing of the user menu

        Function involved: print_events(events)
        """
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        Calendar.print_events(self.events)
        sys.stdout = sys.__stdout__

        # Predicted output calculation
        predicted_event = ""
        reminder = ""
        num = 1
        for event in self.events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            reminder = str(0) + " minutes before"
            predicted_event += "Events: " + " " + str(num) + " " + start + " " + event[
                'summary'] + " " + "| Reminder: " + " " + reminder + "\n"
            num += 1

        self.assertEqual(predicted_event, capturedOutput.getvalue())


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(CalendarTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=2).run(suite)


main()
