# stdlib
import sys
from io import StringIO

from django.test import TestCase

from djangopsi.models import Environment, Report, ReportGroup, Url
from djangopsi.services.formatters import (
    format_report_group_slack_message_json,
    print_report_group_console_report,
)


class DisablePrint:
    def __enter__(self):
        result = StringIO()
        sys.stdout = result

    def __exit__(self, a, b, c):
        sys.stdout = sys.__stdout__


class FormattersTestCase(TestCase):
    def setUp(self):
        self.env = Environment.objects.create(
            name="production", base_url="http://example.com"
        )
        url_1 = Url.objects.create(name="home", path="/", environment=self.env)
        url_2 = Url.objects.create(
            name="contact", path="/contact", environment=self.env
        )

        self.report_group = ReportGroup.objects.create(environment=self.env)

        self.report_1 = Report.objects.create(
            psi_id="report1",
            strategy="mobile",
            category="SLOW",
            score="90",
            raw_data="{}",
            url=url_1,
            report_group=self.report_group,
        )
        self.report_2 = Report.objects.create(
            psi_id="report2",
            strategy="mobile",
            category="SLOW",
            score="90",
            raw_data="{}",
            url=url_2,
            report_group=self.report_group,
        )
        self.report_3 = Report.objects.create(
            psi_id="report3",
            strategy="desktop",
            category="FAST",
            score="100",
            raw_data="{}",
            url=url_1,
            report_group=self.report_group,
        )
        self.report_4 = Report.objects.create(
            psi_id="report4",
            strategy="desktop",
            category="FAST",
            score="100",
            raw_data="{}",
            url=url_2,
            report_group=self.report_group,
        )

    def test_format_report_group_slack_message_json(self):
        formatted_message = format_report_group_slack_message_json(self.report_group)

        self.assertIn("Mobile score average: 90", formatted_message["text"])
        self.assertIn("Desktop score average: 100", formatted_message["text"])
        self.assertIn(
            "your app hosted at:\r\n" + self.report_group.environment.base_url,
            formatted_message["text"],
        )

    def test_print_report_group_console_report(self):
        with DisablePrint():
            print_report_group_console_report(
                base_url=self.env.base_url,
                report_list=[
                    {
                        "url": self.report_1.url.__dict__,
                        "psi_report": self.report_1.__dict__,
                    }
                ],
                strategy="all",
            )
            result_string = sys.stdout.getvalue()

        self.assertIn("Statistics for " + self.env.base_url, result_string)
        self.assertIn("Strategy used: all", result_string)
