"""
Where we will control all announces.
"""
import asyncio
import sqlite3
import urllib.parse
import httpx
from Client import Client
from typing import List

from Database import Database
from Torrent import Torrent
from DownloadUploadEngine import download_data, upload_data
import bencoding


# an announcement function
async def announce(httpx_client: httpx.AsyncClient, TYPE: str, torrent: Torrent, client: Client):
    # if it's not a regular announcement in a speficied interval, than we need to declare it. so we use a dictionary which lets us declare the event type
    event = {"start": "started",
             "end": "completed",
             "resume": None}

    HTTP_HEADERS = {
        "Accept-Encoding": "gzip",
        "User-Agent": client.user_agent
    }

    HTTP_PARAMS = {
        "info_hash": urllib.parse.quote_from_bytes(torrent.info_hash),
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

    # we must place the event type right after "left" and before anything else. so we will have to add that manually
    # and then merge the dictionaries
    if event[TYPE]:
        HTTP_PARAMS["event"] = event[TYPE]

    HTTP_PARAMS = urllib.parse.urlencode(HTTP_PARAMS)
    HTTP_PARAMS = HTTP_PARAMS.replace("%25", "%")
    URL = torrent.announce_url + f"?{HTTP_PARAMS}"
    try:
        req = await httpx_client.get(URL, headers=HTTP_HEADERS)

    except:
        return
    info = bencoding.decode(req.content)

    try:
        torrent.time_to_announce = info[b"interval"]
    except:
        torrent.time_to_announce = 1800

    try:
        torrent.seeders = int(info[b"complete"])
    except:
        torrent.seeders = 0
    try:
        torrent.leechers = int(info[b"incomplete"])
    except:
        torrent.leechers = 0

    if TYPE == "start":
        print("start announced")
        torrent.is_start_announced = True

    elif TYPE == "end":
        print("end announced")
        torrent.is_finish_announced = True

    else:
        print("resume announced")


def create_connection(db_file):
    return sqlite3.connect(db_file)


async def main_loop(torrent_list: List[Torrent], client_list: List[Client], db_instance: Database):
    async with httpx.AsyncClient() as httpx_client:
        while True:
            tasks = []
            # we will use a set to avoid duplicates
            torrents_to_update = set()
            # first we will take care of announcements.
            for torrent in torrent_list:
                client = client_list[torrent.client_id]
                if not torrent.is_start_announced:
                    tasks.append(announce(httpx_client, "start", torrent, client))
                    torrents_to_update.add(torrent)
                # smaller than zero because fresh torrents wont be announced that way
                if torrent.time_to_announce < 0:
                    tasks.append(announce(httpx_client, "resume", torrent, client))
                    torrents_to_update.add(torrent)

                if torrent.progress() == 100 and not torrent.is_finish_announced:
                    tasks.append(announce(httpx_client, "end", torrent, client))
                    torrents_to_update.add(torrent)

                # every five seconds we will update the db
                if torrent.time_to_announce % 5 == 0:
                    torrents_to_update.add(torrent)

            if tasks:
                print("Total announcements need to be made:", len(tasks))

            await asyncio.gather(*tasks)
            if torrents_to_update:
                db_instance.update_torrents(torrents_to_update)
                print("total torrents updated:", len(torrents_to_update))

            for torrent in torrent_list:
                client = client_list[torrent.client_id]

                to_download = download_data(torrent, client)
                torrent.temp_taken_download = to_download
                client.available_download -= to_download
                torrent.downloaded += to_download

                to_upload = upload_data(torrent, client)
                torrent.temp_taken_upload = to_upload
                client.available_upload -= to_upload
                torrent.uploaded += to_upload

            for torrent in torrent_list:
                client.available_upload += torrent.temp_taken_upload
                torrent.temp_taken_upload = 0
                client.available_download += torrent.temp_taken_download
                torrent.temp_taken_download = 0

                torrent.time_to_announce -= 1

            await asyncio.sleep(1)
