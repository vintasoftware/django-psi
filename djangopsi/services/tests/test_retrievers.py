from django.test import TestCase

from djangopsi.services.retrievers import treat_pagespeed_response


class RetrieversTestCase(TestCase):
    def setUp(self):
        pass

    def test_treat_pagespeed_response(self):

        mock_response = {
            "id": 1,
            "loadingExperience": {"overall_category": "fast"},
            "lighthouseResult": {"categories": {"performance": {"score": 0.8}}},
        }

        expected_return_value = {
            "psi_id": 1,
            "category": "fast",
            "strategy": "test_strategy",
            "score": 80,
            "raw_data": mock_response,
        }

        actual_return_value = treat_pagespeed_response(mock_response, "test_strategy")

        self.assertDictEqual(actual_return_value, expected_return_value)
