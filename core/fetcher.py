import logging
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

def fetch_html(url: str, user_agent: str, timeout: int = 10, wait_until: str = "networkidle") -> BeautifulSoup:
    """
    Fetch and parse HTML content from a URL using Playwright.
    
    Args:
        url: The URL to fetch
        user_agent: User-Agent header string
        timeout: Request timeout in seconds (default: 10)
        wait_until: Playwright wait_until strategy (default: "networkidle")
    
    Returns:
        BeautifulSoup object
    
    Raises:
        PlaywrightTimeoutError: If the request times out
        Exception: For other errors
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()
            try:
                logger.info(f"Fetching URL: {url}")
                page.goto(url, wait_until=wait_until, timeout=timeout * 1000)
                html_content = page.content()
            finally:
                context.close()
                browser.close()

        logger.info(f"Successfully fetched URL: {url} (Length: {len(html_content)})")
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup
    except PlaywrightTimeoutError as e:
        logger.error(f"Request timeout for URL: {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching URL: {url}: {str(e)}")
        raise
