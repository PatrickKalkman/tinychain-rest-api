# main/tasks.py
from app.celery import app

from tinychain import alerting


@app.task
def process_alerts():
    alertProcessor = alerting.AlertProcessor()
    alertProcessor.process()

    notifier = alerting.Notifier()
    notifier.notifyAlerts()
