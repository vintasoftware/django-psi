# django
from django.test import TestCase

from .. import formatters


class FormattersTestCase(TestCase):
    def setUp(self):
        pass

    def test_format_report_group_slack_message_json(self):
        slack_message = formatters.format_report_group_slack_message_json(None)

        self.assertEqual(slack_message, None)
