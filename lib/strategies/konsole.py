from lib.sessions.app.konsole import KonsoleSession
from lib.strategies.base import OpenStrategy


class KonsoleOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KonsoleSession
                .ensure_active(open_strategy='krunner', **kwargs)
                .type_and_submit(app_name)
        )