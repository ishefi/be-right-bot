"""Together with pytest.ini, this makes sure our patcher works early enough."""
from tests.conftest import install_loader_patcher
install_loader_patcher()


def pytest_cmdline_preparse(*args, **kwargs):
    install_loader_patcher()
