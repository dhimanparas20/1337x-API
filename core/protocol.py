from typing import Protocol, List, Any, Callable, Optional
from bs4 import BeautifulSoup

class TorrentSiteAdapter(Protocol):
    """
    Protocol for torrent site adapters.
    Each site (Pirate Bay, 1337x, etc.) must implement this interface.
    """

    def build_search_url(self, query: str, category: Optional[str], page: int) -> str:
        """
        Build the search URL for the given query, category (optional), and page number.
        """
        ...

    def validate_page(self, pgno: Any) -> int:
        """
        Validate and coerce the page number.
        Returns the valid page number to use (or a default if invalid).
        """
        ...

    def scrape_search_page(
        self, 
        soup: BeautifulSoup, 
        fetch_html: Callable[[str], BeautifulSoup], 
        user_agent: str
    ) -> List[dict]:
        """
        Scrape the search page soup and return a list of torrent dictionaries.
        
        Args:
            soup: The parsed HTML of the search page.
            fetch_html: A callable to fetch additional URLs (e.g. detail pages).
                       Signature: (url: str) -> BeautifulSoup.
            user_agent: The user agent string to use for additional fetches.
            
        Returns:
            List of dictionaries matching the standard torrent result schema.
        """
        ...
