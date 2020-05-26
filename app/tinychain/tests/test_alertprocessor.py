from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import Alert
from tinychain.tasks import AlertProcessor


class AlertProcessorTest(TestCase):
    """Test processing the alerts"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@simpletechture.nl',
            'test123'
        )

    def test_process_alerts(self):
        """Test processing alerts"""
        Alert.objects.create(user=self.user,
                             exchange='Kraken',
                             coinpair='EUR:BTC',
                             indicator='>',
                             limit=8200.00)

        alert_processor = AlertProcessor()
        result = alert_processor.process()
        self.assertTrue(result)
