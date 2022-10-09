import asyncio
import os
import sqlite3
import threading

import Database
import Website
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


def parse_size(amount, type):
    match type:
        case 'b':
            return amount

        case 'kb':
            return amount * (10 ** 3)

        case 'mb':
            return amount * (10 ** 6)


def add_torrents_from_folder():
    download_speed = parse_size(2, 'mb')
    upload_speed = parse_size(50, 'kb')

    fresh_torrent_list = []
    for torrent in os.listdir("torrents"):
        torr = parse(f"torrents/{torrent}")

        new_tor = tor_create(torr['torrent_name'], torr['torrent_size'], download_speed, upload_speed,
                             torr['announce_url'], torr['file_hash'], 0, 0, 0)

        fresh_torrent_list.append(new_tor)

        os.remove(f"torrents/{torrent}")

    return fresh_torrent_list


db_instance = Database.Database("torrents_and_clients.db")
fresh_torrents = add_torrents_from_folder()
if fresh_torrents:
    db_instance.add_torrents(fresh_torrents)
torrent_list = db_instance.return_torrent_list()
client_list = db_instance.return_client_list()

if len(client_list) == 0:
    new_cl = cli_create(random_id(), "only client for now", Clients[0]['User-Agent'], 25565, parse_size(300, 'kb'),
                        parse_size(20, 'mb'), Clients[0]['peerID'])
    db_instance.add_client(new_cl)
    client_list.append(new_cl)


def main(torrent_list, client_list, db_instance):
    asyncio.run(main_loop(torrent_list, client_list, db_instance))


threading.Thread(target=main, args=(torrent_list, client_list, db_instance)).start()
Website.main(torrent_list, client_list)

# main(torrent_list, client_list, db_instance)