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

main_loop(TorrentList, ClientList)
