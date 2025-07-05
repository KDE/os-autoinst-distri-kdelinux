from lib.sessions.krunner import KRunnerSession
from lib.strategies.base import OpenStrategy


class KRunnerOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KRunnerSession
                .open()
                .type_and_submit(app_name, **kwargs)
        )