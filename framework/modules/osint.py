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
from bs4 import BeautifulSoup
from framework.loader import Loader
from colored import fg, bg, attr
import re
import json
import aiohttp
import asyncio
import logging

loader = Loader()


def get_config():
    with open("data/config.json", "r") as file:
        return json.load(file)


def set(config):
    with open("data/config.json", "w") as f:
        json.dump(config, f, indent=2)


def getJson(object_dict: dict, indent: int = 0) -> str:
    lines = []

    trig = f"{fg(77)}-{attr('reset')}"

    for key, value in object_dict.items():
        if isinstance(value, dict):
            lines.append("  " * indent + f"{trig} {key}")
            lines.extend(getJson(value, indent + 1).split("\n"))
        elif isinstance(value, list):
            lines.append("  " * indent + f"{trig} {key} LIST:")
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    lines.append("  " * (indent + 1) + f"[{i}]")
                    lines.extend(getJson(item, indent + 2).split("\n"))
                elif isinstance(item, list):
                    lines.append("  " * (indent + 1) + f"[{i}] LIST:")
                    lines.extend(
                        getJson({"key": item}, indent + 2).split("\n"))
                else:
                    lines.append("  " * (indent + 1) + f"[{i}]: {item}")
        else:
            lines.append("  " * indent + f"{trig} {key}: {value}")
    return "\n".join(lines)


@loader.module
class Osint:
    @loader.command(description="Search information by URL")
    async def website(query: str):
        url = f"https://sitecheck.sucuri.net/api/v3/?scan={query}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if not response.status == 200:
                    return "[-] Failed to get response."

                data = await response.json()
                logging.debug(data)

                print(f"[+] {query}")
                return getJson(data)

    @loader.command(description="Search with Nova")
    async def nova(query: str):
        url = f"https://api.proxynova.com/comb?query={query}&start=0&limit=100"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if not response.status == 200:
                    return "[-] Failed to get response."

                data = await response.json()
                logging.debug(data)

                count = data.get("count", None)
                lines = data.get("lines", [])

                print(f"[+] Found {count} results")
                for line in lines:
                    print(bg(77), fg(0), line, attr('reset'))

                return "[+] Done"

    @loader.command(description="Search in REVENG")
    async def reveng(query: str):
        url = f"https://reveng.ee/search?q={query}"
        data = ""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    text = await response.text()

                    soup = BeautifulSoup(text, 'html.parser')

                    rows = soup.select('table.table tbody tr.search-result')
                    if not rows:
                        return "No results found."

                    for row in rows:
                        name_elem = row.select_one(
                            'td:nth-child(2) .entity-prop-value')
                        source_elem = row.select_one('td:nth-child(4)')
                        birth_date_elem = row.select_one(
                            'td:nth-child(3) tr:nth-child(2) td:nth-child(2)')

                        name = name_elem.text.strip() if name_elem else "N/A"
                        source = source_elem.text.strip() if source_elem else "N/A"
                        birth_date = birth_date_elem.text.strip() if birth_date_elem else "N/A"

                        data += f"[{source}] {name}: {birth_date}\n"

        except aiohttp.ClientError as e:
            return f"An error occurred while making the request: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

        return data if data else "No results found."

    @loader.command(description="Search in NETRUBI.ru")
    async def netrubi(name: str):
        async with aiohttp.ClientSession() as session:
            url = "https://netrubi.ru/nomer/{}".format(
                name.replace("+7", "")
            )

            async with session.get(url) as response:
                text = await response.text()

                soup = BeautifulSoup(text, 'html.parser')

                phone_number = (
                    soup.find('h1').text.strip()
                    if soup.find('h1')
                    else "Not Found"
                )
                print("number :", phone_number)

                operator_info = (
                    soup.find(
                        'div', class_='wrap-section').find_all('p')[1].text.strip()
                    if soup.find('div', class_='wrap-section')
                    and len(soup.find('div', class_='wrap-section').find_all('p')) > 1
                    else "Not Found"
                )
                print("operator :", operator_info)

                region_info = (
                    soup.find(
                        'a', href="/telefonnie-kodi-gorodov/celabinskaa-oblast").text.strip()
                    if soup.find('a', href="/telefonnie-kodi-gorodov/celabinskaa-oblast")
                    else "Not Found"
                )
                print("region :", region_info)

                rating_value = (
                    soup.find('meta', itemprop='ratingValue')['content']
                    if soup.find('meta', itemprop='ratingValue')
                    else "-1"
                )
                print("rating :", rating_value)

                review_count = (
                    soup.find('meta', itemprop='reviewCount')['content']
                    if soup.find('meta', itemprop='reviewCount')
                    else "Not Found"
                )
                print("reviews :", review_count)

                for comment_item in soup.find_all('div', class_='comment-item'):
                    review_text = (
                        comment_item.find(
                            'div', itemprop='description').text.strip()
                        if comment_item.find('div', itemprop='description')
                        else "Not Found"
                    )
                    review_author = (
                        comment_item.find('span', itemprop='name').text.strip()
                        if comment_item.find('span', itemprop='name')
                        else "Not Found"
                    )
                    review_rating = (
                        comment_item.find('meta', itemprop='ratingValue')[
                            'content']
                        if comment_item.find('meta', itemprop='ratingValue')
                        else "Not Found"
                    )
                    print(review_text, "-", review_author, "|", review_rating)
        return "Done."

    @loader.command(description="Search by email")
    async def email(
        name: str,
        file: str = "./data/email.json"
    ):
        async with aiohttp.ClientSession() as session:
            with open(file) as f:
                data = json.load(f)

            for site, api_data in data.items():
                errortype = api_data["errorType"]
                url = api_data["url"].format(name)

                api = (
                    api_data["api"].format(name)
                    if "api" in api_data
                    else None)
                data = (
                    '{' + api_data["data"].format(name) + '}'
                    if "data" in api_data
                    else None)
                method = api_data["method"]

                try:
                    async with session.request(method, url, timeout=2, data=data) as response:
                        if errortype == "code":
                            if response.status == 200:
                                print(
                                    f"{bg(77)}{fg(0)} [+] {site} | {url} {attr('reset')}")
                        elif errortype == "message":
                            text = await response.text()
                            if not re.findall(api_data["message"]["error"], text):
                                print(
                                    f"{bg(77)}{fg(0)} [+] {site} | {url} {attr('reset')}")

                        if api:
                            async with session.request(method, api, timeout=2) as data_response:
                                print(getJson(await data_response.json()))
                except asyncio.TimeoutError:
                    print(
                        f"{bg(178)}{fg(0)} [!] {site} | TimeOut {attr('reset')}")

    @loader.command(description="Search by username")
    async def username(
            name: str,
            file: str = "./data/username.json"):
        async with aiohttp.ClientSession() as session:
            with open(file) as f:
                data = json.load(f)

            for site, api_data in data.items():
                errortype = api_data["errorType"]
                url = api_data["url"].format(name)

                api = (
                    api_data["api"].format(name)
                    if "api" in api_data
                    else None)
                data = (
                    '{' + api_data["data"].format(name) + '}'
                    if "data" in api_data
                    else None)
                method = api_data["method"]

                try:
                    async with session.request(method, url, timeout=2, data=data) as response:
                        if errortype == "code":
                            if response.status == 200:
                                print(
                                    f"{bg(77)}{fg(0)} [+] {site} | {url} {attr('reset')}")
                        elif errortype == "message":
                            text = await response.text()
                            if not re.findall(api_data["message"]["error"], text):
                                print(
                                    f"{bg(77)}{fg(0)} [+] {site} | {url} {attr('reset')}")

                        if api:
                            async with session.request(method, api, timeout=2) as data_response:
                                print(getJson(await data_response.json()))
                except asyncio.TimeoutError:
                    print(
                        f"{bg(178)}{fg(0)} [!] {site} | TimeOut {attr('reset')}")
