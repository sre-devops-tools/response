from apscheduler.schedulers.background import BackgroundScheduler

from response.slack.decorators import handle_notifications


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(handle_notifications, 'interval', seconds=25)
    scheduler.start()