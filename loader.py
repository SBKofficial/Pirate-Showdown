import importlib
import pkgutil
import logging

def load_plugins(application):
    """Dynamically loads all modules in the plugins directory."""
    import plugins
    for loader, module_name, is_pkg in pkgutil.walk_packages(plugins.__path__, plugins.__name__ + "."):
        module = importlib.import_module(module_name)
        if hasattr(module, "register"):
            module.register(application)
            logging.info(f"Loaded plugin: {module_name}")
