from typing import TypedDict, List, Union, Dict

class TorrentDetails(TypedDict, total=False):
    category: str
    type: str
    language: str
    uploader: str
    downloads: str
    dateUploaded: str

class TorrentResult(TypedDict):
    name: str
    magnet: str
    Seeders: str
    Leechers: str
    Size: str
    Date: str
    Images: Union[str, List[str]]
    otherDetails: Dict[str, str]
