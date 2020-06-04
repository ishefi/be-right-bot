import sys
from fnmatch import fnmatch
import pytest
import unittest

import attr


def install_loader_patcher():
    for loader in sys.meta_path:
        if isinstance(loader, LoaderPatcher):
            return
    sys.meta_path.insert(0, LoaderPatcher())


@attr.s
class ModuleSpec(object):
    name = attr.ib()
    loader = attr.ib()


class LoaderPatcher(object):
    @property
    def loader(self):
        return self

    def find_spec(self, fullname, path, target=None):
        if fnmatch(fullname, 'base.config'):
            return ModuleSpec(
                name='base.config', loader=self
            )
        return None

    def load_module(self, module):
        if fnmatch(module, 'base.config'):
            import sys
            sys.modules['base.config'] = MockConfig()


@pytest.fixture(scope='function', autouse=True)
def _reset_global_mocks(request):
    """Reset MockConfig to its defaults."""
    try:
        MockConfig.reset_singleton()
        if isinstance(request.instance, unittest.TestCase):
            request.instance.m_config = MockConfig()
    except Exception as ex:
        print(ex)


class Singleton(type):
    _singletons = {}

    def __call__(cls):
        if cls not in cls._singletons:
            singleton = super(Singleton, cls).__call__()
            cls._singletons[cls] = singleton
        return cls._singletons[cls]

    def reset_singleton(cls):
        if cls not in cls._singletons:
            singleton = super(Singleton, cls).__call__()
            cls._singletons[cls] = singleton
        else:
            cls._singletons[cls]._reset()
        return cls._singletons[cls]


class MockConfig(dict, metaclass=Singleton):
    """Great for mocking `base.config`"""

    def __init__(self):
        super(MockConfig, self).__init__()
        self.__ready = True
        self._reset()

    def _reset(self):
        self.aws = {
            'region': 'mock-region',
            'access_key_id': 'mock-access-key-id',
            'secret_access_key': 'mock-secret',
        }
        self.app_url = 'https://telebot.all{}'

    def __getattr__(self, name):
        if name == '__name__':
            return 'base.config'
        try:
            return self.__getitem__(name)
        except KeyError:
            raise AttributeError('No %r in mock config' % name)
