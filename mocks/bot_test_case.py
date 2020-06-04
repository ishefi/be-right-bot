import uuid
import unittest
from mock import patch
import pprint


def pp(obj):
    """Format anything nicely."""
    return pprint.PrettyPrinter().pformat(obj)


class BotTestCase(unittest.TestCase):
    module_prefix = None

    # *** self.m_config = magic! ***
    # every instance of BotTestCase have a member self.m_config

    def assert_contains_key_value(self, haystack, key, value):
        self.assertIsInstance(haystack, dict)
        self.assertIn(key, haystack)
        self.assertEqual(
            haystack[key], value, f'{key}: {value} is not in {pp(haystack)}'
        )

    def patch_module(self, target, *args, **kwargs):
        _, mocker = self.xpatch_module(target, *args,  **kwargs)
        return mocker

    def xpatch_module(self, target, *args, **kwargs):
        if not self.module_prefix:
            raise AssertionError('Must set `module_prefix` for `patch_module`!')
        return self.xpatch(self.module_prefix + target, *args, **kwargs)

    def patch(self, target, *args, **kwargs):
        _, mocker = self.xpatch(target, *args, **kwargs)
        return mocker

    def xpatch(self, target, *args, **kwargs):
        kwargs['autospec'] = True
        patcher = patch(target, *args, **kwargs)
        mocker = patcher.start()
        self.addCleanup(self.stop_patcher, patcher)
        return patcher, mocker

    def stop_patcher(self, patcher):
        try:
            patcher.stop()
        except RuntimeError:
            pass

    def unique(self, prefix):
        return prefix + uuid.uuid4().hex[:7]
