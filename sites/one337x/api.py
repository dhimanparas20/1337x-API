from core.orchestrator import fetch_site
from sites.one337x.adapter import One337xAdapter

# Default User-Agent if none provided
DEFAULT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

x1337_adapter = One337xAdapter()

def fetch(query, pgno=1, userAgent=DEFAULT_USER_AGENT):
    """
    Fetch and scrape torrent data from 1337x using the reusable core architecture.
    """
    if userAgent is None:
        userAgent = DEFAULT_USER_AGENT
        
    return fetch_site(x1337_adapter, query, pgno, userAgent)
