from django.conf import settings
from django.db.models import Avg

from djangopsi.models import Environment, ReportGroup, Report

def format_report_group_slack_message_json(report_group):
    mobile_report_score = report_group.reports.filter(strategy='mobile').aggregate(Avg('score'))['score__avg']
    desktop_report_score = report_group.reports.filter(strategy='desktop').aggregate(Avg('score'))['score__avg']
    previous_mobile_report_score = ReportGroup.objects.filter(
        created__lt=report_group.created
    ).order_by('created').last().reports.filter(strategy='mobile').aggregate(Avg('score'))['score__avg']
    previous_desktop_report_score = ReportGroup.objects.filter( 
        created__lt=report_group.created
    ).order_by('created').last().reports.filter(strategy='desktop').aggregate(Avg('score'))['score__avg']
    return {
"text": "Hello, a new Google PageSpeed report was generated for your app hosted at:\r\n\
" + report_group.environment.base_url + "\r\n\r\n\
Mobile score average: " + str(mobile_report_score) + "%, Desktop score average: " + str(desktop_report_score) + "%\r\n\
Mobile score delta is " + str(mobile_report_score - previous_mobile_report_score) + "% by last report group\r\n\
Desktop score delta is " + str(desktop_report_score - previous_desktop_report_score) + "% by last report group\r\n\
For more info, check: " + settings.PROTOCOL + "://" + settings.DOMAIN + "/" +
settings.ADMIN_PATH + "/djangopsi/environment/" +
str(report_group.environment.id) + "/report_group/" + str(report_group.id) + "/dashboard/"}


def print_report_group_console_report(base_url, report_list, strategy):
    print("\r\n\
PageSpeed Insights\r\n\
--------------------------------------------\r\n\
Statistics for {0}\r\n\
Strategy used: {1}\r\n".format(base_url, strategy)
)

    for report in report_list:
        print("Name: {0}".format(report['url']['name']))
        print("----- path: {0}".format(report['url']['path']))
        if report['psi_report']:
            print("----- category: {0}".format(report['psi_report']['category']))
            print("----- score: {0}".format(report['psi_report']['score']))
        else:
            print("----- report failed")
            
        print("--------------------------------------------")
