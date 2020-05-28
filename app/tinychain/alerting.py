import collections

from app.logger import get_module_logger
from core.models import Alert, DeviceToken
from django.conf import settings
from decimal import Decimal

from apns2.client import APNsClient
from apns2.payload import Payload, PayloadAlert
from apns2.credentials import TokenCredentials

import krakenex


class AlertProcessor:

    kraken = krakenex.API()

    def process(self):
        alerts = Alert.objects.all().order_by('-exchange') \
                                    .order_by('-coinpair')

        for alert in alerts:
            pair = self.create_ticker_pair(alert.coinpair)
            price = Decimal(self.get_pair_price(pair))

            limit = Decimal(alert.limit)
            higher = '>' in alert.indicator and price > limit
            lower = '<' in alert.indicator and price < limit

            alert.is_active = higher or lower
            alert.trigger_value = price if alert.is_active else 0
            alert.save()

        return True

    def create_ticker_pair(self, coinpair):
        return f"X{coinpair.replace(':', 'Z')}"

    def get_pair_price(self, ticker):
        result = self.kraken.query_public(f'Ticker?pair={ticker}')
        ticker = result.get('result').get(ticker)
        return ticker.get('a')[0]


class Notifier:

    logger = get_module_logger(__name__)

    def notifyAlerts(self):
        active_alerts = Alert.objects.all().filter(is_active=True)
        for alert in active_alerts:
            deviceTokens = DeviceToken.objects.all().filter(user=alert.user)
            if deviceTokens.count() > 0:

                payload_alert = PayloadAlert(
                    title='Price alert',
                    body=str(alert),
                )

                payload = Payload(alert=payload_alert,
                                  sound='chime', badge=1)
                self.send_push_message(deviceTokens[0].token, payload)
            else:
                self.logger.info(
                    'Could not send alert, no device token was found')

    def send_push_message(self, token, payload):
        token_credentials = TokenCredentials(
            auth_key_path=settings.PUSH_AUTH_KEY_PATH,
            auth_key_id=settings.PUSH_AUTH_KEY_ID,
            team_id=settings.PUSH_AUTH_TEAM_ID)

        client = APNsClient(credentials=token_credentials, use_sandbox=True)

        Notification = collections.namedtuple(
            'Notification', ['token', 'payload'])
        notifications = [Notification(payload=payload, token=token)]

        res = client.send_notification_batch(
            notifications=notifications, topic=settings.PUSH_AUTH_TOPIC)

        return res
