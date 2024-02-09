"""
Where we will control all announces.
https://stackoverflow.com/questions/48007453/asynchronous-http-calls-using-aiohttp-asyncio-fail-with-cannot-connect-to-host
"""
import asyncio
import random
import sqlite3
import threading
import time
import urllib.parse

import aiohttp as aiohttp
from Client import Client
from typing import List

from Database import Database
from Torrent import Torrent
from DownloadUploadEngine import download_data, upload_data
import bencoding
import socket


# an announcement function
async def announce(aiohttp_client: aiohttp.ClientSession, TYPE: str, torrent: Torrent, client: Client):
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

    # try:
    async with aiohttp_client.get(URL, headers=HTTP_HEADERS,) as resp:
        content = await resp.read()
        info = bencoding.decode(content)


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
        torrent.is_start_announced = True

    if TYPE == "end":
        torrent.is_finish_announced = True


def create_connection(db_file):
    return sqlite3.connect(db_file)

# a helper func that decreses time that we will never run out of sync.
# this is a temp solutin, not a fix
# def decrease_time(torrentList):
#     while True:
#         for torrent in torrentList:
#             torrent.time_to_announce -= 30
#         time.sleep(30)
async def main_loop(torrent_list: List[Torrent], client_list: List[Client], db_instance: Database):
    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False
    )

    # # will decrease time without bother
    # threading.Thread(target=decrease_time, args=(torrent_list,)).start()

    timeout = aiohttp.ClientTimeout(total=5)
    aiohttp_client = aiohttp.ClientSession(connector=conn, trust_env=True, timeout=timeout)
    async with aiohttp_client as session:
        while True:
            tasks = []
            # we will use a set to avoid duplicates
            torrents_to_update = set()
            clients_to_update = set()
            # first we will take care of announcements.
            for torrent in torrent_list:
                client = client_list[torrent.client_id]
                if not torrent.is_start_announced:
                    tasks.append(announce(session, "start", torrent, client))
                    torrents_to_update.add(torrent)
                # smaller than zero because fresh torrents wont be announced that way
                if torrent.time_to_announce <= 0:
                    tasks.append(announce(session, "resume", torrent, client))
                    torrents_to_update.add(torrent)

                if torrent.progress() == 100 and not torrent.is_finish_announced:
                    tasks.append(announce(session, "end", torrent, client))
                    torrents_to_update.add(torrent)

                # every five seconds we will update the db
                if  torrent.temp_taken_download != 0 or torrent.temp_taken_upload != 0:
                    torrents_to_update.add(torrent)
                    clients_to_update.add(client)
            if tasks:
                print("Total announcements need to be made:", len(tasks))
                exceptions = await asyncio.gather(*tasks, return_exceptions=True)
                errors = [exception for exception in exceptions if exception is not None]
                if len(errors) > 0: 
                    print("Total errors:" ,len([exception for exception in exceptions if exception is not None]))
                print("done announcing")

            if torrents_to_update:
                print("torrents to save to db:", len(torrents_to_update))
                db_instance.update_torrents(torrents_to_update)
            if clients_to_update:
                db_instance.update_clients(clients_to_update)

            for torrent in torrent_list:
                client = client_list[torrent.client_id]

                to_download = download_data(torrent, client) * 30
                torrent.temp_taken_download = to_download
                client.available_download -= to_download
                torrent.downloaded += to_download

                to_upload = upload_data(torrent, client) * 30
                torrent.temp_taken_upload = to_upload
                client.available_upload -= to_upload
                torrent.uploaded += to_upload

            for torrent in torrent_list:
                client = client_list[torrent.client_id]
                # we will update the client speed but we wont take it away from torrent because we need it to print speed in website
                client.available_upload += torrent.temp_taken_upload
                client.available_download += torrent.temp_taken_download

            for torrent in torrent_list:
                torrent.time_to_announce -= 30

            time.sleep(30)
