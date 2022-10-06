from dataclasses import dataclass


# using dataclasses as its easier to save and retrieve info
@dataclass
class Torrent:
    name: str
    size: str
    seeders: int  # amount of seeders
    leechers: int  # amount of leechers

    download_speed: int  # MAXIMUM download speed in Bytes
    upload_speed: int  # MAXIMUM upload speed in Bytes
    is_start_announced: bool  # if the torrent was already announced.
    announce_url: str  # Where we will announce torrent
    info_hash: bytes  # Data of torrent to announce

    time_to_announce: int  # How much seconds until we will announce the torrent

    client_id: int  # the id of the client. The reason we save the id and not a reference to the object is because it
    # is easier to both save and load, and neither the client or torrent has functions that work on each other

    downloaded: int  # amount of downloaded data
    uploaded: int  # amount of uploaded data

    temp_taken_download: int  # Temp var to hold how much download bandwidth we took from client to the current second
    temp_taken_upload: int  # Temp var to hold how much upload bandwidth we took from client to the current second

    def progress(self) -> int:
        return 100 * (self.downloaded / self.size)


def create_from_db(db_payload) -> Torrent:
    temp_taken_download = 0
    temp_taken_upload = 0
    pass


def create_from_user_input(torrent_name, torrent_size, download_speed, upload_speed, announce_url, info_hash, client_id,
                           downloaded, uploaded) -> Torrent:
    # when we first add the torrent, we dont know if we can upload \ download. Therefore we will add the torrent with no peers. 
    # amount of peers will be updated once we announce (start or resume)
    seeders = 0
    leechers = 0

    # we will want to announce as soon as we added the torrent
    time_to_announce = 0

    is_start_announced = False if downloaded == 0 else True

    temp_taken_download = 0
    temp_taken_upload = 0

    return Torrent(torrent_name, torrent_size, seeders, leechers, download_speed, upload_speed, is_start_announced,
                   announce_url, info_hash, time_to_announce, client_id, downloaded, uploaded, temp_taken_download,
                   temp_taken_upload)
