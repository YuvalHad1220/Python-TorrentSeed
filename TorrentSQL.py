from dataclasses import dataclass


# a class that we will save and retrieve from SQL. will not contain all the data we need and it will not be used while running the script - but we do use it to save and retireve info.

@dataclass
class TorrentSQL:
    name: str
    size: int
    seeders: int  # amount of seeders
    leechers: int  # amount of leechers
    download_speed: int  # MAXIMUM download speed in Bytes
    upload_speed: int  # MAXIMUM upload speed in Bytes
    is_start_announced: bool  # if the torrent was already announced.
    is_finish_announced: bool # if the torrent was already finished
    announce_url: str  # Where we will announce torrent
    info_hash: bytes  # Data of torrent to announce
    time_to_announce: int  # How much seconds until we will announce the torrent

    client_id: int  # the id of the client. The reason we save the id and not a reference to the object is because it
    # is easier to both save and load, and neither the client or torrent has functions that work on each other
    downloaded: int  # amount of downloaded data
    uploaded: int  # amount of uploaded data
