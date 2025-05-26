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
from framework.loader import Loader
from framework.utils import generate
from urllib.parse import urlparse
from colored import fg, attr
import sqlite3
import pandas as pd
import os
from tqdm import tqdm


class DatabaseManager:
    def __init__(self, db_path='cache/databases.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def load_csv_to_db(self, csv_path):
        table_name = os.path.splitext(os.path.basename(csv_path))[
            0].replace("-", "_")
        df = pd.read_csv(csv_path, low_memory=False)

        with tqdm(total=len(df), desc=csv_path) as pbar:
            df.to_sql(table_name, self.conn, if_exists='replace', index=False)
            pbar.update(len(df))

        for column in df.columns:
            column_name = column.replace("-", "_")
            index_name = f'idx_{column_name}'
            self.cursor.execute(
                f'CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column_name});')

        self.conn.commit()

    def search_in_db(self, query):
        query = query.replace('_', '-')

        for table in self.get_tables():
            columns = self.get_columns(table)
            sql_query = f'SELECT * FROM {table} WHERE ' + \
                " OR ".join([f'{col} LIKE ?' for col in columns])
            parameters = [f'%{query}%' for _ in columns]
            try:
                self.cursor.execute(sql_query, parameters)
                results = self.cursor.fetchall()
                for result in results:
                    print(f"[+] Found in {table}: {result}")
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")

    def get_tables(self):
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        return [table[0] for table in self.cursor.fetchall()]

    def get_columns(self, table):
        self.cursor.execute(f"PRAGMA table_info({table});")
        return [column[1] for column in self.cursor.fetchall()]

    def close(self):
        self.conn.close()


class Search:
    @staticmethod
    def load_databases(databases):
        db_manager = DatabaseManager()
        for database in databases:
            if database.endswith(".csv"):
                db_manager.load_csv_to_db(os.path.join("databases/", database))
        db_manager.close()

    @staticmethod
    def search_files(query):
        db_manager = DatabaseManager()
        db_manager.search_in_db(query)
        db_manager.close()


loader = Loader()

# config = loader.Config(
#     loader.Value(
#         name = "name",
#         description = "description",
#         value = "value",
#         validator = loader.Validators.String
#     )
# )


@loader.module
class DBManager:
    @loader.command(description="Load CSV files into the database and search")
    async def search(query: str):
        databases = os.listdir("databases/")
        print(f"[+] Loading {len(databases)} files into the database...")
        Search.load_databases(databases)

        print(f"[+] Searching for: '{query}'")
        Search.search_files(query)

        return "[+] Done"

    @loader.command(description="Manage installed databases")
    async def databases():
        databases = [
            f" {database} "
            for database in os.listdir("databases/")
            if os.path.isfile(os.path.join("databases/", database))
        ]

        index = generate([
            " + new database ",
            *databases
        ])

        if index == 0:
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

                    os.makedirs("databases", exist_ok=True)

                    path = os.path.join("databases", filename)

                    with open(path, "wb") as file:
                        file.write(text)

                    return "Installed!"
        else:
            selected = databases[index - 1].strip()
            remove = generate([
                " Yes ",
                " No ",
            ], title=f"Remove {selected} file?")

            path = os.path.join("databases/", selected)

            if remove == 0:
                os.remove(path)
                return "Removed!"
            else:
                return "OK"
