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
from .loader import Loader, COMMANDS

import logging
import inspect

loader = Loader()


async def run(command):
    logging.debug(f"Running {command}")
    command_name, *args = command.split()
    if command_name in COMMANDS:
        logging.debug(f"Found {command_name}")

        if not COMMANDS[command_name]["working"]:
            return "[!] Command is disabled!"
        function = COMMANDS[command_name]["attr"](*args)
        # arguments = inspect.getfullargspec(function).args

        try:
            if inspect.iscoroutine(function):
                return await function
            else:
                return function
        except TypeError as error:
            logging.error(f"Command {command_name} error: {error}")
            return "[!] Command arguments required! {}"
        except Exception as e:
            logging.error(f"[!] Command {command_name} error: {e}")
            return "[!] Command error, check logs"
    else:
        logging.debug(f"Command {command_name} not found")
        return "[!] Command not found!"
