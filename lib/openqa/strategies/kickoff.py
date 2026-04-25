from lib.sessions.syscore.kickoff import KickOffSession
from lib.strategies.base import OpenStrategy


class KickoffOpenStrategy(OpenStrategy):
    def open_app(self, app_name, **kwargs):
        (
            KickOffSession
                .ensure_active()
                .click_kickoff_searchbar()
                .type_and_submit(app_name, **kwargs)
        )