from dataclasses import dataclass
import random
import string


# generates a random 12 digit id
def random_id() -> int:
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=12))


# using dataclasses as its easier to save and retrieve info
@dataclass
class Client:
    rand_id: str  # Random ID constructed from 12 random chars
    client_name: str  # How client will be represented to the user
    user_agent: str  # The user agent that will report to the tracker
    port: int  # The port where we will report data
    upload_limit: int  # Limit in Bytes at how much client can upload
    download_limit: int  # Limit in Bytes at how much client can upload
    available_upload: int  # How much upload bandwidth is available in Bytes
    available_download: int  # How much upload bandwidth is available in Bytes
    peer_id: str  # A peer ID which is originated in the ORIGINAL torrent client. example for one: -AZ3020-


def create_from_db(db_payload) -> Client:
    pass


def create_from_user_input(rand_id, client_name, user_agent, port, upload_limit, download_limit, peer_id) -> Client:
    available_upload = upload_limit
    available_download = download_limit
    return Client(rand_id, client_name, user_agent, port, upload_limit, download_limit, available_upload,
                  available_download, peer_id)
