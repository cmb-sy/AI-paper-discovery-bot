import unittest
from src.services.notifier import Notifier

class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.notifier = Notifier()

    def test_send_notification_success(self):
        # Mock data for testing
        paper_info = {
            'title': 'Sample Paper Title',
            'authors': ['Author One', 'Author Two'],
            'summary': 'This is a sample summary of the paper.'
        }
        response = self.notifier.send_notification(paper_info)
        self.assertTrue(response['ok'])  # Assuming the response has an 'ok' field

    def test_send_notification_failure(self):
        # Mock data for testing
        paper_info = {
            'title': 'Sample Paper Title',
            'authors': ['Author One', 'Author Two'],
            'summary': 'This is a sample summary of the paper.'
        }
        # Simulate a failure in sending notification
        self.notifier.slack_api.send_message = lambda *args, **kwargs: {'ok': False}
        response = self.notifier.send_notification(paper_info)
        self.assertFalse(response['ok'])

if __name__ == '__main__':
    unittest.main()