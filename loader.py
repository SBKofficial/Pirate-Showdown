import importlib
import pkgutil
import logging
import plugins

def load_plugins(application):
    """
    Dynamically scans the /plugins directory and imports all modules.
    It then calls the register() function in each file to activate commands.
    """
    # walk_packages looks inside the 'plugins' package directory
    for loader, module_name, is_pkg in pkgutil.walk_packages(plugins.__path__, plugins.__name__ + "."):
        try:
            # Import the file (e.g., plugins.start)
            module = importlib.import_module(module_name)
            
            # Check if the file has a 'register' function and run it
            if hasattr(module, "register"):
                module.register(application)
                logging.info(f"✅ Loaded plugin: {module_name}")
            else:
                logging.warning(f"⚠️ Plugin {module_name} is missing a register() function.")
                
        except Exception as e:
            logging.error(f"❌ Failed to load plugin {module_name}: {e}")
