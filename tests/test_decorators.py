from django.test import TestCase

from djangopsi.decorators import is_psi_checked


class DecoratorTests(TestCase):
    def test_is_psi_checked(self):
        @is_psi_checked
        def a_view(request):
            return None

        self.assertEqual(a_view.is_psi_checked, True)
