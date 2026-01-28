import logging
from typing import List, Any, Callable
from bs4 import BeautifulSoup
from core.protocol import TorrentSiteAdapter

logger = logging.getLogger(__name__)

class PirateBayAdapter(TorrentSiteAdapter):
    BASE_URL = "https://thepiratebay.org"
    
    def build_search_url(self, query: str, page: int) -> str:
        # Pirate Bay URL pattern: https://thepiratebay.org/search.php?q={query}&audio=on&search=Pirate+Search&page={pgno}&orderby=
        return f"{self.BASE_URL}/search.php?q={query}&audio=on&search=Pirate+Search&page={page}&orderby="

    def validate_page(self, pgno: Any) -> int:
        try:
            number = int(pgno)
            if number >= 0:
                return number
            logger.warning(f'Invalid page number "{pgno}", falling back to 0.')
            return 0
        except (TypeError, ValueError):
            logger.warning(f'Invalid page number "{pgno}", falling back to 0.')
            return 0

    def scrape_search_page(
        self, 
        soup: BeautifulSoup, 
        fetch_html: Callable[[str], BeautifulSoup], 
        user_agent: str
    ) -> List[dict]:
        data_list = []
        entries = soup.find_all('li', class_='list-entry')
        
        if not entries:
            logger.warning("No list entries found in the HTML")
            return data_list
        
        for entry in entries:
            try:
                # Initialize default values
                name = "Na"
                magnet = "Na"
                seeders = "Na"
                leechers = "Na"
                size = "Na"
                date = "Na"
                uploader = "Na"
                category = "Na"
                
                # Extract Name
                name_tag = entry.find('span', class_='item-title')
                if name_tag:
                    name = name_tag.text.strip()
                
                # Extract Magnet
                icons_span = entry.find('span', class_='item-icons')
                if icons_span:
                    magnet_tag = icons_span.find('a', href=lambda h: h and h.startswith('magnet:'))
                    if magnet_tag:
                        magnet = magnet_tag['href']
                
                # Extract Seeders
                seed_tag = entry.find('span', class_='item-seed')
                if seed_tag:
                    seeders = seed_tag.text.strip()
                
                # Extract Leechers
                leech_tag = entry.find('span', class_='item-leech')
                if leech_tag:
                    leechers = leech_tag.text.strip()
                
                # Extract Size
                size_tag = entry.find('span', class_='item-size')
                if size_tag:
                    size = size_tag.get_text().strip()
                
                # Extract Date
                date_tag = entry.find('span', class_='item-uploaded')
                if date_tag:
                    date = date_tag.text.strip()
                
                # Extract Uploader
                user_tag = entry.find('span', class_='item-user')
                if user_tag:
                    uploader = user_tag.text.strip()
                
                # Extract Category
                type_tag = entry.find('span', class_='item-type')
                if type_tag:
                    category = type_tag.text.strip()

                # Build data dictionary
                data = {
                    "name": name,
                    "magnet": magnet,
                    "Seeders": seeders,
                    "Leechers": leechers,
                    "Size": size,
                    "Date": date,
                    "Images": "Na", 
                    "otherDetails": {
                        "uploader": uploader,
                        "category": category
                    }
                }
                
                data_list.append(data)
                
            except Exception as e:
                logger.error(f"Error parsing entry: {str(e)}")
                continue
                
        return data_list
