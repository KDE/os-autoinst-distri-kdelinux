def get_open_strategy(name):
    from lib.strategies import OPEN_STRATEGIES
    if name not in OPEN_STRATEGIES:
        raise ValueError(f'open strategy {name} does not exist.')
    return OPEN_STRATEGIES[name]


class OpenableSessionMixin:
    default_app_name = None
    allowed_open_strategies = ['krunner', 'konsole']

    @classmethod
    def ensure_active(cls, open_strategy='krunner', launch_app=True, **kwargs):
        if not cls.default_app_name:
            raise ValueError(f'{cls.__name__} must define a default app name')
        if not cls.allowed_open_strategies:
            raise ValueError(f'{cls.__name__} must define a list of strategies')
        if open_strategy not in cls.allowed_open_strategies:
            raise ValueError(f'{cls.__name__} open strategy {open_strategy} is not allowed')

        if launch_app:
            strategy = get_open_strategy(open_strategy)
            strategy.open_app(cls.default_app_name, **kwargs)

        instance = cls()
        instance.expect_ready()
        return instance
