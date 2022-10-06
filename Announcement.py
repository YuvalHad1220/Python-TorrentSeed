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
    info = bencoding.decode(req.content)
    torrent.time_to_announce = info[b"interval"]
    torrent.seeders = int(info[b"complete"])
    torrent.leechers = int(info[b"incomplete"])

    if TYPE == "start":
        torrent.is_start_announced = True


def main_loop(TorrentList: List[Torrent], ClientList: List[Client]):
    while True:
        # first part - here we will run all the torrents, announce if need, and then download\upload according to current limitations
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
            torrent.temp_taken_download = toDownload
            client.available_download -= toDownload
            torrent.downloaded += toDownload

            toUpload = upload_data(torrent, client)
            torrent.temp_taken_upload = toUpload
            client.available_upload -= toUpload
            torrent.uploaded += toUpload

        # second part of loop - here we will return the taken bandiwdth and also make the torrent closer to announce
        for torrent in TorrentList:
            print(client)
            print(torrent)
            print("-------")
            client.available_upload += torrent.temp_taken_upload
            torrent.temp_taken_upload = 0
            client.available_download += torrent.temp_taken_download
            torrent.temp_taken_download = 0

            torrent.time_to_announce -= 1


        time.sleep(1)
