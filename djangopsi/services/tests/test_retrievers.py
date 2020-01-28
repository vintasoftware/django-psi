# deps
import mock
from django.test import TestCase

from djangopsi.services.retrievers import (  # run_pagespeed_analysis,
    check_urls_in_pagespeed,
    get_all_project_urls_to_check,
    treat_pagespeed_response,
)


class RetrieversTestCase(TestCase):
    def setUp(self):
        self.test_strategy = "test_strategy"
        self.test_base_url = "http://www.vinta.com.br"
        self.test_psi_service = "test_service"
        self.test_urls = [{"path": "1"}, {"path": "2"}]

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

    def test_get_all_project_urls_to_check(self):
        with self.assertRaises(AttributeError):
            get_all_project_urls_to_check(None, [], None)

    @mock.patch("djangopsi.services.retrievers.run_pagespeed_analysis")
    def test_check_urls_in_pagespeed(self, _run_pagespeed_analysis):
        check_urls_in_pagespeed(
            self.test_psi_service,
            self.test_urls,
            self.test_base_url,
            self.test_strategy,
        )

        _run_pagespeed_analysis.assert_called()
        self.assertEqual(_run_pagespeed_analysis.call_count, 2)

    def test_run_pagespeed_analysis(self):
        pass
        # analysis_result = run_pagespeed_analysis(
        #     psi_service, url_to_check, strategy="desktop"
        # )
