import unittest
from unittest.mock import MagicMock, patch
# Add other imports here if needed
import Calendar
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']


class CalendarTest(unittest.TestCase):

    @patch('Calendar.get_calendar_api')
    # This test tests number of upcoming events.
    def test_get_upcoming_events_number(self, mock_api):
        mock_api.return_value = MagicMock(build)
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
    def test_edit_events(self):
        mock_api = MagicMock()
        time = MagicMock()

        # Simulate retrieving all events
        events = Calendar.get_all_events(mock_api, time)
        mock_api.events.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "id": "ABCDEFIGHIT",
                    "summary": "test",
                    "start": {
                        "dateTime": "2019-06-03T02:00:00+09:00"
                    },
                    "end": {
                        "dateTime": "2019-06-03T02:45:00+09:00"
                    },
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
                },
            ]
        }

        # get_all_events is tested in a different method. no need to test again

        # Set the return values for events
        events = mock_api.events().list().execute()["items"]
        option = 1
        change = 'I made changes to this event'
        Calendar.edit_event(mock_api, events[option-1]['id'], change, False)

        # Predict the changed events
        predicted_event = events[option-1]

        # Check if the function is called:
        args, kwargs = mock_api.events.return_value.update.call_args_list[0]
        self.assertEqual(kwargs['eventId'], predicted_event['id'])

        # If updated, update the events
        events[option-1]["summary"] = change

        event = events[option-1]

        self.assertEqual(change, event['summary'])

        # Delete the event after finishing
        Calendar.delete_event(mock_api, event['id'])

    def test_delete_events(self):
        """
        This test deletes an event and check if it is still on the calender.
        """
        mock_api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()

        a_event = mock_api.events().quickAdd(
            calendarId='primary',
            text='Appointment at Somewhere on June 3rd 10am-10:25am').execute()

        """
        a_event structure
        
        a_event = {
            "kind": 'calendar#event',
            "etag": ""3205424328208000"",
            "id": "f4aa09cj3b0srnas27pdv6af40", (Randomized)
            "status": "confirmed",
            "htmlLink": 'https://www.google.com/calendar/event?eid=ZjRhYTA5Y2ozYjBzcm5hczI3cGR2NmFmNDAgbXNoYTAwNDZAc3R1ZGVudC5tb25hc2guZWR1'
            "created": '2020-10-14T07:56:04.000Z',
            'updated': '2020-10-14T07:56:04.104Z',
            'summary': 'Appointment at Somewhere'
            'location': "Somewhere",
            creator: {
                'email' : 'abcdeg@gmail.com'
                'self': True
            },
            'organizer: {
                'email' : 'abcdeg@gmail.com'
                'self': True
            },
            'start': {'dateTime': '2021-06-03T10:00:00+08:00'},
            'end': {'dateTime': '2021-06-03T10:25:00+08:00'},
            'iCalUID': 'f4aa09cj3b0srnas27pdv6af40@google.com'
            'sequence': 0
            'reminders' = {'useDefault': True}
            
        """

        Calendar.delete_event(mock_api, a_event['id'])
        """
        After the deletion of an event, gets the updated events from the calender.
        Searches if the deleted event is still on the calender
        """
        updated_events = Calendar.get_all_events(mock_api, time_now)
        for event in updated_events:
            self.assertNotEqual(a_event['id'], event['id'])

    def test_cancel_events(self):
        """
        This test cancels an event and check if its status is cancelled.
        """
        mock_api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()

        a_event = mock_api.events().quickAdd(
            calendarId='primary',
            text='A changed event at Somewhere on June 3rd 10am-10:25am').execute()

        Calendar.cancel_event(mock_api, a_event['id'])

        updated_events = Calendar.get_all_events(mock_api, time_now)
        changed_event = mock_api.events().get(calendarId='primary', eventId=a_event['id']).execute()

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


def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(CalendarTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=2).run(suite)


main()
