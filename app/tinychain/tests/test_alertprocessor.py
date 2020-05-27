from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Alert
from tinychain.alerting import AlertProcessor


class AlertProcessorTest(TestCase):
    """Test processing the alerts"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@simpletechture.nl',
            'test123'
        )

    def test_process_lower_alerts(self):
        """Test processing lower alerts"""
        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='<',
                                     limit=18200.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertTrue(alert.is_active)

    def test_process_higher_alerts(self):
        """Test processing higher alerts"""
        alert = Alert.objects.create(user=self.user,
                                     exchange='Kraken',
                                     coinpair='XBT:EUR',
                                     indicator='>',
                                     limit=100.00)

        alert_processor = AlertProcessor()
        alert_processor.process()

        alert.refresh_from_db()
        self.assertTrue(alert.is_active)
