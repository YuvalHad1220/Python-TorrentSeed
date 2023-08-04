from dataclasses import dataclass

from TorrentSQL import TorrentSQL


# using dataclasses as its easier to save and retrieve info
@dataclass
class Torrent(TorrentSQL):
    temp_taken_download: int  # Temp var to hold how much download bandwidth we took from client to the current second
    temp_taken_upload: int  # Temp var to hold how much upload bandwidth we took from client to the current second

    def progress(self) -> float:
        return 100 * (self.downloaded / self.size)

    def ratio(self) -> float:
        return self.uploaded / (self.downloaded + 1)


    def __hash__(self):
        return hash((self.name, self.announce_url, self.info_hash))
def create_from_user_input(torrent_name, torrent_size, download_speed, upload_speed, announce_url, info_hash, client_id,
                           downloaded, uploaded) -> Torrent:
    # when we first add the torrent, we dont know if we can upload \ download. Therefore we will add the torrent with
    # no peers. amount of peers will be updated once we announce (start or resume)
    seeders = 0
    leechers = 0

    # we will want to announce as soon as we added the torrent
    time_to_announce = 0

    is_start_announced = False if downloaded == 0 else True
    is_finished_announced = False if (downloaded == 0 or downloaded // torrent_size != 1) else True
    temp_taken_download = 0
    temp_taken_upload = 0

    return Torrent(torrent_name, torrent_size, seeders, leechers, download_speed, upload_speed, is_start_announced,
                   is_finished_announced, announce_url, info_hash, time_to_announce, client_id, downloaded, uploaded,
                   temp_taken_download, temp_taken_upload)
