from dataclasses import dataclass

from ClientSQL import ClientSQL


# using dataclasses as its easier to save and retrieve info
@dataclass
class Client(ClientSQL):
    """TEMP VARIABLES THAT DO NOT NEED TO BE SAVED:"""
    available_upload: int  # How much upload bandwidth is available in Bytes
    available_download: int  # How much upload bandwidth is available in Bytes
    total_downloaded: int  # a temp variable that will be used to display total download in each client via the website
    total_uploaded: int  # same temp variable
    download_speed: int  # a temp variable for website
    upload_speed: int  # a temp variable for website

    def __hash__(self):
        return hash((self.rand_id, self.client_name))

def create_from_user_input(rand_id, client_name, user_agent, port, upload_limit, download_limit, peer_id) -> Client:
    available_upload = upload_limit
    available_download = download_limit
    total_downloaded = 0
    total_uploaded = 0
    download_speed = 0
    upload_speed = 0
    return Client(rand_id, client_name, user_agent, port, upload_limit, download_limit, peer_id, available_upload, available_download, total_downloaded, total_uploaded, download_speed, upload_speed)