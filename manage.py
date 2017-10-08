from gevent import monkey;monkey.patch_all()
import os
import sys
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell, Server,Command

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db)

"""Starts the celery worker."""
class CeleryWorker(Command):
    name = 'celery'
    capture_all_args = True
    def run(self, argv):
        ret = subprocess.call(
            ['celery', 'worker', '-A', 'app.celery'] + argv)
        sys.exit(ret)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command("runserver", Server())
manager.add_command("celery", CeleryWorker())

if __name__ == '__main__':
    manager.run()
