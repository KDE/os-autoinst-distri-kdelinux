from lib.sessions.app.konsole import KonsoleSession
from lib.strategies.base import OpenStrategy


class KonsoleOpenStrategy(OpenStrategy):
    def open_app(self, app_name):
        (
            KonsoleSession
                .ensure_active()
                .type_and_submit(app_name)
        )