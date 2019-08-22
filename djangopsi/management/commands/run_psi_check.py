import requests
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from apiclient.discovery import build
from django.conf import settings

from djangopsi.models import Environment, ReportGroup
from djangopsi.services.retrievers import get_all_project_urls_to_check, check_urls_in_pagespeed
from djangopsi.services.formatters import format_report_group_slack_message_json, print_report_group_console_report


logger = logging.getLogger(__name__)

PSI_GOOGLE_API_DEV_KEY = settings.PSI_GOOGLE_API_DEV_KEY


class Command(BaseCommand):
    help = 'Creates PageSpeed Insights reports for your django project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            action='store',
            dest='env',
            default='production',
            help='The environment where tests are going to be run',
        )

        parser.add_argument(
            '--strategy',
            action='store',
            dest='strategy',
            default='all',
            help='The strategy used to run',
        )
        
        parser.add_argument(
            '-c',
            '--console',
            action='store_true',
            dest='console',
            help='Output the results to the console',
        )

        parser.add_argument(
            '-k',
            '--keep',
            action='store_true',
            dest='keep',
            help='Saves the report to the database',
        )

        parser.add_argument(
            '--slack-message',
            action='store_true',
            dest='slack_message',
            default=False,
            help='Messages the user on Slack',
        )

        # parser.add_argument(
        #     '-v',
        #     '--verbose',
        #     action='store_true',
        #     dest='verbose',
        #     help='Runs in verbose mode',
        # )

    def _console_report(self, base_url, report_list, strategy):
        print_report_group_console_report(base_url, report_list, strategy)

    def _safety_check(self):
        # Check if there are production env settings
        if not (settings.PSI_ENVS['production'] or settings.PSI_ENVS['production']['base_url']):
            logger.error('FAIL AND EXIT')
            # raise Error

    def handle(self, *args, **options):
        # XXX TODO safety checks
        self._safety_check()

        self.stdout.write(self.style.SUCCESS('Pagespeed report started'))

        environment = 'production'
        if options['env']:
            environment = options['env']

        analysis_base_url = settings.PSI_ENVS[environment]['base_url']
        
        # Disable file cache based in
        # https://github.com/googleapis/google-api-python-client/issues/299
        psi_service = build(serviceName='pagespeedonline', version='v5', developerKey=PSI_GOOGLE_API_DEV_KEY, cache_discovery=False)
        
        urls_to_check = get_all_project_urls_to_check()
        
        url_reports = []
        if options['strategy'] != 'all':
            url_reports = check_urls_in_pagespeed(psi_service, urls_to_check, analysis_base_url, options['strategy'])
        else:
            url_reports += check_urls_in_pagespeed(psi_service, urls_to_check, analysis_base_url, 'mobile')
            url_reports += check_urls_in_pagespeed(psi_service, urls_to_check, analysis_base_url, 'desktop')

        if options['keep']:
            env, _ = Environment.objects.get_or_create(name=environment, base_url=analysis_base_url)
            report_group = ReportGroup.objects.create(environment=env)
            for report in url_reports:
                url, _ = env.urls.get_or_create(name=report['url']['name'], path=report['url']['path'])
                url.reports.create(
                    psi_id=report['psi_report']['psi_id'],
                    strategy=report['psi_report']['strategy'],
                    category=report['psi_report']['category'],
                    score=report['psi_report']['score'],
                    raw_data=report['psi_report']['raw_data'],
                    report_group=report_group
                )

        if options['console']:
            self._console_report(base_url=analysis_base_url, report_list=url_reports, strategy=options['strategy'])

        if options['slack_message']:
            requests.post(
                settings.PSI_SLACK_MESSAGE_HOOK,
                json=format_report_group_slack_message_json(report_group)
            )

