from lib.sessions.syscore.krunner import KRunnerSession
from lib.strategies.base import OpenStrategy


class KRunnerOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KRunnerSession
                .ensure_active()
                .type_and_submit(app_name, **kwargs)
        )