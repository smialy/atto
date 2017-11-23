import os
import importlib
import types
from pathlib import Path


class Settings:

    def __init__(self, data=None):
        for name, value in _to_dict(data).items():
            if _is_valid_name(name):
                continue
            self.__dict__[name] = value

    def __setattr__(self, name, value):
        raise AttributeError(
            '"{}" object is readonly'.format(self.__class__.__name__))

    def __delattr__(self, name):
        raise AttributeError(
            '"{}" object is readonly'.format(self.__class__.__name__))

    def __getitem__(self, name):
        return self.__dict__[name]

    def __contains__(self, name):
        return name in self.__dict__

    def extend(self, settings):
        for name, origin_value in _to_dict(settings).items():
            if _is_valid_name(name):
                continue
            value = getattr(self, name, None)
            origin_type = type(origin_value)
            if value is None:
                env_value = os.getenv(name)
                if env_value is not None:
                    origin_value = _cast_env_value(origin_type, env_value)
                self.__dict__[name] = origin_value
            else:
                if not isinstance(value, origin_type):
                    error_msg = 'Mistmatch variable type {}{}. Expected: {}'\
                        .format(name, origin_type, type(value))
                    raise RuntimeError(error_msg)


class ModuleSettings(Settings):

    def __init__(self, setring_module_name):
        settings_module = os.getenv(setring_module_name)
        if settings_module is None:
            error_msg = 'Not found settings module name in env: {}'.format(
                setring_module_name)
            raise RuntimeError(error_msg)
        module = importlib.import_module(settings_module)
        super().__init__(module)


def _to_dict(data=None):
    if data is None:
        return {}
    if isinstance(data, dict):
        return data.copy()
    if isinstance(data, types.ModuleType):
        return {name: getattr(data, name) for name in dir(data)}
    raise TypeError('Expected "dict" or "module"')


def _is_valid_name(name):
    return name.startswith('_') or not name.isupper()


def _cast_env_value(origin_type, value):
    if issubclass(origin_type, bool):
        return value.upper() in ('1', 'TRUE')
    elif issubclass(origin_type, int):
        return int(value)
    elif issubclass(origin_type, Path):
        return Path(value)
    elif issubclass(origin_type, bytes):
        return value.encode()
    return value
