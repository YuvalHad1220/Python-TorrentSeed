#This is the engine of the download\upload faking mechanism.
#If conditions are right, we will take the amount we want from client and use it to download.


from random import randint
from Client import Client
from typing import List
from Torrent import Torrent

# returns 30-80 KBs
def slow_download_speed() -> int:
    return randint(10 * 1024, 50 * 1024)

# a weird algo that just always returns a low speed
def slow_upload_speed(torrent: Torrent) -> int:
        return torrent.upload_speed // (torrent.leechers ** 0.6)

# we will return a random speed somewhere between 50 - 90 % of the original speed
def random_speed(max_speed: int) -> int:
    return randint(max_speed * 50, max_speed * 90) // 100

def download_data(torrent: Torrent, client: Client) -> int:
    # we will first run a list of checks before running the algoritm

    # if torrent is completed
    if torrent.progress() == 100:
        return 0 

    # we want at least 2 seeders to run the algorithm. 
    if torrent.seeders <= 2:
        return 0

    available_bandwidth = client.available_download
    if available_bandwidth == 0:
        return 0

    max_download_speed = torrent.download_speed

    # if we have not a lot of seeders we will use slow speed to avoid getting caught
    if (torrent.seeders <= 3):
        max_download_speed = slow_download_speed()

    # we will use either available bandwidth or the max download speed
    bandwidth_to_use = min(available_bandwidth, max_download_speed)

    chosen_speed = random_speed(bandwidth_to_use)

    # if we want to download more than what we have left, we will fix it
    if chosen_speed + torrent.downloaded >= torrent.size:
        chosen_speed = torrent.size - torrent.downloaded

    return chosen_speed

# same principials as before.
def upload_data(torrent: Torrent, client: Client) -> int:
    
    # if we are downloading then
    if torrent.progress() != 100 and torrent.leechers == 1:
        return 0

    if torrent.ratio() > 3:
        return 0

    # if we dont have a lot of leechers
    if torrent.leechers <= 2:
        return 0

    # we cant upload data we dont have
    if torrent.progress() == 0:
        return 0

    available_bandwidth = client.available_upload
    # if no bandwidth is left. in the future we will try to fix it
    if available_bandwidth == 0:
        return 0



    max_upload_speed = torrent.upload_speed

    # will be a slow upload
    if torrent.leechers <= 4:
        max_upload_speed = slow_upload_speed(torrent)


    
    bandwidth_to_use = min(available_bandwidth, max_upload_speed)

    chosen_speed = random_speed(bandwidth_to_use)

    return chosen_speed



