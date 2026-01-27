import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch(query, pgno, userAgent=None):
    """
    Return a test response for Pirate Bay.
    """
    logger.info(f"Test fetch for Pirate Bay - Query: {query}, Page: {pgno}")
    
    return [
        {
            "name": f"Test Torrent for {query}",
            "Images": "Na",
            "Seeders": "100",
            "Leechers": "50",
            "Date": "2026-01-26",
            "Size": "1.23 GiB",
            "otherDetails": {
                "uploader": "Tester",
                "status": "This is a test response"
            },
            "magnet": "magnet:?xt=urn:btih:test"
        }
    ]
