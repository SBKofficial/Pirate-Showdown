import importlib
import pkgutil
import logging
import plugins

def load_plugins(application):
    """Dynamically loads all modules in the plugins directory."""
    for loader, module_name, is_pkg in pkgutil.walk_packages(plugins.__path__, plugins.__name__ + "."):
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, "register"):
                module.register(application)
                logging.info(f"✅ Loaded plugin: {module_name}")
        except Exception as e:
            logging.error(f"❌ Failed to load plugin {module_name}: {e}")
