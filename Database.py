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

# decided to use sqlite3 because we use really simple db operations. any ORM will just add overhead that really is not necessary
import sqlite3

class Database:
    def __init__(self):
        # If the database is busy doing any data sensitive operations, we WILL NOT RUN ANY UPDATES ON THE TORRENTLIST.
        self.isBusy = False



        pass