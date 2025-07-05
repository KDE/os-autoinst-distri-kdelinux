from lib.sessions.konsole import KonsoleSession
from lib.sessions.krunner import KRunnerSession
from lib.strategies.base import OpenStrategy


class KonsoleOpenStrategy(OpenStrategy):
    def open_app(self, app_name):
        (
            KonsoleSession
            .open()
            .type_and_submit(app_name)
        )
