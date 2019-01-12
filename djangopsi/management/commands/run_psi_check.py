import requests
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.urls import reverse
from apiclient.discovery import build
from django.conf import settings

logger = logging.getLogger(__name__)

root_urlconf = __import__(settings.ROOT_URLCONF)  # import root_urlconf module
all_urlpatterns = root_urlconf.urls.urlpatterns  # project's urlpatterns

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
        report = False

        id = response['id']
        category = response['loadingExperience'].get('overall_category', '-')
        score = response['lighthouseResult']['categories']['performance']['score'] * 100

        report = {
            'id': id,
            'category': category,
            'score': score,
            'raw_data': response
        }

        return report

    def _run_pagespeed(self, path):
        url_to_check = self._analysis_base_url + path
        logger.info('Analyzing url in pagespeed: {url}'.format(url=url_to_check))

        analysis_result = False
        try:
            r = self.service.pagespeedapi().runpagespeed(url=url_to_check, strategy='desktop').execute()
        except:
            logger.error('There was an error analyzing this url.')

        if r:
            logger.info('Done. Analysis made successfuly.')
            analysis_result = self._treat_pagespeed_response(r)
        
        return analysis_result
        
    def _check_urls_pagespeed(self, urls):
        url_reports = []
        for url in urls:
            report = self._run_pagespeed(url['path'])
            if report:
                url_reports.append({'url': url, 'report': report})

        return url_reports

    def _console_report(self, report_list):
        print("\n" + "PageSpeed Insights")
        print("--------------------------------------------\n")

        print("Statistics for {0}\n".format(self._analysis_base_url))

        for report in report_list:
            print("Name: {0}".format(report['url']['name']))
            print("----- path: {0}".format(report['url']['path']))
            print("----- status: {0}".format(report['report']['status']))
            print("----- category: {0}".format(report['report']['category']))
            print("----- score: {0}\n".format(report['report']['score']))
            
        print("--------------------------------------------")
        print("\n")


    def _safety_check(self):

        # Check if there are production env settings
        if not settings.PSI_ENVS['production']['base_url']:
            logger.error('FAIL AND EXIT')


    def handle(self, *args, **options):
        # XXX TODO safety checks
        # self._safety_check()

        self.stdout.write(self.style.SUCCESS('Pagespeed report started'))

        if options['env']:
            self._analysis_base_url = settings.PSI_ENVS[options['env']]['base_url']
        else:
            self._analysis_base_url = settings.PSI_ENVS['production']['base_url']
        
        # Disable file cache based in
        # https://github.com/googleapis/google-api-python-client/issues/299
        self.service = build(serviceName='pagespeedonline', version='v5', developerKey=PSI_GOOGLE_API_DEV_KEY, cache_discovery=False)
        
        urls_to_check = self._get_all_urls_to_check(all_urlpatterns)
        
        url_reports = self._check_urls_pagespeed(urls_to_check)

        if options['console']:
            self._console_report(url_reports)

