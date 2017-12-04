from gevent import monkey;monkey.patch_all()
from app import create_app, db
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from flask_apscheduler import APScheduler


app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


class Scheduler():
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server())
manager.add_command("scheduler", Scheduler())

if __name__ == '__main__':
    manager.run()
