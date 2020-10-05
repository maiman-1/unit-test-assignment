import unittest
from unittest.mock import Mock
# Add other imports here if needed
import Calendar
import datetime

class CalendarTest(unittest.TestCase):
    # This test tests number of upcoming events.
    def test_get_upcoming_events_number(self):
        num_events = 2
        time = "2020-08-03T00:00:00.000000Z"

        mock_api = Mock()
        events = Calendar.get_upcoming_events(mock_api, time, num_events)

        self.assertEqual(
            mock_api.events.return_value.list.return_value.execute.return_value.get.call_count, 1)

        args, kwargs = mock_api.events.return_value.list.call_args_list[0]
        self.assertEqual(kwargs['maxResults'], num_events)

    # Add more test cases here
    def test_edit_events(self):
        api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()
        option = 6

        events = Calendar.get_all_events(api, time_now)
        Calendar.edit_event(api, events[option - 1]['id'], 'I made changes to this event')
        self.assertEqual(
            'I made changes to this event', events[option - 1]['summary'])

    def test_delete_events(self):
        """
        This test deletes an event and check if it is still on the calender.
        """
        api = Calendar.get_calendar_api()
        time_now = datetime.datetime.utcnow()
        option = 7

        events = Calendar.get_all_events(api, time_now)
        deleted_Event = events[option - 1]['id']
        Calendar.delete_event(api, events[option - 1]['id'])
        """
        After the deletion of an event, gets the updated events from the calender.
        Searches if the deleted event is still on the calender
        """
        updated_events = Calendar.get_all_events(api, time_now)
        for event in updated_events:
            self.assertNotEqual(deleted_Event, event['id'])

def main():
    # Create the test suite from the cases above.
    suite = unittest.TestLoader().loadTestsFromTestCase(CalendarTest)
    # This will run the test suite.
    unittest.TextTestRunner(verbosity=2).run(suite)


main()
