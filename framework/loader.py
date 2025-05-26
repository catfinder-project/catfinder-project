"""                                                                           
 _|    _|              _|      _|_|_|              _|      _|_|            
 _|    _|    _|_|    _|_|_|_|  _|    _|  _|  _|_|        _|      _|    _|  
 _|_|_|_|  _|    _|    _|      _|    _|  _|_|      _|  _|_|_|_|  _|    _|  
 _|    _|  _|    _|    _|      _|    _|  _|        _|    _|      _|    _|  
 _|    _|    _|_|        _|_|  _|_|_|    _|        _|    _|        _|_|_|  
                                                                       _|  
                                                                   _|_|    

    this code was written by 🍬 HotDrify
             hotdrify.t.me
"""
import os
import sys
import importlib
import logging
import asyncio
import json
from functools import wraps

MODULES = {}
COMMANDS = {}
SYSTEM = ("core",)


class Validators:
    @staticmethod
    def String(value):
        return isinstance(value, str)

    @staticmethod
    def Int(value):
        return isinstance(value, int)

    @staticmethod
    def Float(value):
        return isinstance(value, float)


class Value:
    def __init__(self, key, description, value, validator=None):
        self.key = key
        self.description = description
        self.value = value
        self.validator = validator

        if validator and not validator(value):
            raise ValueError(f"Value '{value}' for '{key}' is not valid.")


class Config:
    def __init__(self):
        self.values = {}

    def add(self, value: Value):
        self.values[value.key] = value

    def get(self, key):
        return self.values.get(key).value if key in self.values else None

    def __repr__(self):
        return str({key: value.value for key, value in self.values.items()})


class Loader:
    def __init__(self):
        self.PATH = os.path.join("framework", "modules")
        self.config = Config()
        self.load_config()

    def load_config(self):
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            if not os.path.exists("data/database.json"):
                logging.warning(
                    "Configuration file not found, a new one will be created.")
                return

            with open("data/database.json", "r") as f:
                data = json.load(f)
                for module_name, values in data.get("config", {}).items():
                    for key, value in values.items():
                        self.Config(
                            Value(key, f"Configuration for {key} in {module_name}", value))
        except FileNotFoundError:
            logging.warning(
                "Configuration file not found, a new one will be created.")
        except json.JSONDecodeError:
            logging.error("Error reading the configuration file.")
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")

    def save_config(self):
        config_data = {"config": {}}
        for key, value in self.config.values.items():
            module_name = value.key.split('.')[0]
            if module_name not in config_data["config"]:
                config_data["config"][module_name] = {}
            config_data["config"][module_name][value.key] = value.value

        with open("data/database.json", "w") as f:
            json.dump(config_data, f, indent=4)

    def Config(self, *values: Value):
        for value in values:
            self.config.add(value)
        self.save_config()

    async def load(self, module_name: str) -> None:
        logging.debug(f"Loading module {module_name}")
        try:
            module = importlib.import_module(os.path.join(
                self.PATH, module_name).replace("/", "."))
        except ImportError as error:
            logging.error(f"Module {module_name} import error: {error}")
            return
        except Exception as error:
            logging.error(f"Module {module_name} error: {error}")
            return

        MODULES[module_name] = {"module": module}

        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and hasattr(attr, 'command'):
                if attr_name != "Loader":
                    logging.debug(f"Registering command {attr_name}")
                    COMMANDS[attr_name] = {
                        "working": True,
                        "attr": attr,
                        "description": getattr(attr, 'description', 'No description available.')
                    }

    async def unload(self, module_name: str) -> None:
        if module_name in SYSTEM:
            raise Exception("Is system module!")

        logging.debug(f"Unloading module {module_name}")
        commands_to_remove = [name for name in COMMANDS if COMMANDS[name]
                              ["attr"].__module__ == f"framework.modules.{module_name}"]

        for command_name in commands_to_remove:
            logging.debug(f"Removing command {command_name}")
            COMMANDS.pop(command_name)

        MODULES.pop(module_name, None)
        sys.modules.pop(f"framework.modules.{module_name}", None)

    def modules(self) -> int:
        count = 0
        for module_name in os.listdir("framework/modules"):
            if module_name.endswith(".py"):
                count += 1
        return count

    async def loadall(self) -> None:
        logging.debug("Loading all modules")
        tasks = []
        for module_name in os.listdir(self.PATH):
            if module_name.endswith(".py"):
                tasks.append(self.load(module_name[:-3]))
        await asyncio.gather(*tasks)

    def module(self, cls):
        logging.debug(f"Registering module {cls.__name__}")

        @wraps(cls)
        def wrapper(*args, **kwargs):
            instance = cls(*args, **kwargs)
            MODULES[cls.__name__] = instance
            return instance
        return wrapper

    def command(self, name=None, description=None):
        def decorator(func):
            logging.debug(f"Registering command {func.__name__}")

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            wrapper.command = True

            if name:
                wrapper.name = name
            else:
                wrapper.name = func.__name__
            COMMANDS[wrapper.name] = {
                "working": True,
                "attr": wrapper,
                "description": description
            }

            return wrapper
        return decorator
