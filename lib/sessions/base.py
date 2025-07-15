from time import sleep

from testapi import *

"""
To avoid circular import issues. 
"""
def get_open_strategy(method):
    from lib.strategies import OPEN_STRATEGIES
    if method not in OPEN_STRATEGIES:
        raise ValueError(f'open method {method} does not exist.')
    return OPEN_STRATEGIES[method]


class BaseSession:
    _current_instance = None
    default_app_name = None
    allowed_open_strategies = ['krunner', 'konsole']

    @classmethod
    def open(cls, method='krunner', **kwargs):
        if cls._current_instance is not None:
            raise RuntimeError(f"{cls.__name__} instance already exists. Call close() before opening a new one.")
        if not cls.default_app_name:
            raise ValueError(f'{cls.__name__} must define a default app name')
        if not cls.allowed_open_strategies:
            raise ValueError(f'{cls.__name__} must define a list of strategies')
        if method not in cls.allowed_open_strategies:
            raise ValueError(f'{cls.__name__} open method {method} is not allowed')
        strategy = get_open_strategy(method)
        strategy.open_app(cls.default_app_name, **kwargs)
        instance = cls()
        cls._current_instance = instance
        instance.expect_ready()
        return instance

    @classmethod
    def current(cls):
        """
        Some session like tty/krunner should never call this current function.
        For E2E testing scenario for an Operating System, I think making each session a singleton is enough.
        :return:
        """
        if cls._current_instance is None:
            raise RuntimeError(f"{cls.__name__} has not been opened yet. Call open() first.")
        return cls._current_instance

    def expect(self, needle, timeout=30):
        assert_screen(needle, 'timeout', timeout)
        return self

    def click(self, needle, timeout=30, button='left'):
        assert_and_click(needle, 'timeout', timeout, 'button', button)
        return self

    def expect_ready(self, timeout=30):
        raise NotImplementedError(f"{self.__class__.__name__} must implement expect_ready()")

    def type_and_submit(self, text, **kwargs):
        needle = kwargs.get('needle')
        timeout = kwargs.get('timeout', 30)
        type_string(text)
        if needle:
            self.expect(needle, timeout)
        send_key('ret')
        return self

    def expect_gui_password_pop_up(self, timeout=30):
        return self.expect('gui_password_pop_up', timeout)

    def submit_gui_password(self):
        return self.type_and_submit('1122334455')

    def close_window(self):
        send_key('alt-f4')
        return self





