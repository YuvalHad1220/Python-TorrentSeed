from dataclasses import dataclass


# a class that we will save and retrieve from SQL. will not contain all the data we need and it will not be used while running the script - but we do use it to save and retireve info.

@dataclass
class ClientSQL:
    rand_id: str  # Random ID constructed from 12 random chars
    client_name: str  # How client will be represented to the user
    user_agent: str  # The user agent that will report to the tracker
    port: int  # The port where we will report data
    upload_limit: int  # Limit in Bytes at how much client can upload
    download_limit: int  # Limit in Bytes at how much client can upload
    peer_id: str  # A peer ID which is originated in the ORIGINAL torrent client. example for one: -AZ3020-

    def __hash__(self):
        return hash((self.rand_id, self.client_name))
