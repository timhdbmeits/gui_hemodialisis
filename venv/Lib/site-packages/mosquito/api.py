# Standard library modules.
from contextlib import contextmanager

# Third party modules.

# Local modules
from mosquito.swarm import Swarm
from mosquito.scheduler import Scheduler

# Globals and constants variables.
ATTRIBUTE_REGISTRY = dict()


def registry():
    """
    :return: a reference on the global attribute registry
    :rtype: dict
    """
    return ATTRIBUTE_REGISTRY


def available_attributes():
    """
    :return: names of all available attributes
    :rtype: list[str]
    """
    return sorted(getattr(Swarm, '__attrs__'))


def register_attributes(**kwargs):
    """
    Update global attribute registry.

    :param kwargs: attribute key values mapping
    """
    for attr, value in kwargs.items():
        if attr not in available_attributes():
            raise AttributeError(f'unknown attribute "{attr}"')

        ATTRIBUTE_REGISTRY[attr] = value


def attribute(attr):
    """
    Decorator for an attribute callback.

    :param attr: name of the attribute to be registered
    :return: decorator to register attribute
    """
    def attribute_decorator(value):
        register_attributes(**{attr: value})

        return value

    return attribute_decorator


@contextmanager
def swarm(*args, **kwargs):
    """
    Context that sets up a session swarm using registered attributes and provides a preconfigured
    scheduler object.

    :param args: positional arguments for :class:`Scheduler`
    :param kwargs: key word arguments for :class:`Scheduler`
    :return: scheduler
    :rtype: Scheduler
    """
    _swarm = Swarm(**registry())

    try:
        _swarm.open()
        yield Scheduler(_swarm, *args, **kwargs)

    finally:
        _swarm.close()


def observer():
    return Swarm.observer
