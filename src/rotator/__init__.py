from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

from rotator.keys import SCHED_HOUR, SCHED_MINUTE, SCHED_JOBID
from rotator.schedule.listeners import execution_listener, error_listener

app = Flask(__name__)
app.config.from_object('app_config')

from rotator import db_config

app.config.update(db_config.load_config())

from db_back import create_backup

scheduler = BackgroundScheduler()
scheduler.add_listener(execution_listener, EVENT_JOB_EXECUTED)
scheduler.add_listener(error_listener, EVENT_JOB_ERROR)
scheduler.add_job(create_backup, 'cron',
                  hour=int(app.config[SCHED_HOUR]),
                  minute=int(app.config[SCHED_MINUTE]),
                  id=app.config[SCHED_JOBID])
scheduler.start()

from rotator import model_blueprint

app.register_blueprint(model_blueprint.blueprint)

from rotatordb import db_session


@app.teardown_request
def remove_db_session(exception):
    db_session.remove()
