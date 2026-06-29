import sys

import os

from pathlib import Path



# ---------------------------------------------------------

# THE ULTIMATE PATH ROUTING FIX

# ---------------------------------------------------------

# 1. Resolve exact absolute paths dynamically

current_dir = Path(__file__).parent.resolve()

layer_3_dir = current_dir.parent.resolve()

root_dir = layer_3_dir.parent.resolve()



# 2. Forcefully inject them at the highest priority in sys.path

if str(layer_3_dir) not in sys.path:

    sys.path.insert(0, str(layer_3_dir))

if str(root_dir) not in sys.path:

    sys.path.insert(0, str(root_dir))



import pytest

from unittest.mock import Mock



from layer_3.storage.translation_analytics_service import TranslationAnalyticsService



# Helper Class for Repository Mocking

class MockRecord:

    def __init__(self, language):

        self.original_language = language



class TestTranslationAnalyticsService:



    @pytest.fixture

    def mock_repo(self):

        return Mock()



    @pytest.fixture

    def service(self, mock_repo):

        return TranslationAnalyticsService(repository=mock_repo)



    # ---------------------------------------------------------

    # HEALTH METRICS TESTS

    # ---------------------------------------------------------

    

    def test_get_translation_health_metrics_success(self, service, mock_repo):

        mock_repo.get_translation_metrics.return_value = {

            "total": 100,

            "success": 95,

            "failed": 5

        }



        result = service.get_translation_health_metrics()



        assert result["total"] == 100

        assert result["success"] == 95

        assert result["failed"] == 5

        assert result["success_rate"] == 95.0



    def test_health_metrics_zero_records(self, service, mock_repo):

        mock_repo.get_translation_metrics.return_value = {

            "total": 0,

            "success": 0,

            "failed": 0

        }



        result = service.get_translation_health_metrics()



        assert result["success_rate"] == 0.0



    # ---------------------------------------------------------

    # LANGUAGE DISTRIBUTION TESTS

    # ---------------------------------------------------------



    def test_language_distribution(self, service, mock_repo):

        mock_repo.get_recent_language_usage.return_value = {

            "hi": 60,

            "es": 30,

            "fr": 10

        }



        result = service.get_language_distribution()



        assert result["hi"]["count"] == 60

        assert result["hi"]["percentage"] == 60.0

        assert result["es"]["count"] == 30

        assert result["es"]["percentage"] == 30.0



    def test_language_distribution_empty(self, service, mock_repo):

        mock_repo.get_recent_language_usage.return_value = {}



        result = service.get_language_distribution()



        assert result == {}



    def test_language_distribution_sorted(self, service, mock_repo):

        mock_repo.get_recent_language_usage.return_value = {

            "fr": 5,

            "hi": 50,

            "es": 20

        }



        result = service.get_language_distribution()

        keys = list(result.keys())



        assert keys == ["hi", "es", "fr"]



    # ---------------------------------------------------------

    # CUSTOMER LANGUAGE PROFILE TESTS

    # ---------------------------------------------------------



    def test_customer_language_profile(self, service, mock_repo):

        mock_repo.get_customer_history.return_value = [

            MockRecord("hi"),

            MockRecord("hi"),

            MockRecord("en")

        ]



        result = service.get_customer_language_profile(123)



        assert result["preferred_language"] == "hi"

        assert result["total_translations"] == 3

        assert result["language_history"] == ["hi", "hi", "en"]



    def test_customer_language_profile_no_history(self, service, mock_repo):

        mock_repo.get_customer_history.return_value = []



        result = service.get_customer_language_profile(123)



        assert result["preferred_language"] == "en"

        assert result["language_history"] == []

        assert result["total_translations"] == 0

        assert result["dominance_score"] == 1.0



    def test_customer_language_dominance_score(self, service, mock_repo):

        mock_repo.get_customer_history.return_value = [

            MockRecord("hi"),

            MockRecord("hi"),

            MockRecord("hi"),

            MockRecord("en")

        ]



        result = service.get_customer_language_profile(123)



        assert result["preferred_language"] == "hi"

        assert result["dominance_score"] == 0.75



    # ---------------------------------------------------------

    # FAILED TRANSLATION REPORT TESTS

    # ---------------------------------------------------------



    def test_failed_translation_report(self, service, mock_repo):

        failed_records = [

            MockRecord("hi"),

            MockRecord("hi"),

            MockRecord("es")

        ]



        mock_repo.get_failed_translations.return_value = failed_records



        result = service.get_failed_translation_report()



        assert result["failure_count"] == 3

        assert result["failure_by_language"]["hi"] == 2

        assert result["failure_by_language"]["es"] == 1

        assert result["records"] == failed_records



    def test_failed_translation_report_empty(self, service, mock_repo):

        mock_repo.get_failed_translations.return_value = []



        result = service.get_failed_translation_report()



        assert result["failure_count"] == 0

        assert result["failure_by_language"] == {}

        assert result["records"] == []



    def test_failed_translation_limit(self, service, mock_repo):

        mock_repo.get_failed_translations.return_value = []



        service.get_failed_translation_report(limit=50)



        mock_repo.get_failed_translations.assert_called_once_with(limit=50)