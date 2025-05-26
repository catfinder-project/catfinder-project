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
from framework.loader import Loader, COMMANDS, MODULES
from framework.utils import generate
from framework.main import VERSION
from urllib.parse import urlparse
from colored import fg, bg, attr
import logging
import aiohttp
import json
import sys
import os


def get_config(file="data/config.json"):
    with open(file, "r") as file:
        return json.load(file)


def set(config, file="data/config.json"):
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)


def view_file(filename):
    try:
        with open(f"logs/{filename}", "r") as f:
            lines = f.readlines()

        if not lines:
            return "Log file is empty"

        page = 0
        page_size = 20
        total_pages = (len(lines) // page_size +
                       (1 if len(lines) % page_size else 0))

        while True:
            os.system("clear")
            print()

            start = page * page_size
            end = start + page_size
            for line in lines[start:end]:
                print(line.strip())

            print()
            print(f"{bg(15)}{fg(0)} file: {filename} | ({page+1}/{total_pages}) ")
            print(f" n - next page | p - prev page | q - quit {attr('reset')}")

            choice = input("> ").lower()

            if choice == 'n' and page < total_pages - 1:
                page += 1
            elif choice == 'p' and page > 0:
                page -= 1
            elif choice == 'q':
                break

    except Exception as e:
        return f"Error reading log file: {e}"


loader = Loader()


@loader.module
class Core:
    @loader.command(description="Print all commands")
    async def help():
        text = f"The CatFinder v{VERSION}\n"
        for command, cmd_config in COMMANDS.items():
            if cmd_config["working"]:
                description = cmd_config["description"]
                if not description:
                    description = "No description available"

                text += f"- {command}: {description}\n"
        return text.rstrip("\n")

    @loader.command(description="General settings")
    async def settings():
        config = get_config()
        index = generate([
            " Configurator ",
            " API credits ",
            " Clear cache ",
            " Log level ",
            " Commands ",
            " Modules ",
            " Restart ",
            " Proxy ",
            " Logs "
        ])

        if index == 1:
            credits = config["credits"]
            api = generate([f" {api} " for api in credits.keys()])

            keys = list(credits.keys())
            name = keys[api]

            print("description: ", config["credits"][name]["description"])

            key = input(f"{fg(77)}┌[catfinder]-(API-key)\n└> {attr('reset')}")
            config["credits"][name]["auth"] = key
            set(config)
            return "api key setted!"

        if index == 2:
            os.remove("cache/databases.db")
            return "Removed!"

        if index == 3:
            levels = [
                "warning",
                "debug",
                "error",
                "info"
            ]
            level = generate([f" {level} " for level in levels])
            config["loglevel"] = levels[level]
            logging.debug(config)
            set(config)

            restart = generate([
                " Yes ",
                " No "
            ], title="To apply this setting, do I need to restart?")

            if restart == 0:
                os.system("clear")
                os.execl(
                    sys.executable,
                    sys.executable,
                    "-m",
                    "framework",
                )
            else:
                return "please restart"

        if index == 4:
            all_commands = list(COMMANDS.keys())
            logging.debug(all_commands)
            command = generate([f" {command_name} " for command_name in all_commands],
                               title="Select commands to disable", select=True)
            for index in command:
                name = all_commands[index]
                COMMANDS[name]["working"] = False
                logging.debug(COMMANDS[name])
            return "Commands is disabled!"

        if index == 5:
            all_modules = list(MODULES.keys())
            modules = [
                f" {module_name} "
                for module_name in all_modules
            ]

            logging.debug(all_modules)
            module = generate(
                [
                    " + new module ",
                    *modules
                ],
                title="Select module to unload")

            if module == 0:
                url = input(f"{fg(77)}┌[catfinder]-(url)\n└> {attr('reset')}")
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=2) as response:
                        if response.status != 200:
                            return f"[!] Failed to get response: {response.status}"

                        content_disposition = response.headers.get(
                            "Content-Disposition", None)
                        if content_disposition:
                            filename = content_disposition.split('filename=')[
                                1].strip('"')
                        else:
                            filename = os.path.basename(urlparse(url).path)

                        text = await response.read()
                        path = os.path.join("framework", "modules", filename)
                        logging.debug(path)

                        with open(path, "wb") as file:
                            file.write(text)

                        load_path = path[:-3].replace("/", ".")
                        logging.debug(load_path)

                        await loader.load(filename[-3])

                        return "Installed!"

            name = all_modules[module - 1]

            try:
                await loader.unload(name)
            except Exception as error:
                return f"Failed to unload module: {error}"

            remove = generate([
                " Yes ",
                " No "
            ], title="Remove from storage?")
            if remove == 0:
                os.remove(f"framework/modules/{name}.py")
                return "Removed!"
            if remove == 1:
                return "Unloaded!"

        if index == 6:
            os.system("clear")
            os.execl(
                sys.executable,
                sys.executable,
                "-m",
                "framework",
            )

        if index == 7:
            proxy = input(f"{fg(77)}┌[catfinder]-(proxy)\n└> {attr('reset')}")
            config["proxy"] = proxy
            logging.debug(config)
            set(config)
            return "proxy setted!"

        if index == 8:
            try:
                log_files = [f for f in os.listdir(
                    "logs") if os.path.isfile(os.path.join("logs", f))]

                if not log_files:
                    return "No log files found in logs directory"

                selected = generate(
                    [f" {log_file} " for log_file in log_files],
                    title="Select log file to view"
                )

                if selected < len(log_files) - 1:
                    view_file(log_files[selected])

            except Exception as e:
                return f"Error accessing logs: {e}"
