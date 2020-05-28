from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Alert
from tinychain.alerting import AlertProcessor

from unittest.mock import patch


class AlertProcessorTest(TestCase):
    """Test processing the alerts"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@simpletechture.nl',
            'test123'
        )

    @patch('krakenex.API.query_public')
    def test_positive_lower_alerts(self, mock_query_public):
        """Test if lower alert becomes active"""

        mock_query_public.return_value = self.generate_json(17000.0)

        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='<',
                                     limit=18200.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertTrue(alert.is_active)

    @patch('krakenex.API.query_public')
    def test_positive_higher_alerts(self, mock_query_public):
        """Test if higher alert becomes active"""

        mock_query_public.return_value = self.generate_json(200.0)

        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='>',
                                     limit=100.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertTrue(alert.is_active)

    @patch('krakenex.API.query_public')
    def test_negative_lower_alerts(self, mock_query_public):
        """Test if lower alert does not becomes active"""

        mock_query_public.return_value = self.generate_json(350.0)

        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='<',
                                     limit=100.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertFalse(alert.is_active)

    @patch('krakenex.API.query_public')
    def test_negative_higher_alerts(self, mock_query_public):
        """Test if higher alert does not become active"""

        mock_query_public.return_value = self.generate_json(9000.0)

        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='>',
                                     limit=10000.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertFalse(alert.is_active)

    @patch('krakenex.API.query_public')
    def test_active_alert_becomes_inactive(self, mock_query_public):
        """Test if higher alert does not become active"""

        mock_query_public.return_value = self.generate_json(9000.0)

        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='>',
                                     limit=10000.00,
                                     is_active=True)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertFalse(alert.is_active)

    def generate_json(self, price):
        return {
            "error": [],
            "result": {
                "XXBTZEUR": {
                    "a": [
                        str(price),
                        "1",
                        "1.000"
                    ],
                    "b": [
                        "8345.00000",
                        "1",
                        "1.000"
                    ],
                    "c": [
                        "8343.00000",
                        "0.00749041"
                    ],
                    "v": [
                        "191.70864403",
                        "5505.40011852"
                    ],
                    "p": [
                        "8352.10052",
                        "8304.10921"
                    ],
                    "t": [
                        1155,
                        28526
                    ],
                    "l": [
                        "8292.00000",
                        "8114.40000"
                    ],
                    "h": [
                        "8427.50000",
                        "8449.00000"
                    ],
                    "o": "8364.90000"
                }
            }
        }
