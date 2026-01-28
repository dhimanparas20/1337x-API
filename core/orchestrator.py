import logging
import functools
from typing import Union, List, Dict, Any
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from core.protocol import TorrentSiteAdapter
from core.fetcher import fetch_html

logger = logging.getLogger(__name__)

def fetch_site(
    adapter: TorrentSiteAdapter, 
    query: Union[str, None], 
    pgno: Any, 
    user_agent: str
) -> Union[List[Dict[str, Any]], Dict[str, str]]:
    """
    Orchestrate the fetching and scraping process for a given site adapter.
    
    Args:
        adapter: The site adapter instance to use.
        query: The search query.
        pgno: The page number (raw input).
        user_agent: The user agent string to use.
        
    Returns:
        A list of torrent dictionaries or an error dictionary.
    """
    if not query:
        logger.warning("Empty query received")
        return {"Message": "Empty Request"}
    
    page = adapter.validate_page(pgno)
    
    try:
        url = adapter.build_search_url(query, page)
        logger.info(f"Fetching data for query: {query}, page: {page} via {adapter.__class__.__name__}")
        
        soup = fetch_html(url, user_agent)
        
        # Create a partial fetcher bound with the user agent for any detail page fetches
        fetch_partial = functools.partial(fetch_html, user_agent=user_agent, timeout=10)
        
        data_list = adapter.scrape_search_page(soup, fetch_partial, user_agent)
        
    except PlaywrightTimeoutError as e:
        logger.error(f"Timeout during fetch: {str(e)}")
        return {"Message": f"Timeout error: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {str(e)}")
        return {"Message": f"Error occurred: {str(e)}"}

    if not data_list:
        logger.info(f"No data found for query: {query}, page: {page}")
        return {"Message": "No data found"}

    logger.info(f"Successfully fetched {len(data_list)} items for query: {query}, page: {page}")
    return data_list
