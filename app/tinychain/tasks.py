# main/tasks.py
from app.celery import app
from app.logger import get_module_logger

from core.models import Alert


@app.task
def process_alerts():
    alertProcessor = AlertProcessor()
    alertProcessor.process()


class AlertProcessor:

    logger = get_module_logger(__name__)

    def process(self):
        alerts = Alert.objects.all().order_by('-exchange') \
                                    .order_by('-coinpair')

        self.logger.info(f"Processing {alerts.count()} alerts")
        return True
