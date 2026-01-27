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
baseURL = "https://www.1377x.to" 
defUserAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"  

def fetch(query, pgno, userAgent=defUserAgent):
    """
    Fetch and scrape torrent data from 1337x.
    
    Args:
        query: Search query string
        pgno: Page number (defaults to 1 if None)
        userAgent: User-Agent header string
    
    Returns:
        List of scraped data dictionaries or error message dictionary
    """
    data_list = []
    
    if query is None:
        logger.warning("Empty query received")
        return {"Message": "Empty Request"}
    
    if not isValidPageNumber(pgno):
        logger.warning(f'Invalid page number of "{pgno}", using default page number of 1. Reason: page number must be a positive integer. Result: falling back to page 1.')
        pgno = 1
    
    try:
        url = f"https://www.1377x.to/category-search/{query}/Music/{pgno}/"
        logger.info(f"Fetching data for query: {query}, page: {pgno}")
        
        soup = getSoup(url, userAgent)
        if soup is None:
            logger.error(f"Failed to get soup for URL: {url}")
            return {"Message": "Failed to fetch page"}
        
        scrapeData(soup, userAgent, data_list)
        
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
    
    Args:
        url: The URL to fetch
        userAgent: User-Agent header string
        timeout: Request timeout in seconds (default: 10)
    
    Returns:
        BeautifulSoup object or None if request fails
    
    Raises:
        RequestException: For network-related errors
        HTTPError: For HTTP error responses
    """
    try:
        r = s.get(url, headers={'User-Agent': userAgent}, timeout=timeout)
        r.raise_for_status()  # Raises HTTPError for bad status codes (4xx, 5xx)
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

def scrapeData(soup, userAgent, data_list):
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
            
            # Extract name and link with bounds checking
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
            complete_url = baseURL + href
            
            magnet, lst1, lst2, imgSrc = scrapeMagnet(complete_url, userAgent)
            
            # Build data dictionary with proper error handling
            try:
                other_details = {}
                if lst1 and len(lst1) >= 5:
                    other_details = {
                        "category": lst1[0].text if len(lst1) > 0 else "N/A",
                        "type": lst1[1].text if len(lst1) > 1 else "N/A",
                        "language": lst1[2].text if len(lst1) > 2 else "N/A",
                        "uploader": lst1[4].text if len(lst1) > 4 else "N/A"
                    }
                else:
                    logger.warning(f"Insufficient detail list 1 items for: {name}")
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
                    logger.warning(f"Insufficient detail list 2 items for: {name}")
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
            except (IndexError, AttributeError, TypeError) as e:
                logger.error(f"Error building data dictionary for {name}: {str(e)}")
                data = {"error": f"Failed to scrape data for {name}", "name": name}
            except Exception as e:
                logger.error(f"Unexpected error building data dictionary for {name}: {str(e)}")
                data = {"error": f"Failed to scrape data for {name}", "name": name}
            
            logger.debug(f"Scraped data for: {name}")
            data_list.append(data)
            
        except (IndexError, AttributeError) as e:
            logger.error(f"Error parsing row data: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error processing row: {str(e)}")
            continue
    
def scrapeMagnet(complete_url, userAgent): 
    """
    Scrape magnet link, images, and detail lists from a torrent detail page.
    
    Args:
        complete_url: Full URL to the torrent detail page
        userAgent: User-Agent header string
    
    Returns:
        Tuple of (magnet, lst1, lst2, imgSrc)
    """
    try:
        soup = getSoup(complete_url, userAgent)
    except (RequestException, HTTPError) as e:
        logger.error(f"Failed to fetch page for magnet scraping: {complete_url}: {str(e)}")
        return "Na", None, None, "Na"
    except Exception as e:
        logger.error(f"Unexpected error fetching page for magnet scraping: {complete_url}: {str(e)}")
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
        else:
            logger.debug(f"No magnet link found for: {complete_url}")
    except AttributeError as e:
        logger.warning(f"Error finding magnet tag for {complete_url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error extracting magnet link for {complete_url}: {str(e)}")
    
    # Extract images
    imgSrc = []
    try:
        images = soup.find_all("img", class_="img-responsive")
        for img in images:
            src = img.get("src")
            if src:
                imgSrc.append(src)
        if not imgSrc:
            logger.debug(f"No images found for: {complete_url}")
            imgSrc = "Na"
    except AttributeError as e:
        logger.warning(f"Error finding images for {complete_url}: {str(e)}")
        imgSrc = "Na"
    except Exception as e:
        logger.error(f"Unexpected error extracting images for {complete_url}: {str(e)}")
        imgSrc = "Na"
    
    # Extract detail lists
    lst1, lst2 = None, None
    try:
        lst = soup.find_all("ul", class_="list")
        if len(lst) < 3:
            logger.warning(f"Insufficient list elements found for {complete_url}: expected at least 3, got {len(lst)}")
        else:
            lst1 = lst[1].find_all("span") if len(lst) > 1 else None
            lst2 = lst[2].find_all("span") if len(lst) > 2 else None
    except (IndexError, AttributeError) as e:
        logger.warning(f"Error extracting detail lists for {complete_url}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error extracting detail lists for {complete_url}: {str(e)}")
    
    return magnet, lst1, lst2, imgSrc   

# Helpers
def isValidPageNumber(pgno):
    try:
        number = int(pgno)
        return number > 0
    except (TypeError, ValueError):
        return False
