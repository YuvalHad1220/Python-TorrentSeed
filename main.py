import sqlite3

from Client import create_from_user_input as cli_create, random_id
from Torrent import create_from_user_input as tor_create
from Announcement import main_loop
from parseTorrentFile import parse

# clients to choose from
Clients = [{"Name": "qBittorrent 4.3.1",
            "peerID": "-qB4310-",
            "User-Agent": "qBittorrent/4.3.1"
            },
           {"Name": "qBittorrent 4.3.0",
            "peerID": "-qB4300-",
            "User-Agent": "qBittorrent/4.3.0"
            },
           {"Name": "qBittorrent 4.2.5",
            "peerID": "-qB4250-",
            "User-Agent": "qBittorrent/4.2.5"
            },
           {"Name": "qBittorrent 4.2.3",
            "peerID": "-qB4230-",
            "User-Agent": "qBittorrent/4.2.3"
            },
           {"Name": "qBittorrent 4.2.1",
            "peerID": "-qB4210-",
            "User-Agent": "qBittorrent/4.2.1"
            },
           {"Name": "Transmission 3.00",
            "peerID": "-TR3000-",
            "User-Agent": "Transmission/3.00"
            },
           {"Name": "uTorrent 2.2.1",
            "peerID": "-UT2210-",
            "User-Agent": "uTorrent/2210(25110)"
            }]

download_speed = 3200
upload_speed = 50

torrent1 = parse("Shower & locker room big compilation pack.torrent")
torrent1 = tor_create(torrent1["torrent_name"], torrent1["torrent_size"], download_speed, upload_speed, torrent1["announce_url"], torrent1["file_hash"], 0, 0, 0)
print(torrent1.size)
# print(torrent1, torrent2, torrent3)

client = cli_create(rand_id=random_id(), client_name="my first client", user_agent=Clients[0]["User-Agent"], port=25565, upload_limit=100, download_limit=10000, peer_id=Clients[0]["peerID"])

# print(client)

ClientList = [client]
TorrentList = [torrent1]

#main_loop(TorrentList, ClientList)
from dataclasses import dataclass, fields
import builtins
class dctdb:

    def __init__(self, dc: dataclass, conn):
        self.dc = dc
        self.conn = conn
        self.create_table()

    def create_table(self):
        CREATE_COMMAND = "CREATE TABLE IF NOT EXISTS "

        _create_command = self.dc.__name__ + '(id integer PRIMARY KEY AUTOINCREMENT, '

        for field in fields(self.dc):
            match field.type:
                case builtins.int:
                    _create_command += field.name + " integer, "

                case builtins.str:
                    _create_command += field.name + " text, "

                case builtins.bool:
                    _create_command += field.name + " boolean, "

                case builtins.bytes:
                    _create_command += field.name + " binary, "

                case _:
                    print(field.type)
                    exit(-1)

        _create_command = _create_command[:-2]

        CREATE_COMMAND += _create_command + ");"

        c = self.conn.cursor()
        c.execute(CREATE_COMMAND)
        return True

    def add_to_table(self, instance_of_dc):
        INSERT_COMMAND = "INSERT INTO " + self.dc.__name__ + "("

        _insert_command = ','.join(field.name for field in fields(self.dc))

        INSERT_COMMAND += _insert_command + ") VALUES (" + ("?,"*len(fields(instance_of_dc)))[:-1] + ")"

        c = self.conn.cursor()
        tup = tuple(getattr(instance_of_dc, field.name) for field in fields(instance_of_dc))
        c.execute(INSERT_COMMAND, tup)
        self.conn.commit()
        return True

    def fetch_all_from_table(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM " + self.dc.__name__)

        rows = cur.fetchall()
        for row in rows:
            for item in row:
                print(type(item))
        return [self.dc(*row[1:]) for row in rows]

    def update(self, instance_of_dc, find_by_field_name):
        UPDATE_COMMAND = "UPDATE " +self.dc.__name__ + " SET "
        _update_command = ''.join(f"{field.name} = ?, " for field in fields(self.dc))[:-2]
        UPDATE_COMMAND += _update_command + f" WHERE {find_by_field_name} = ?"
        c = self.conn.cursor()
        tup = tuple(getattr(instance_of_dc, field.name) for field in fields(instance_of_dc)) + (getattr(instance_of_dc, find_by_field_name),)

        c.execute(UPDATE_COMMAND, tup)
        self.conn.commit()


    def delete(self, instance_of_dc):
        DELETE_COMMAND = "DELETE FROM " +self.dc.__name__ +" WHERE "
        _delete_command = ''.join(f"{field.name} = ? AND " for field in fields(self.dc))[:-5]

        DELETE_COMMAND += _delete_command + ";"
        print(DELETE_COMMAND)

        c = self.conn.cursor()
        tup = tuple(getattr(instance_of_dc, field.name) for field in fields(instance_of_dc))

        c.execute(DELETE_COMMAND, tup)
        self.conn.commit()


def create_connection(db_file):
    return sqlite3.connect(db_file)
uri = "db.db"
conn = create_connection(uri)
import Client

client_db = dctdb(Client.Client, conn)
import Torrent

client_db = dctdb(Client.Client, conn)
torrent_db = dctdb(Torrent.Torrent, conn)

torrent_db.create_table()
client_db.create_table()

torrent_db.add_to_table(torrent1)
client_db.add_to_table(client)

torrent_db.fetch_all_from_table()