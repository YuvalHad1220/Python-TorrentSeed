import asyncio
import threading
import Database
import Website

from Announcement import main_loop


db_instance = Database.Database("torrents_and_clients.db")
torrent_list = db_instance.return_torrent_list()
client_list = db_instance.return_client_list()

def main(torrent_list, client_list, db_instance):
    asyncio.run(main_loop(torrent_list, client_list, db_instance))


threading.Thread(target=main, args=(torrent_list, client_list, db_instance)).start()
Website.main(torrent_list, client_list)

main(torrent_list, client_list, db_instance)