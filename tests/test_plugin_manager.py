"""Plugin manager unit tests using unittest."""

import copy
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from plugin_manager import PluginManager, PluginRegistry


class TestPluginManager(unittest.TestCase):
    def setUp(self):
        self.original_plugins = copy.deepcopy(PluginRegistry.AVAILABLE_PLUGINS)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, 'plugins-test.json')
        self.manager = PluginManager(config_file=self.config_path)

    def tearDown(self):
        PluginRegistry.AVAILABLE_PLUGINS = self.original_plugins
        self.temp_dir.cleanup()

    def test_enable_disable_optional_plugin(self):
        self.assertTrue(self.manager.enable_plugin('official_timing'))
        self.assertTrue(self.manager.is_enabled('official_timing'))

        self.assertTrue(self.manager.disable_plugin('official_timing'))
        self.assertFalse(self.manager.is_enabled('official_timing'))

    def test_dependency_blockers_prevent_core_disable(self):
        self.assertTrue(self.manager.enable_plugin('leaderboard'))

        blockers = self.manager.get_disable_blockers('race_management')
        self.assertIn('leaderboard', blockers)

        self.assertFalse(self.manager.disable_plugin('race_management'))

    def test_custom_plugin_uninstall_blocked_by_dependency(self):
        self.assertTrue(self.manager.install_plugin('custom_base', {
            'name': 'Custom Base',
            'module': 'custom_base_mod',
            'enabled': True,
            'dependencies': []
        }))

        self.assertTrue(self.manager.install_plugin('custom_child', {
            'name': 'Custom Child',
            'module': 'custom_child_mod',
            'enabled': True,
            'dependencies': ['custom_base']
        }))

        blockers = self.manager.get_disable_blockers('custom_base')
        self.assertIn('custom_child', blockers)

        self.assertFalse(self.manager.uninstall_plugin('custom_base'))

        self.assertTrue(self.manager.disable_plugin('custom_child'))
        self.assertTrue(self.manager.uninstall_plugin('custom_child'))
        self.assertTrue(self.manager.uninstall_plugin('custom_base'))

    def test_custom_plugin_dependencies_persist_in_config(self):
        self.assertTrue(self.manager.install_plugin('persisted_plugin', {
            'name': 'Persisted Plugin',
            'module': 'persisted_mod',
            'enabled': True,
            'dependencies': ['authentication']
        }))

        reloaded_manager = PluginManager(config_file=self.config_path)
        plugin = reloaded_manager.get_plugin_info('persisted_plugin')

        self.assertIsNotNone(plugin)
        self.assertEqual(plugin.get('dependencies'), ['authentication'])
        self.assertTrue(plugin.get('enabled'))


if __name__ == '__main__':
    unittest.main()
