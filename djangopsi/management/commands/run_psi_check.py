import requests
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.urls import reverse
from apiclient.discovery import build

logger = logging.getLogger(__name__)

root_urlconf = __import__(settings.ROOT_URLCONF)  # import root_urlconf module
all_urlpatterns = root_urlconf.urls.urlpatterns  # project's urlpatterns

PAGESPEED_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
PRODUCTION_URL = 'https://splendidspoon.com'

class Command(BaseCommand):
    help = 'Creates PageSpeed Insights reports for your django project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--env',
            action='store',
            dest='env',
            default='staging',
            help='The environment where tests are going to be run',
        )
        
        parser.add_argument(
            '-c',
            '--console',
            action='store_true',
            dest='console',
            help='Output the results to the console',
        )
    
    # As in: https://stackoverflow.com/questions/32933229
    # /how-to-get-a-list-of-all-views-in-a-django-application
    def _get_all_urls_to_check(self, urlpatterns, url_list=[]):
        for pattern in urlpatterns:
            if isinstance(pattern, RegexURLResolver):
                # call this function recursively
                self._get_all_urls_to_check(pattern.url_patterns, url_list)
            elif isinstance(pattern, RegexURLPattern):
                callback_func = pattern.callback
                if hasattr(callback_func, 'view_class') and \
                        hasattr(callback_func.view_class, 'is_psi_checked') and \
                        callback_func.view_class.is_psi_checked:
                    pattern_name = pattern.name
                    pattern_url = reverse(pattern.name)
                    url_list.append({'name': pattern_name, 'path': pattern_url})

        return url_list

    def _treat_pagespeed_response(self, response):

        status_code = response.status_code
        status = requests.status_codes._codes[status_code][0]

        data = response.json()
        id = data['id']
        category = data['loadingExperience']['overall_category']
        score = data['lighthouseResult']['categories']['performance']['score'] * 100

        return {
            'id': id,
            'status': status,
            'category': category,
            'score': score,
            'raw_data': data
        }

    def _run_pagespeed(self, url):
        logger.info('Checking url in pagespeed: {url}'.format(url=(PRODUCTION_URL + url)))
        r = requests.get(PAGESPEED_URL + '?url=' + PRODUCTION_URL + url)
        logger.info('Checking url done, status: {status_code}'.format(status_code=(r.status_code)))
        
        return self._treat_pagespeed_response(r)
        
    def _check_urls_pagespeed(self, urls):
        url_reports = []
        for url in urls:
            report = self._run_pagespeed(url['path'])
            url_reports.append({'url': url, 'report': report})

        return url_reports

    def _console_report(self, report_list):
        print("\n" + "PageSpeed Insights")
        print("--------------------------------------------\n")

        print("Statistics for {0}\n".format(PRODUCTION_URL))

        for report in report_list:
            print("Name: {0}".format(report['url']['name']))
            print("----- path: {0}".format(report['url']['path']))
            print("----- status: {0}".format(report['report']['status']))
            print("----- category: {0}".format(report['report']['category']))
            print("----- score: {0}\n".format(report['report']['score']))
            
        print("--------------------------------------------")
        print("\n")


    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Pagespeed report started'))
        urls_to_check = self._get_all_urls_to_check(all_urlpatterns)
        # service = build(serviceName='pagespeedonline', version='v5', developerKey=key)
        url_reports = self._check_urls_pagespeed(urls_to_check)

        if options['console']:
            self._console_report(url_reports)

