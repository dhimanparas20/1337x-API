from core.orchestrator import fetch_site
from sites.pirate_bay.adapter import PirateBayAdapter

# Default User-Agent if none provided
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

pb_adapter = PirateBayAdapter()

def fetch(query, pgno=0, userAgent=DEFAULT_USER_AGENT):
    """
    Fetch and scrape torrent data from The Pirate Bay using the reusable core architecture.
    """
    if userAgent is None:
        userAgent = DEFAULT_USER_AGENT
        
    return fetch_site(pb_adapter, query, pgno, userAgent)
