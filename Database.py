"""
The Database part of the project.
Here the torrents and clients will be saved. We could also retrieve clients and torrents through functions here.

The auto-saving process will be as follows:
1. Every minute -> we will save all the torrents. We dont need to update the clients because they are fairly static
2. Once a torrent is started (extremly useful for when we add torrents from user, for example) -> we will add the torrent to the db, nothing else is changed
3. Once a torrent is finished -> we will update the torrent data in db

4. Once a client is created -> For obvious reasons (The client shouldnt be dynamic so we dont need to update it)

This way we will minimize the chances that the app will close unexpectedly and MAJOR updates to the state of the torrents is not saved.

Also - the logic here is that the torrent's main loop JUST WHEN the database is not busy. Therefore we will not alter any data that might not be saved bcz the database is busy

"""

from typing import List
from dctodb import dctodb
from Client import Client
from Torrent import Torrent


class Database:
    def __init__(self, db_filename):
        # If the database is busy doing any data sensitive operations, we WILL NOT RUN ANY UPDATES ON THE TORRENTLIST.
        self.clientConn = dctodb(Client, db_filename)
        self.torrentConn = dctodb(Torrent, db_filename)

    def return_client_list(self) -> List[Client]:
        return self.clientConn.fetch_all()

    def return_torrent_list(self) -> List[Client]:
        return self.torrentConn.fetch_all()

    def update_client(self, client):
        self.clientConn.update("rand_id", client)


    def update_torrent(self, torrent):
        self.torrentConn.update("info_hash", torrent)


    def update_torrents(self, torrents):
        self.torrentConn.update("info_hash", *torrents)

    def add_torrent(self, torrent):
        self.torrentConn.insert(torrent)


    def add_torrents(self, torrents):
        self.torrentConn.insert(*torrents)


    def add_client(self, client):
        self.clientConn.insert(client)
