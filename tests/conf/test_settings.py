import os
from unittest import mock

import pytest

from atto.conf import ModuleSettings, Settings


def test_empty():
    settings = Settings()
    with pytest.raises(AttributeError):
        settings.NOT_EXISTS


def test_readonly():
    settings = Settings({
        'FOO': 'new_foo',
        'bar': 'bar'
    })
    assert settings.FOO == 'new_foo'

    with pytest.raises(AttributeError):
        assert settings.bar == 'bar'

    with pytest.raises(AttributeError):
        settings.NOT_EXISTS

    assert 'NOT_EXISTS' not in settings
    assert 'FOO' in settings

    with pytest.raises(AttributeError):
        settings.NEW_VALUE = '2'
    assert settings.FOO == 'new_foo'

    with pytest.raises(AttributeError):
        del settings.FOO
    assert settings.FOO == 'new_foo'


def test_extend_base():
    settings = Settings({
        'FOO': 'foo'
    })
    settings.extend(dict(
        FOO='new_foo',
        BAR='new bar',
        baz='new baz'
    ))
    assert settings.FOO == 'foo'
    assert settings.BAR == 'new bar'
    assert 'baz' not in settings


def test_extend_mistmatch_types():
    settings = Settings({
        'FOO': 'foo'
    })

    with pytest.raises(RuntimeError):
        settings.extend(dict(FOO=1))


@mock.patch.dict(os.environ, {
    'BAR': 'env-bar',
    'INT': '123',
    'BYTE': 'env-byte',
    'BOOL_WORD': 'False',
    'BOOL_NUM': '0',
})
def test_extend_with_envs():
    settings = Settings()
    settings.extend({
        'BAR': 'bar',
        'INT': 1,
        'BYTE': b'byte',
        'BOOL_WORD': True,
        'BOOL_NUM': True,
    })
    assert settings.BAR == 'env-bar'
    assert settings.INT == 123
    assert settings.BYTE == b'env-byte'
    assert not settings.BOOL_WORD
    assert not settings.BOOL_NUM


@mock.patch.dict(os.environ, {'TEST_SETINGS': 'tests.conf.settings'})
def test_module_init():
    settings = ModuleSettings('TEST_SETINGS')
    assert settings.FOO == 'module foo'
    assert 'bar' not in settings
