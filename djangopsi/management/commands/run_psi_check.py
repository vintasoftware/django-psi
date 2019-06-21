import requests
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from apiclient.discovery import build
from django.conf import settings

from djangopsi.services import get_all_project_urls_to_check, check_urls_in_pagespeed


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
            '-s',
            '--strategy',
            action='store',
            dest='strategy',
            default='desktop',
            help='The strategy used to run',
        )
        
        parser.add_argument(
            '-c',
            '--console',
            action='store_true',
            dest='console',
            help='Output the results to the console',
        )

        # parser.add_argument(
        #     '-v',
        #     '--verbose',
        #     action='store_true',
        #     dest='verbose',
        #     help='Runs in verbose mode',
        # )

    def _console_report(self, report_list, base_url, strategy):
        print("\n" + "PageSpeed Insights")
        print("--------------------------------------------\n")

        print("Statistics for {0}".format(base_url))
        print("Strategy used: {0}\n".format(strategy))

        for report in report_list:
            print("Name: {0}".format(report['url']['name']))
            print("----- path: {0}".format(report['url']['path']))
            if report['psi_report']:
                print("----- category: {0}".format(report['psi_report']['category']))
                print("----- score: {0}\n".format(report['psi_report']['score']))
            else:
                print("----- report failed")
            
        print("--------------------------------------------")
        print("\n")


    def _safety_check(self):
        # Check if there are production env settings
        if not (settings.PSI_ENVS['production'] or settings.PSI_ENVS['production']['base_url']):
            logger.error('FAIL AND EXIT')
            # raise Error


    def handle(self, *args, **options):
        # XXX TODO safety checks
        self._safety_check()

        self.stdout.write(self.style.SUCCESS('Pagespeed report started'))

        if options['env']:
            analysis_base_url = settings.PSI_ENVS[options['env']]['base_url']
        else:
            analysis_base_url = settings.PSI_ENVS['production']['base_url']
        
        # Disable file cache based in
        # https://github.com/googleapis/google-api-python-client/issues/299
        psi_service = build(serviceName='pagespeedonline', version='v5', developerKey=PSI_GOOGLE_API_DEV_KEY, cache_discovery=False)
        
        urls_to_check = get_all_project_urls_to_check()
        
        if options['strategy']:
            url_reports = check_urls_in_pagespeed(psi_service, urls_to_check, analysis_base_url, options['strategy'])
        else:
            url_reports = check_urls_in_pagespeed(psi_service, urls_to_check, analysis_base_url)

        if options['console']:
            self._console_report(report_list=url_reports, base_url=analysis_base_url, strategy=options['strategy'])

