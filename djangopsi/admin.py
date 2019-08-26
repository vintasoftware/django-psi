import json
import datetime

from functools import update_wrapper
from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import render
from django.db.models import Avg

from .models import Environment, Report, Url, ReportGroup


def get_marks_and_scores(reports):
    first_year = reports.first().created.year
    last_year = reports.last().created.year
    first_month = reports.first().created.month
    last_month = reports.last().created.month

    marks = []
    overall_desktop_scores = []
    overall_mobile_scores = []
    for i in range(first_year, last_year + 1):
        start = 1
        finish = 12
        if i == first_year:
            start = first_month

        if i == last_year:
            finish = last_month

        for j in range(start, finish + 1):
            month = datetime.date(1900, j, 1).strftime('%b')
            mark = '{}, {}'.format(i, month)

            if mark not in marks:
                marks.append(mark)
                month_reports = reports.filter(created__year__gte=i,
                                                created__month__gte=j,
                                                created__year__lte=i,
                                                created__month__lte=j)

                overall_mobile_scores.append(
                    month_reports.filter(
                        strategy='mobile'
                    ).aggregate(Avg('score'))['score__avg']
                )
                overall_desktop_scores.append(
                    month_reports.filter(
                        strategy='desktop'
                    ).aggregate(Avg('score'))['score__avg']
                )

    return marks, overall_desktop_scores, overall_mobile_scores


class EnvironmentAdmin(admin.ModelAdmin):  
    dashboard_template = 'admin/djangopsi/environment/dashboard.html'
    url_dashboard_template = 'admin/djangopsi/environment/url_dashboard.html'
    report_group_dashboard_template = 'admin/djangopsi/environment/report_group_dashboard.html'
    readonly_fields = ['name', 'base_url']

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        my_urls = [
            url(
                r'(?P<id>\d+)/report_group/(?P<report_group_id>\d+)/dashboard/$',
                wrap(self.report_group_dashboard),
                name='%s_%s_report_group_dashboard' % info
            ),
            url(
                r'(?P<id>\d+)/url/(?P<url_id>\d+)/dashboard/$',
                wrap(self.url_dashboard),
                name='%s_%s_url_dashboard' % info
            ),
            url(
                r'(?P<id>\d+)/dashboard/$',
                wrap(self.dashboard),
                name='%s_%s_dashboard' % info
            ),
        ]

        return my_urls + urls

    def dashboard(self, request, id):
        environment = Environment.objects.get(pk=id)
        paths = environment.urls.all()

        reports = Report.objects.filter(
            url__environment_id=environment.id
        ).order_by('created')

        marks, overall_desktop_scores, overall_mobile_scores = get_marks_and_scores(reports)

        return render(request, self.dashboard_template, {
            'title': 'Page Speed Dashboard: %s' % environment.name,
            'environment': environment,
            'marks': json.dumps(marks),
            'paths': paths,
            'overall_mobile_scores': json.dumps(overall_mobile_scores),
            'overall_desktop_scores': json.dumps(overall_desktop_scores),
            'opts': self.model._meta,
        })

    def url_dashboard(self, request, id, url_id):
        environment = Environment.objects.get(pk=id)
        path = Url.objects.get(pk=url_id)

        reports = Report.objects.filter(
            url__environment_id=environment.id, url_id=url_id
        ).order_by('created')

        marks, overall_desktop_scores, overall_mobile_scores = get_marks_and_scores(reports)

        return render(request, self.url_dashboard_template, {
            'title': 'Page Speed Dashboard: %s - %s' % (environment.name, path.name),
            'environment': environment,
            'path': path,
            'marks': json.dumps(marks),
            'overall_mobile_scores': json.dumps(overall_mobile_scores),
            'overall_desktop_scores': json.dumps(overall_desktop_scores),
            'opts': self.model._meta,
        })

    def report_group_dashboard(self, request, id, report_group_id):
        environment = Environment.objects.get(pk=id)
        report_group = ReportGroup.objects.get(pk=report_group_id)
        paths = environment.urls.all()
        mobile_reports = report_group.reports.filter(strategy='mobile')
        desktop_reports = report_group.reports.filter(strategy='desktop')
        mobile_reports_avg = mobile_reports.aggregate(Avg('score'))['score__avg']
        desktop_reports_avg = desktop_reports.aggregate(Avg('score'))['score__avg']

        return render(request, self.report_group_dashboard_template, {
            'title': 'Page Speed Dashboard: %s environment - Report Group #%s' % (
                                                            environment.name,
                                                            report_group.id
                                                       ),
            'environment': environment,
            'paths': paths,
            'report_group': report_group,
            'mobile_reports_avg': mobile_reports_avg,
            'desktop_reports_avg': desktop_reports_avg,
            'mobile_reports': mobile_reports,
            'desktop_reports': desktop_reports,
            'opts': self.model._meta,
        })


admin.site.register(Environment, EnvironmentAdmin)
