import os
import time
import random
import logging
from collections import deque
from colored import fg, bg, attr
from datetime import datetime

from . import banners


class SplashScreen:
    def __init__(self, logger, log_dir="logs"):
        self.cat_art = random.choice(banners.cats).format(
            color=fg(178),
            background=bg(15),
            bgcolor=fg(0),
            reset=attr('reset'),
        )

        self.splash_text = random.choice(banners.splash_texts).format(
            background=bg(15),
            color=fg(0),
            reset=attr('reset'),
        )

        self.cat_lines = self.cat_art.strip('\n').split('\n')
        self.cat_height = len(self.cat_lines)
        self.cat_width = max(len(line) for line in self.cat_lines)
        self.logger = logger
        self.log_buffer = deque(maxlen=1000)
        self._running = False
        self.log_dir = log_dir
        self._setup_log_handlers()

    def _setup_log_handlers(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        date_str = datetime.now().strftime("%Y-%m-%d")
        log_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        class SplashLogHandler(logging.Handler):
            def __init__(self, splash):
                super().__init__()
                self.splash = splash

            def emit(self, record):
                msg = self.format(record)
                self.splash._add_log_message(msg)

        self.splash_handler = SplashLogHandler(self)
        self.splash_handler.setFormatter(log_formatter)

        self.level_handlers = {
            level: logging.FileHandler(
                os.path.join(self.log_dir, f"{date_str}_{level_name}.log"),
                encoding='utf-8'
            )
            for level, level_name in [
                (logging.DEBUG, "DEBUG"),
                (logging.INFO, "INFO"),
                (logging.WARNING, "WARNING"),
                (logging.ERROR, "ERROR"),
                (logging.CRITICAL, "CRITICAL"),
            ]
        }

        for handler in self.level_handlers.values():
            handler.setFormatter(log_formatter)

        root_logger = logging.getLogger()

        root_logger.addHandler(self.splash_handler)
        for level, handler in self.level_handlers.items():
            handler.setLevel(level)
            root_logger.addHandler(handler)

    def _add_log_message(self, message):
        self.log_buffer.append(message)
        if self._running:
            self._redraw()

    def _clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def _redraw(self):
        term_width, term_height = os.get_terminal_size()
        self._clear_screen()

        for row in range(term_height - 1):
            log_index = len(self.log_buffer) - term_height + row + 1
            log_line = self.log_buffer[log_index] if 0 <= log_index < len(
                self.log_buffer) else ""
            print(log_line[:term_width])

        cat_col = max(0, (term_width - self.cat_width) // 2)
        cat_row = max(0, (term_height - self.cat_height - 1) //
                      2)

        for i, line in enumerate(self.cat_lines):
            print(f"\033[{cat_row + i + 1};{cat_col + 1}H{line}")

        splash_text_centered = self.splash_text.center(term_width)
        print(f"\033[{term_height};1H{splash_text_centered}")

    def show(self):
        self._running = True
        self._redraw()

    def close(self):
        if self._running:
            self._running = False
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.splash_handler)
            for handler in self.level_handlers.values():
                root_logger.removeHandler(handler)
                handler.close()
            self._clear_screen()

    def __enter__(self):
        self.show()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
