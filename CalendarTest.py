import unittest
from unittest.mock import Mock
# Add other imports here if needed
import Calendar
import datetime


class CalendarTest(unittest.TestCase):
    # This test tests number of upcoming events.
    def test_get_upcoming_events_number(self):
        num_events = 10
        time = datetime.datetime.utcnow()
        mock_api = Mock()
        events = Calendar.get_all_events(mock_api, time)
        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)

        args, kwargs = mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(kwargs['maxResults'], num_events)

    # Add more test cases here
    def test_edit_events(self):
        mock_api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()
        option = 6

        events = Calendar.get_all_events(mock_api, time_now)
        Calendar.edit_event(mock_api, events[option - 1]['id'], 'I made changes to this event')
        # print(events[option - 1]['summary'])
        self.assertEqual(
            'I made changes to this event', events[option - 1]['summary'])

    def test_delete_events(self):
        """
        This test deletes an event and check if it is still on the calender.
        """
        mock_api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()
        option = 7

        events = Calendar.get_all_events(mock_api, time_now)

        deleted_Event = events[option - 1]['id']
        Calendar.delete_event(mock_api, events[option - 1]['id'])
        """
        After the deletion of an event, gets the updated events from the calender.
        Searches if the deleted event is still on the calender
        """
        updated_events = Calendar.get_all_events(mock_api, time_now)
        for event in updated_events:
            self.assertNotEqual(deleted_Event, event['id'])

    def test_cancel_events(self):
        """
        This test cancels an event and check if its status is cancelled.
        """
        mock_api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()
        option = 2

        events = Calendar.get_all_events(mock_api, time_now)

        canceled_event = events[option - 1]
        canceled_event_id = events[option - 1]['id']
        Calendar.cancel_event(mock_api, canceled_event_id)

        """
        After the cancellation of an event, obtain the updated calendar.
        Tests if Cancelled Event is still on the calendar
        """
        self.assertEqual(
            'cancelled', canceled_event['status'])  # It prints out confirmed.. I think there is something wrong with
        # the functionality
        # AssertionError: 'cancelled' != 'confirmed'

def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(CalendarTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=2).run(suite)


main()
