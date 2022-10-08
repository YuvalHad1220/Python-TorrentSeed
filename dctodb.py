import sqlite3
from dataclasses import fields, asdict
import builtins
from typing import Type, Any


def _create_connection(db_filename):
    return sqlite3.connect(db_filename)


class dctodb:
    def __init__(self, dc: Type[Any], db_filename: str):
        self.dc: Type[Any] = dc
        self.db_filename: str = db_filename
        self.create_table()

    def create_table(self):
        command = f"CREATE TABLE IF NOT EXISTS {self.dc.__name__} (id integer PRIMARY KEY AUTOINCREMENT, "

        for field in fields(self.dc):
            match field.type:
                case builtins.int:
                    command += f"{field.name} integer, "

                case builtins.str:
                    command += f"{field.name} text, "

                case builtins.bool:
                    command += f"{field.name} boolean, "

                case builtins.bytes:
                    command += f"{field.name} binary, "

                case _:
                    raise Exception(f"unsupported data type: {field.type}")

        command = command[:-2]  # removing ', ' from command
        command += ");"  # closing the command
        conn = _create_connection(self.db_filename)
        cur = conn.cursor()
        cur.execute(command)
        conn.close()

    def insert(self, *instances_of_dc):
        var_names = [field.name for field in fields(instances_of_dc[0])]
        command = f"INSERT INTO {self.dc.__name__} ({','.join(var_names)}) VALUES ({'?,' * len(var_names)}"
        command = command[:-1]  # strip ','
        command += ")"

        val_list = [tuple(asdict(instance).values()) for instance in instances_of_dc]

        conn = _create_connection(self.db_filename)
        cur = conn.cursor()
        cur.executemany(command, val_list)
        conn.commit()
        conn.close()

    def fetch_all(self):
        conn = _create_connection(self.db_filename)
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {self.dc.__name__}")
        rows = cur.fetchall()
        conn.close()

        fetched = []
        # for each row we will iterate over every column and make sure the correct type in inserted

        for row in rows:
            row = row[1:]  # popping the id - it is not necessary
            args = (
                field.type(col) for field, col in zip(fields(self.dc), row)
            )  # initiating the args with their right type
            fetched.append(self.dc(*args))

        return fetched

    def update(self, find_by_field, *instances_of_dc):
        var_names = [field.name for field in fields(instances_of_dc[0])]
        command = f"UPDATE {self.dc.__name__} SET {''.join(f'{name} = ?,' for name in var_names)}"
        command = command[:-1]  # remove ','

        command += f" WHERE {find_by_field} = ?"

        # arg_list contains a tuple of values of all objects data to update COMBINED with the key
        arg_list = []
        for instance in instances_of_dc:
            vals = tuple(getattr(instance, field.name) for field in fields(instance))
            find_by = (getattr(instance, find_by_field),)

            arg_list.append(vals + find_by)

        conn = _create_connection(self.db_filename)
        c = conn.cursor()
        c.executemany(command, arg_list)
        conn.commit()
        conn.close()

    def delete(self, *instances_of_dc):
        var_names = [field.name for field in fields(instances_of_dc[0])]
        command = f"DELETE FROM {self.dc.__name__} WHERE {''.join(f'{name} = ? AND ' for name in var_names)}"
        command = command[:-4]  # remove '? AND' from query

        # a list of the tuples containing the value of all objects we want to remove
        val_list = [tuple(asdict(instance).values()) for instance in instances_of_dc]
        conn = _create_connection(self.db_filename)
        c = conn.cursor()
        c.executemany(command, val_list)
        conn.commit()
        conn.close()
