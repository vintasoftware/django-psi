import logging
import progressbar

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
# from django.core.urlresolvers import RegexURLResolver, RegexURLPattern
from django.urls import URLPattern, URLResolver
from django.urls import reverse
from django.conf import settings

progressbar.streams.wrap_stderr()
logger = logging.getLogger(__name__)

def treat_pagespeed_response(response, strategy):
    report = False

    id = response['id']
    category = response['loadingExperience'].get('overall_category', '-')
    score = response['lighthouseResult']['categories']['performance']['score'] * 100

    report = {
        'psi_id': id,
        'category': category,
        'strategy': strategy,
        'score': score,
        'raw_data': response
    }

    return report

# As in: https://stackoverflow.com/questions/32933229
# /how-to-get-a-list-of-all-views-in-a-django-application
def get_all_project_urls_to_check(urlpatterns=None, url_list=[]):
    if not urlpatterns:
        root_urlconf = __import__(settings.ROOT_URLCONF)  # import root_urlconf module
        urlpatterns = root_urlconf.urls.urlpatterns  # project's urlpatterns

    for pattern in urlpatterns:
        if isinstance(pattern, URLResolver):
            # call this function recursively
            get_all_project_urls_to_check(pattern.url_patterns, url_list)
        elif isinstance(pattern, URLPattern):
            callback_func = pattern.callback
            if hasattr(callback_func, 'view_class') and \
                    hasattr(callback_func.view_class, 'is_psi_checked') and \
                    callback_func.view_class.is_psi_checked:
                pattern_name = pattern.name
                pattern_url = reverse(pattern.name)
                url_list.append(
                    {
                        'name': pattern_name,
                        'path': pattern_url
                    }
                )

    return url_list

def check_urls_in_pagespeed(psi_service, urls, base_url, strategy):
    url_reports = []
    for i in progressbar.progressbar(range(len(urls)), redirect_stdout=True):
        report = run_pagespeed_analysis(psi_service, base_url + urls[i]['path'], strategy)
        if report:
            url_reports.append({'url': urls[i], 'psi_report': report})

    return url_reports


def run_pagespeed_analysis(psi_service, url_to_check, strategy='desktop'):

    try:
        URLValidator(url_to_check)
    except ValidationError:
        logger.error('Invalid url: {url}.'.format(url=url_to_check))
        raise ValidationError

    logger.info('Analyzing url in pagespeed: {url}'.format(url=url_to_check))

    analysis_result = False
    r = None
    try:
        r = psi_service.pagespeedapi().runpagespeed(url=url_to_check, strategy=strategy).execute()
    except:
        logger.error('There was an error analyzing this url.')

    if r:
        logger.info('Done. Analysis made successfuly.')
        analysis_result = treat_pagespeed_response(response=r, strategy=strategy)
    
    return analysis_result