import html
import logging
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

s = HTMLSession()
baseURL = "https://thepiratebay.org"
defUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

def fetch(query, pgno=0, userAgent=defUserAgent):
    """
    Fetch and scrape torrent data from The Pirate Bay.
    
    Args:
        query: Search query string
        pgno: Page number (defaults to 0 if None)
        userAgent: User-Agent header string
    
    Returns:
        List of scraped data dictionaries or error message dictionary
    """
    data_list = []
    
    if query is None:
        logger.warning("Empty query received")
        return {"Message": "Empty Request"}
    
    if not isValidPageNumber(pgno):
        logger.warning(f'Invalid page number of "{pgno}", using default page number of 0. Reason: page number must be a non-negative integer. Result: falling back to page 0.')
        pgno = 0
    else:
        pgno = int(pgno)
    
    try:
        # Pirate Bay URL pattern: https://thepiratebay.org/search.php?q={query}&audio=on&search=Pirate+Search&page={pgno}&orderby=
        url = f"{baseURL}/search.php?q={query}&audio=on&search=Pirate+Search&page={pgno}&orderby="
        logger.info(f"Fetching data for query: {query}, page: {pgno}")
        
        soup = getSoup(url, userAgent)
        if soup is None:
            logger.error(f"Failed to get soup for URL: {url}")
            return {"Message": "Failed to fetch page"}
        
        scrapeData(soup, data_list)
        
    except (RequestException, HTTPError) as e:
        logger.error(f"HTTP/Network error during fetch: {str(e)}")
        return {"Message": f"Network error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {str(e)}")
        return {"Message": f"Error occurred: {str(e)}"}

    if len(data_list) == 0:
        logger.info(f"No data found for query: {query}, page: {pgno}")
        return {"Message": "No data found"}

    logger.info(f"Successfully fetched {len(data_list)} items for query: {query}, page: {pgno}")
    return data_list

def getSoup(url, userAgent, timeout=10):
    """
    Fetch and parse HTML content from a URL.
    """
    try:
        # requests_html might need header adjustment or handling of JS if strictly required, 
        # but for now we try standard get.
        r = s.get(url, headers={'User-Agent': userAgent}, timeout=timeout)
        r.raise_for_status()
        logger.info(f"HTML Found: {r.text}")
        soup = BeautifulSoup(r.text, 'html.parser')
        return soup
    except Timeout:
        logger.error(f"Request timeout for URL: {url}")
        raise
    except ConnectionError as e:
        logger.error(f"Connection error for URL: {url}: {str(e)}")
        raise
    except HTTPError as e:
        status_code = e.response.status_code if hasattr(e, 'response') and e.response is not None else "unknown"
        logger.error(f"HTTP error {status_code} for URL: {url}: {str(e)}")
        raise
    except RequestException as e:
        logger.error(f"Request failed for URL: {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching URL: {url}: {str(e)}")
        raise

def scrapeData(soup, data_list):
    """
    Scrape data from the parsed HTML soup.
    """
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
                # Get text but be careful of hidden inputs if they exist and are unwanted, 
                # though text usually gets only visible text or all text.
                # The sample shows <input type="hidden"> inside. .text will include it if it has text, 
                # but input usually doesn't have text content.
                size = size_tag.get_text().strip()
                # Clean up if necessary (e.g. remove "Size" label if present, though sample assumes just value)
            
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
                "Images": "Na", # No images in list view usually
                "otherDetails": {
                    "uploader": uploader,
                    "category": category
                }
            }
            
            data_list.append(data)
            
        except Exception as e:
            logger.error(f"Error parsing entry: {str(e)}")
            continue

def isValidPageNumber(pgno):
    try:
        number = int(pgno)
        return number >= 0
    except (TypeError, ValueError):
        return False
