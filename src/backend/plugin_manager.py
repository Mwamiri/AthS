"""
Plugin Management System
Enables modular architecture with admin-controlled feature activation/deactivation
"""

import json
import importlib
import os
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Central registry for all system plugins/modules"""
    
    # Define all available plugins in the system
    AVAILABLE_PLUGINS = {
        # Core Features
        'authentication': {
            'name': 'Authentication',
            'description': 'User authentication with JWT and optional 2FA',
            'version': '2.1.6',
            'enabled': True,
            'required': True,  # Cannot be disabled
            'category': 'core',
            'module': 'auth_service'
        },
        'user_management': {
            'name': 'User Management',
            'description': 'User registration, profiles, and account management',
            'version': '2.1.6',
            'enabled': True,
            'required': True,
            'category': 'core',
            'module': 'user_service'
        },
        'race_management': {
            'name': 'Race Management',
            'description': 'Create and manage races, events, and registrations',
            'version': '2.1.6',
            'enabled': True,
            'required': True,
            'category': 'core',
            'module': 'race_service'
        },
        
        # Enterprise Features
        'audit_logging': {
            'name': 'Audit Logging',
            'description': 'Track all user actions and system events for compliance',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'audit_service'
        },
        'email_notifications': {
            'name': 'Email Notifications',
            'description': 'Send SMTP emails for events, alerts, and notifications',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'email_service'
        },
        'health_monitoring': {
            'name': 'Health Monitoring',
            'description': 'System health checks and alerts for infrastructure',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'alerts'
        },
        'rate_limiting': {
            'name': 'Rate Limiting',
            'description': 'API rate limiting with per-user policies and dashboards',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'rate_limiter'
        },
        'feature_flags': {
            'name': 'Feature Flags',
            'description': 'Safely rollout features with gradual rollout and A/B testing',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'feature_flags'
        },
        'request_deduplication': {
            'name': 'Request Deduplication',
            'description': 'Prevent duplicate API requests and ensure idempotency',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'deduplication'
        },
        'database_migrations': {
            'name': 'Database Migrations',
            'description': 'Database schema versioning with Alembic',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'infrastructure',
            'module': 'migrations'
        },
        'ci_cd_pipeline': {
            'name': 'CI/CD Pipeline',
            'description': 'Automated testing, building, and deployment',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'infrastructure',
            'module': 'cicd'
        },
        
        # Optional Features
        'two_fa': {
            'name': 'Two-Factor Authentication',
            'description': 'TOTP-based 2FA with QR codes and backup codes',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'security',
            'module': 'twofa',
            'dependencies': ['authentication']
        },
        'leaderboard': {
            'name': 'Leaderboard',
            'description': 'Real-time athlete leaderboards and rankings',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'features',
            'module': 'leaderboard',
            'dependencies': ['race_management']
        },
        'results_analytics': {
            'name': 'Results Analytics',
            'description': 'Detailed analytics and statistics for race results',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'features',
            'module': 'analytics',
            'dependencies': ['race_management']
        },
        'official_timing': {
            'name': 'Official Timing System',
            'description': 'Manual timing interface for officials with START/STOP buttons',
            'version': '2.1.6',
            'enabled': False,  # Disabled by default until fully tested
            'required': False,
            'category': 'features',
            'module': 'timing',
            'dependencies': ['race_management']
        },
        'athlete_registration': {
            'name': 'Athlete Self-Registration',
            'description': 'Allow athletes to self-register for events',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'features',
            'module': 'athlete_registration',
            'dependencies': ['race_management', 'user_management']
        },
        'reports': {
            'name': 'Report Generation',
            'description': 'Generate PDF and Excel reports for races and results',
            'version': '2.1.6',
            'enabled': True,
            'required': False,
            'category': 'features',
            'module': 'reports',
            'dependencies': ['race_management']
        },
        'gallery_manager': {
            'name': 'Gallery & Photo Manager',
            'description': 'Manage athlete/team photos and media assignments from backend.',
            'version': '3.0.3',
            'enabled': True,
            'required': False,
            'category': 'features',
            'module': 'gallery_manager',
            'dependencies': ['user_management']
        },
        'file_manager': {
            'name': 'File Explorer / File Manager',
            'description': 'Browse, upload, download, and delete managed files from backend.',
            'version': '3.0.3',
            'enabled': True,
            'required': False,
            'category': 'infrastructure',
            'module': 'file_manager',
            'dependencies': ['user_management']
        },
        'subscription_manager': {
            'name': 'SaaS Subscription Manager',
            'description': 'Manage client subscriptions, plans, lifecycle actions, and payment states.',
            'version': '3.0.3',
            'enabled': True,
            'required': False,
            'category': 'enterprise',
            'module': 'subscription_manager',
            'dependencies': ['user_management']
        }
    }


class PluginManager:
    """Manages plugin lifecycle: load, enable, disable, unload"""
    
    def __init__(self, config_file: str = 'plugins.json'):
        self.config_file = config_file
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_hooks: Dict[str, List[Callable]] = {}
        self._load_plugin_config()
    
    def _load_plugin_config(self):
        """Load plugin configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                    if isinstance(config, dict) and 'plugin_states' in config:
                        custom_plugins = config.get('custom_plugins', {})
                        for plugin_id, plugin_data in custom_plugins.items():
                            if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS and isinstance(plugin_data, dict):
                                custom_entry = plugin_data.copy()
                                custom_entry.setdefault('name', plugin_id)
                                custom_entry.setdefault('description', 'Custom plugin')
                                custom_entry.setdefault('version', '1.0.0')
                                custom_entry.setdefault('enabled', False)
                                custom_entry.setdefault('required', False)
                                custom_entry.setdefault('category', 'features')
                                custom_entry.setdefault('module', plugin_id)
                                custom_entry.setdefault('dependencies', [])
                                custom_entry['builtin'] = False
                                custom_entry['installed_via'] = custom_entry.get('installed_via', 'admin')
                                PluginRegistry.AVAILABLE_PLUGINS[plugin_id] = custom_entry

                        for plugin_id, settings in config.get('plugin_states', {}).items():
                            if plugin_id in PluginRegistry.AVAILABLE_PLUGINS and isinstance(settings, dict):
                                PluginRegistry.AVAILABLE_PLUGINS[plugin_id].update(settings)
                    else:
                        # Backward compatibility with older flat config format
                        for plugin_id, settings in config.items():
                            if plugin_id in PluginRegistry.AVAILABLE_PLUGINS and isinstance(settings, dict):
                                PluginRegistry.AVAILABLE_PLUGINS[plugin_id].update(settings)
            except Exception as e:
                logger.warning(f"Failed to load plugin config: {e}")
        else:
            self._save_plugin_config()
    
    def _save_plugin_config(self):
        """Save current plugin configuration to file"""
        try:
            plugin_states = {
                plugin_id: {
                    'enabled': plugin.get('enabled', False),
                    'last_modified': plugin.get('last_modified') or datetime.now().isoformat()
                }
                for plugin_id, plugin in PluginRegistry.AVAILABLE_PLUGINS.items()
            }

            custom_plugins = {
                plugin_id: {
                    'name': plugin.get('name', plugin_id),
                    'description': plugin.get('description', ''),
                    'version': plugin.get('version', '1.0.0'),
                    'enabled': plugin.get('enabled', False),
                    'required': plugin.get('required', False),
                    'category': plugin.get('category', 'features'),
                    'module': plugin.get('module', plugin_id),
                    'dependencies': plugin.get('dependencies', []),
                    'builtin': False,
                    'installed_via': plugin.get('installed_via', 'admin')
                }
                for plugin_id, plugin in PluginRegistry.AVAILABLE_PLUGINS.items()
                if not plugin.get('builtin', True)
            }

            config = {
                'plugin_states': plugin_states,
                'custom_plugins': custom_plugins
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")

    def install_plugin(self, plugin_id: str, plugin_data: Dict[str, Any]) -> bool:
        """Install a custom plugin into the registry and persist it."""
        if not plugin_id or plugin_id in PluginRegistry.AVAILABLE_PLUGINS:
            return False

        plugin_name = str(plugin_data.get('name', '')).strip()
        module_name = str(plugin_data.get('module', '')).strip()
        if not plugin_name or not module_name:
            return False

        raw_dependencies = plugin_data.get('dependencies', [])
        if isinstance(raw_dependencies, list):
            dependencies = [str(item).strip() for item in raw_dependencies if str(item).strip()]
        else:
            dependencies = []

        plugin_entry = {
            'name': plugin_name,
            'description': str(plugin_data.get('description', '')).strip() or 'Custom plugin module',
            'version': str(plugin_data.get('version', '1.0.0')).strip() or '1.0.0',
            'enabled': bool(plugin_data.get('enabled', False)),
            'required': False,
            'category': str(plugin_data.get('category', 'features')).strip().lower() or 'features',
            'module': module_name,
            'dependencies': dependencies,
            'builtin': False,
            'installed_via': 'admin',
            'last_modified': datetime.now().isoformat()
        }

        PluginRegistry.AVAILABLE_PLUGINS[plugin_id] = plugin_entry

        if plugin_entry['enabled']:
            self.load_plugin(plugin_id)

        self._save_plugin_config()
        logger.info(f"Plugin installed: {plugin_entry['name']} ({plugin_id})")
        return True

    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a custom plugin from the registry and persistence."""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            return False

        plugin = PluginRegistry.AVAILABLE_PLUGINS[plugin_id]

        if plugin.get('required', False):
            logger.warning(f"Cannot uninstall required plugin: {plugin_id}")
            return False

        if plugin.get('builtin', True):
            logger.warning(f"Cannot uninstall builtin plugin: {plugin_id}")
            return False

        blockers = self.get_disable_blockers(plugin_id)
        if blockers:
            logger.warning(
                f"Cannot uninstall plugin {plugin_id}; enabled dependents found: {', '.join(blockers)}"
            )
            return False

        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]

        del PluginRegistry.AVAILABLE_PLUGINS[plugin_id]
        self._save_plugin_config()
        logger.info(f"Plugin uninstalled: {plugin_id}")
        return True
    
    def load_plugin(self, plugin_id: str) -> bool:
        """Load a specific plugin into memory"""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            logger.error(f"Plugin {plugin_id} not found in registry")
            return False
        
        plugin_info = PluginRegistry.AVAILABLE_PLUGINS[plugin_id]
        
        if not plugin_info.get('enabled', False):
            logger.debug(f"Plugin {plugin_id} is disabled, skipping load")
            return False
        
        if plugin_id in self.loaded_plugins:
            logger.debug(f"Plugin {plugin_id} already loaded")
            return True
        
        try:
            # Dynamically import the plugin module
            module_name = plugin_info.get('module')
            if module_name:
                # Try to import the module
                try:
                    module = importlib.import_module(module_name)
                    self.loaded_plugins[plugin_id] = {
                        'module': module,
                        'info': plugin_info,
                        'loaded_at': datetime.now().isoformat()
                    }
                    logger.info(f"✅ Plugin loaded: {plugin_info['name']} ({plugin_id})")
                    return True
                except ImportError:
                    logger.warning(f"Module {module_name} not found, plugin {plugin_id} will be initialized later")
                    # Still mark as loaded even if module doesn't exist (for optional modules)
                    self.loaded_plugins[plugin_id] = {
                        'module': None,
                        'info': plugin_info,
                        'loaded_at': datetime.now().isoformat()
                    }
                    return True
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """Load all enabled plugins"""
        results = {}
        for plugin_id, plugin_info in PluginRegistry.AVAILABLE_PLUGINS.items():
            if plugin_info.get('enabled', False):
                results[plugin_id] = self.load_plugin(plugin_id)
        
        enabled_count = sum(1 for v in results.values() if v)
        logger.info(f"Loaded {enabled_count}/{len(results)} plugins")
        return results
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            return False
        
        plugin = PluginRegistry.AVAILABLE_PLUGINS[plugin_id]
        
        if plugin.get('required', False) and not plugin.get('enabled', False):
            logger.warning(f"Cannot disable required plugin: {plugin_id}")
            return False
        
        plugin['enabled'] = True
        plugin['last_modified'] = datetime.now().isoformat()
        
        # Load the plugin if not already loaded
        self.load_plugin(plugin_id)
        
        self._save_plugin_config()
        logger.info(f"Plugin enabled: {plugin['name']} ({plugin_id})")
        return True
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            return False
        
        plugin = PluginRegistry.AVAILABLE_PLUGINS[plugin_id]
        
        if plugin.get('required', False):
            logger.warning(f"Cannot disable required plugin: {plugin_id}")
            return False

        blockers = self.get_disable_blockers(plugin_id)
        if blockers:
            logger.warning(
                f"Cannot disable plugin {plugin_id}; enabled dependents found: {', '.join(blockers)}"
            )
            return False
        
        plugin['enabled'] = False
        plugin['last_modified'] = datetime.now().isoformat()
        
        # Unload the plugin if loaded
        if plugin_id in self.loaded_plugins:
            del self.loaded_plugins[plugin_id]
        
        self._save_plugin_config()
        logger.info(f"Plugin disabled: {plugin['name']} ({plugin_id})")
        return True

    def get_disable_blockers(self, plugin_id: str) -> List[str]:
        """Return enabled plugins that depend on the target plugin."""
        blockers = []
        for dependent_id, plugin in PluginRegistry.AVAILABLE_PLUGINS.items():
            dependencies = plugin.get('dependencies', []) or []
            if plugin_id in dependencies and plugin.get('enabled', False):
                blockers.append(dependent_id)
        return blockers
    
    def is_enabled(self, plugin_id: str) -> bool:
        """Check if a plugin is enabled"""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            return False
        return PluginRegistry.AVAILABLE_PLUGINS[plugin_id].get('enabled', False)
    
    def is_loaded(self, plugin_id: str) -> bool:
        """Check if a plugin is loaded in memory"""
        return plugin_id in self.loaded_plugins
    
    def get_plugin_info(self, plugin_id: str) -> Optional[Dict]:
        """Get detailed information about a plugin"""
        if plugin_id not in PluginRegistry.AVAILABLE_PLUGINS:
            return None
        
        plugin_info = PluginRegistry.AVAILABLE_PLUGINS[plugin_id].copy()
        plugin_info['plugin_id'] = plugin_id
        plugin_info['is_loaded'] = self.is_loaded(plugin_id)
        plugin_info['dependencies'] = plugin_info.get('dependencies', [])
        plugin_info['disable_blockers'] = self.get_disable_blockers(plugin_id)
        
        if plugin_id in self.loaded_plugins:
            plugin_info['loaded_at'] = self.loaded_plugins[plugin_id]['loaded_at']
        
        return plugin_info
    
    def get_all_plugins(self) -> List[Dict]:
        """Get information about all plugins"""
        return [self.get_plugin_info(plugin_id) 
                for plugin_id in PluginRegistry.AVAILABLE_PLUGINS.keys()]
    
    def get_plugins_by_category(self, category: str) -> List[Dict]:
        """Get all plugins in a specific category"""
        return [self.get_plugin_info(plugin_id)
                for plugin_id, plugin in PluginRegistry.AVAILABLE_PLUGINS.items()
                if plugin.get('category') == category]
    
    def get_enabled_plugins(self) -> List[Dict]:
        """Get all enabled plugins"""
        return [self.get_plugin_info(plugin_id)
                for plugin_id, plugin in PluginRegistry.AVAILABLE_PLUGINS.items()
                if plugin.get('enabled', False)]
    
    def toggle_plugin(self, plugin_id: str) -> bool:
        """Toggle plugin on/off"""
        is_enabled = self.is_enabled(plugin_id)
        if is_enabled:
            return self.disable_plugin(plugin_id)
        else:
            return self.enable_plugin(plugin_id)
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a callback for a plugin hook"""
        if hook_name not in self.plugin_hooks:
            self.plugin_hooks[hook_name] = []
        self.plugin_hooks[hook_name].append(callback)
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all registered callbacks for a hook"""
        results = []
        if hook_name in self.plugin_hooks:
            for callback in self.plugin_hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing hook {hook_name}: {e}")
        return results
    
    def get_stats(self) -> Dict:
        """Get plugin system statistics"""
        all_plugins = PluginRegistry.AVAILABLE_PLUGINS
        return {
            'total_plugins': len(all_plugins),
            'enabled_count': sum(1 for p in all_plugins.values() if p.get('enabled', False)),
            'loaded_count': len(self.loaded_plugins),
            'categories': list(set(p.get('category') for p in all_plugins.values())),
            'required_plugins': [pid for pid, p in all_plugins.items() if p.get('required', False)],
        }


# Global plugin manager instance
plugin_manager = PluginManager()
