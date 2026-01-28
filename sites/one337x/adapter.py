import logging
import html
from typing import List, Any, Callable, Tuple, Optional
from bs4 import BeautifulSoup
from core.protocol import TorrentSiteAdapter
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

class One337xAdapter(TorrentSiteAdapter):
    BASE_URL = "https://www.1377x.to"
    
    def build_search_url(self, query: str, page: int) -> str:
        # 1337x URL pattern: https://www.1377x.to/category-search/{query}/Music/{pgno}/
        # Note: Original code hardcoded 'Music'. I will keep it for compatibility,
        # but ideally this should be configurable or inferred. 
        # The prompt asked to make it reusable "like Pirate Bay", so I'll stick to the existing logic.
        return f"{self.BASE_URL}/category-search/{query}/Music/{page}/"

    def validate_page(self, pgno: Any) -> int:
        try:
            number = int(pgno)
            if number > 0:
                return number
            logger.warning(f'Invalid page number "{pgno}", falling back to 1.')
            return 1
        except (TypeError, ValueError):
            logger.warning(f'Invalid page number "{pgno}", falling back to 1.')
            return 1

    def scrape_search_page(
        self, 
        soup: BeautifulSoup, 
        fetch_html: Callable[[str], BeautifulSoup], 
        user_agent: str
    ) -> List[dict]:
        data_list = []
        table = soup.find('table', class_='table-list table table-responsive table-striped')

        if table is None:
            logger.warning("No table found in the HTML")
            return data_list
        
        rows = table.find_all('tr')
        if len(rows) <= 1:
            logger.warning("Table found but no data rows present")
            return data_list
        
        for row in rows[1:]:
            try:
                columns = row.find_all('td')
                if len(columns) < 5:
                    logger.warning(f"Insufficient columns in row: expected at least 5, got {len(columns)}")
                    continue
                
                # Extract name and link
                name_cell = columns[0]
                name = name_cell.text.strip()
                
                links = name_cell.find_all('a')
                if len(links) < 2:
                    logger.warning(f"Insufficient links in name cell for row: {name}")
                    continue
                
                link = links[1]
                href = link.get('href')
                if not href:
                    logger.warning(f"No href found in link for row: {name}")
                    continue
                
                se = columns[1].text.strip()
                le = columns[2].text.strip()
                date = columns[3].text.strip()
                size = columns[4].text.strip()
                
                # Detail fetch
                complete_url = self.BASE_URL + href
                magnet, lst1, lst2, imgSrc = self._scrape_detail_page(complete_url, fetch_html)
                
                # Build data dictionary
                other_details = {}
                if lst1 and len(lst1) >= 5:
                    other_details = {
                        "category": lst1[0].text if len(lst1) > 0 else "N/A",
                        "type": lst1[1].text if len(lst1) > 1 else "N/A",
                        "language": lst1[2].text if len(lst1) > 2 else "N/A",
                        "uploader": lst1[4].text if len(lst1) > 4 else "N/A"
                    }
                else:
                    other_details = {
                        "category": "N/A",
                        "type": "N/A",
                        "language": "N/A",
                        "uploader": "N/A"
                    }
                
                if lst2 and len(lst2) >= 3:
                    other_details["downloads"] = lst2[0].text if len(lst2) > 0 else "N/A"
                    other_details["dateUploaded"] = lst2[2].text if len(lst2) > 2 else "N/A"
                else:
                    other_details.setdefault("downloads", "N/A")
                    other_details.setdefault("dateUploaded", "N/A")
                
                data = {
                    "name": name,
                    "Images": imgSrc,
                    "Seeders": se,
                    "Leechers": le,
                    "Date": date,
                    "Size": size,
                    "otherDetails": other_details,
                    "magnet": magnet
                }
                
                logger.debug(f"Scraped data for: {name}")
                data_list.append(data)
                
            except Exception as e:
                logger.error(f"Error processing row for {name if 'name' in locals() else 'unknown'}: {str(e)}")
                continue
                
        return data_list

    def _scrape_detail_page(self, url: str, fetch_html: Callable[[str], BeautifulSoup]) -> Tuple[str, Any, Any, Any]:
        """
        Helper to fetch and scrape the detail page.
        """
        try:
            soup = fetch_html(url)
        except Exception as e:
            logger.error(f"Failed to fetch detail page {url}: {str(e)}")
            return "Na", None, None, "Na"
        
        # Extract magnet link
        magnet = "Na"
        try:
            magnet_tag = soup.find(
                lambda tag: tag.name == "a"
                and "Magnet Download" in tag.get_text(strip=True)
            )
            if magnet_tag and magnet_tag.has_attr("href"):
                magnet = html.unescape(magnet_tag.get("href"))
        except Exception as e:
            logger.warning(f"Error extracting magnet for {url}: {str(e)}")
        
        # Extract images
        imgSrc = []
        try:
            images = soup.find_all("img", class_="img-responsive")
            for img in images:
                src = img.get("src")
                if src:
                    imgSrc.append(src)
            if not imgSrc:
                imgSrc = "Na"
        except Exception as e:
            logger.warning(f"Error extracting images for {url}: {str(e)}")
            imgSrc = "Na"
        
        # Extract detail lists
        lst1, lst2 = None, None
        try:
            lst = soup.find_all("ul", class_="list")
            if len(lst) >= 3:
                lst1 = lst[1].find_all("span") if len(lst) > 1 else None
                lst2 = lst[2].find_all("span") if len(lst) > 2 else None
        except Exception as e:
            logger.warning(f"Error extracting detail lists for {url}: {str(e)}")
        
        return magnet, lst1, lst2, imgSrc
