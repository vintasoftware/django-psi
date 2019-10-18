from django.apps import apps
from django.test import TestCase, modify_settings


@modify_settings(INSTALLED_APPS={"append": "djangopsi"})
class AppsTests(TestCase):
    def test_apps(self):
        app = apps.get_app_config("djangopsi")
        self.assertEqual(app.name, "djangopsi")
