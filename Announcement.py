"""
Where we will control all announces.
"""
import time

from Client import Client
from typing import List
from Torrent import Torrent
from DownloadUploadEngine import download_data, upload_data
import bencoding
import requests


# an announcement function
def announce(TYPE: str, torrent: Torrent, client: Client):
    # if its not a regular announcement in a speficied interval, than we need to declare it. so we use a dictionary which lets us declare the event type
    event = {"start": "started",
             "end": "completed",
             "resume": None}

    HTTP_HEADERS = {
        "Accept-Encoding": "gzip",
        "User-Agent": client.user_agent
    }

    HTTP_PARAMS = {
        "info_hash": torrent.info_hash,
        "peer_id": client.peer_id + client.rand_id,
        "port": client.port,
        "uploaded": int(torrent.uploaded),
        "downloaded": int(torrent.downloaded),
        "left": int(torrent.size - torrent.downloaded),
        "compact": 1,
        "numwant": 200,
        "supportcrypto": 1,
        "no_peer_id": 1
    }

    # we must place the event type right after "left" and before anything else. so we will have to add that manually and then merge the dictionaries 
    if event[TYPE]:
        HTTP_PARAMS["event"] = event[TYPE]

    req = requests.get(torrent.announce_url, params=HTTP_PARAMS, headers=HTTP_HEADERS)
    print(HTTP_PARAMS)

    info = bencoding.decode(req.content)
    print(info)
    torrent.time_to_announce = info[b"interval"]
    torrent.seeders = int(info[b"complete"])
    torrent.leechers = int(info[b"incomplete"])

    if TYPE == "start":
        torrent.is_start_announced = True


def main_loop(TorrentList: List[Torrent], ClientList: List[Client]):
    while True:
        for torrent in TorrentList:
            client = ClientList[torrent.client_id]
            # first we will announce start, if needed. then it will also fix the issue of time_to_announce equals zero right when adding torrent from user
            if torrent.is_start_announced == False:
                announce("start", torrent, client)
                continue

            if torrent.time_to_announce == 0:
                announce("resume", torrent, client)
                continue

            if torrent.progress() == 100:
                announce("end", torrent, client)
                continue

            toDownload = download_data(torrent, client)
            torrent.downloaded += toDownload
            client.available_download += toDownload

            toUpload = upload_data(torrent, client)
            torrent.uploaded += toUpload
            client.available_upload += toUpload

            torrent.time_to_announce -= 1
            print(client)
            print(torrent)
            print("-------")

        time.sleep(1)
