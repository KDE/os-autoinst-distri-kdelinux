from lib.sessions.kickoff import KickOffSession
from lib.strategies.base import OpenStrategy


class KickoffOpenStrategy(OpenStrategy):
    def open_app(self, app_name):
        (
            KickOffSession
                .open()
                .click_kickoff_searchbar()
                .type_and_submit(app_name)
        )