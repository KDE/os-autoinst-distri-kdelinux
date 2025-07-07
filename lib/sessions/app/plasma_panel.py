from lib.sessions.base import BaseSession


class PlasmaPanelSession(BaseSession):
    name = "plasma_panel"
    allowed_open_strategies = []

    @classmethod
    def open(cls, method=None, **kwargs):
        instance = cls()
        cls._current_instance = instance
        instance.expect_ready()
        return instance

    def expect_ready(self, timeout=30):
        self.expect('bottom_panel_left_part', timeout)

    def click_plasma_panel_system_tray_icon(self, timeout=30, button='left'):
        return self.click('plasma_panel_system_tray_icon', timeout=timeout, button=button)

    def expect_plasma_panel_system_tray_default_popup(self, timeout=30):
        return self.click('plasma_panel_system_tray_default_popup', timeout=timeout)
