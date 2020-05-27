from app.logger import get_module_logger
from core.models import Alert
from decimal import Decimal

import krakenex


class AlertProcessor:

    logger = get_module_logger(__name__)
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
            alert.save()

        return True

    def create_ticker_pair(self, coinpair):
        return f"X{coinpair.replace(':', 'Z')}"

    def get_pair_price(self, ticker):
        result = self.kraken.query_public(f'Ticker?pair={ticker}')
        ticker = result.get('result').get(ticker)
        return ticker.get('a')[0]
