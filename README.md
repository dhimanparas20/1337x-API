# 1337x-API

## Introduction

A modular, reusable **Playwright & BeautifulSoup** web-scraping API that fetches torrent information from both **1337x** and **The Pirate Bay**. The architecture is extensible, so new torrent sites can be added with minimal effort.

**Tech:** Fast headless Chrome via Playwright, BeautifulSoup parser, Flask/REST, clean Python ``Protocol`` adapters.

### Supported Sites
- **1337x** – table-based search + detail-page magnet/image fetch
- **The Pirate Bay** – list-based search with direct magnet extraction

**Returns:** name, magnet link, images, seeders, leechers, date, size, category, uploader, language, downloads, etc.

## Architecture


```mermaid
flowchart TB
    subgraph API
        Flask[Flask routes]
    end
    
    subgraph Core
        Orch[Orchestrator]
        Fetcher[Fetcher]
        Protocol[Adapter Protocol]
    end
    
    subgraph Adapters
        PB_Adapter[Pirate Bay Adapter]
        X1337_Adapter[1337x Adapter]
    end
    
    Flask --> PB_Adapter
    Flask --> X1337_Adapter
    PB_Adapter --> Orch
    X1337_Adapter --> Orch
    Orch --> Protocol
    Orch --> Fetcher
    PB_Adapter --> Protocol
    X1337_Adapter --> Protocol
    X1337_Adapter -.->|detail fetches| Fetcher
```

- **Fetcher** – Playwright + BeautifulSoup (headless Chrome, configurable timeout, `wait_until`).
- **Protocol** – Simple interface: `build_search_url()`, `validate_page()`, `scrape_search_page()`. 
- **Orchestrator** – DRY workflow that handles fetch + errors + standard output for all sites.
- **Adapters** – Site-specific logic: URL building, selectors, two-phase scraping (if detail pages needed).
- **Easy Extension** – Add a new torrent site by writing one adapter and one thin api.py wrapper.

## Usage

You can use this API in the following ways:

1. **Pirate Bay – search by name & page (0-based):**
```bash
GET /pirate-bay/<query>/<int:pgno>
GET /pirate-bay/<query>
GET /pirate-bay/?q=<query>&page=<pgno>
```

2. **1337x – search by name & page (1-based):**
```bash
GET /1337x/<query>/<int:pgno>  
GET /1337x/<query>
GET /1337x/?q=<query>&page=<pgno>
```

Default ports:
- Local dev: `127.0.0.1:5000`
- Docker: `0.0.0.0:8000`

## Environment

| Component | Technology | Purpose |
|-----------|------------|---------|
| Browser | Playwright/Chrome (headless) | JS-heavy pages, waits until network-idle |
| Parser | BeautifulSoup 4 | Fast, readable scraping outside browser |
| Framework | Flask + **Flask-RESTful** (or **FastAPI***) | Lightweight API endpoints |
| Adapter Pattern | Python Protocol | OCP-ready; thin per-site plugins |

*Future upgrade suggestion

## Quick Start (Docker)
```bash
docker build -t 1337x-api .
docker run -p 8000:8000 1337x-api
```
**Visit:** `http://127.0.0.1:8000`

---
## Local Dev
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py  # runs on :5000
```

## How to Add a New Site (Extending the Protocol)

1. Create `sites/<site_name>/adapter.py`:  

```python
from typing import Callable, List
from bs4 import BeautifulSoup
from core.protocol import TorrentSiteAdapter

class NewSiteAdapter(TorrentSiteAdapter):
    BASE_URL = "https://..."
    
    def build_search_url(self, query: str, page: int) -> str:
        return f"{self.BASE_URL}/search?q={query}&p={page}"

    def validate_page(self, pgno) -> int:
        # coerce to int, set fallback/default, etc
        ...

    def scrape_search_page(self, soup, fetch_html, user_agent) -> List[dict]:
        # find results, extract fields, map to standard JSON schema
        # optional: fetch extra URLs via `fetch_html(url)` and append details
        ...
```

2. Create `sites/<site_name>/api.py`: wrap orchestrator call in existing `fetch` signature:

```python
from core.orchestrator import fetch_site
from sites.<site_name>.adapter import NewSiteAdapter

adapter = NewSiteAdapter()
def fetch(query, pgno=0, userAgent=...):
    return fetch_site(adapter, query, pgno, userAgent)
```

3. Register route in `app.py` and done.

## JSON Response Schema

The API returns JSON responses in two formats:

### Success Response

A successful response returns an array of torrent objects:

```json
[
  {
    "name": "Example Torrent Name",
    "magnet": "magnet:?xt=urn:btih:...",
    "Seeders": "1234",
    "Leechers": "567",
    "Size": "1.2 GB",
    "Date": "2024-01-15",
    "Images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
    "otherDetails": {
      "category": "Music",
      "type": "Audio",
      "language": "English",
      "uploader": "UploaderName",
      "downloads": "5000",
      "dateUploaded": "2024-01-15 12:00:00"
    }
  }
]
```

### Error Response

Error responses return a single object with a `Message` field:

```json
{
  "Message": "Empty Request"
}
```

Other possible error messages:
- `{"Message": "No data found"}`
- `{"Message": "Timeout error: ..."}`
- `{"Message": "Error occurred: ..."}`

### Response Examples by Site

#### 1337x Response Example

1337x responses include detailed metadata in `otherDetails` and may include multiple images:

```json
[
  {
    "name": "Artist - Album Name [2024] [FLAC]",
    "magnet": "magnet:?xt=urn:btih:abc123def456...",
    "Seeders": "234",
    "Leechers": "45",
    "Size": "456.7 MB",
    "Date": "2 days ago",
    "Images": [
      "https://www.1377x.to/uploads/thumbnails/image1.jpg",
      "https://www.1377x.to/uploads/thumbnails/image2.jpg"
    ],
    "otherDetails": {
      "category": "Music",
      "type": "Audio",
      "language": "English",
      "uploader": "Uploader123",
      "downloads": "1234",
      "dateUploaded": "2024-01-15 12:00:00"
    }
  }
]
```

**Note:** If no images are found, `Images` will be `"Na"` (string) instead of an array.

#### Pirate Bay Response Example

Pirate Bay responses have simpler `otherDetails` and typically return `"Na"` for images:

```json
[
  {
    "name": "Artist - Album Name [2024] [FLAC]",
    "magnet": "magnet:?xt=urn:btih:xyz789ghi012...",
    "Seeders": "567",
    "Leechers": "89",
    "Size": "456.7 MB",
    "Date": "2 days ago",
    "Images": "Na",
    "otherDetails": {
      "uploader": "UploaderName",
      "category": "Audio > Music"
    }
  }
]
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | The name/title of the torrent |
| `magnet` | string | The magnet link (or "Na" if not found) |
| `Seeders` | string | Number of seeders |
| `Leechers` | string | Number of leechers |
| `Size` | string | File size (human-readable format) |
| `Date` | string | Upload date (site-specific format) |
| `Images` | string \| array | Image URL(s) or "Na" if none found |
| `otherDetails` | object | Additional metadata (varies by site) |

**Note:** All string fields may contain `"Na"` if the value cannot be extracted from the source page.