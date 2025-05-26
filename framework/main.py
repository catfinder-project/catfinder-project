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
import asyncio
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any
from .splash import SplashScreen
from .loader import Loader
from . import commands
from . import banners
from colored import fg, bg, attr

VERSION = "2.2025.001"
DEFAULT_CONFIG = {
    "loglevel": "debug",
    "modules_path": "framework/modules",
    "data_path": "data"
}


class Core:
    def __init__(self):
        self._ensure_data_directory()
        self.config = self._load_config()
        self.loop = asyncio.get_event_loop()
        self.loader = Loader()

        self.levels = {
            "debug": logging.DEBUG,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO
        }

    def _ensure_data_directory(self) -> None:
        Path("data").mkdir(exist_ok=True)
        if not Path("data/config.json").exists():
            with open("data/config.json", "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open("data/config.json", "r") as file:
                config = json.load(file)

                return {**DEFAULT_CONFIG, **config}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.warning(f"Using default config due to error: {e}")
            return DEFAULT_CONFIG

    async def main(self) -> None:
        """Main application entry point."""
        try:
            logger = logging.getLogger()
            logger.setLevel(self.levels.get(
                self.config["loglevel"], logging.INFO))

            with SplashScreen(logger=logger) as sp:
                sp.show()
                logger.info("Starting CatFinder v%s", VERSION)
                await self.loader.loadall()
                sp.close()

            self._show_startup_banner()

            while True:
                try:
                    command = input(
                        f"{fg(178)}┌[catfinder]-(main)\n└> {attr('reset')}").strip()
                    if command.lower() in ('exit', 'quit'):
                        break
                    if command:
                        result = await commands.run(command)
                        print(result)
                except KeyboardInterrupt:
                    print("\nUse 'exit' or 'quit' to exit.")
        except Exception as e:
            logging.critical(f"catfinder error: {e}")
            raise

    def _show_startup_banner(self) -> None:
        print(
            banners.startup.format(
                modules=self.loader.modules(),
                color=fg(178),
                background=bg(15),
                bgcolor=fg(0),
                reset=attr('reset'),
                version=VERSION
            )
        )


core = Core()
