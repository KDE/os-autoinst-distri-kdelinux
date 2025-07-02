from testapi import *
from lib.strategies import OPEN_STRATEGIES


class BaseSession:
    default_app_name = None
    allowed_strategies = []

    @classmethod
    def open(cls, method='krunner'):
        if not cls.default_app_name:
            raise ValueError(f'{cls.__name__} must define a default app name')
        if not cls.allowed_strategies:
            raise ValueError(f'{cls.__name__} must define a list of strategies')
        if method not in cls.allowed_strategies or method not in OPEN_STRATEGIES:
            raise ValueError(f'{cls.__name__} open method {method} is not allowed')
        strategy = OPEN_STRATEGIES[method]
        strategy.open_app(default_app_name)
        instance = cls()
        instance.expect_ready()
        return instance

    def expect(self, needle, timeout=30):
        assert_screen(needle, 'timeout', timeout)
        return self

    def expect_ready(self, timeout=30):
        raise NotImplementedError(f"{self.__class__.__name__} must implement expect_ready()")

    def type_and_submit(self, text):
        type_string(text)
        send_key('ret')
        return self
