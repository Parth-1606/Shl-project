import json
import logging
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class SHLCatalogScraper:
    """
    Scraper designed to extract assessment data from SHL Individual Test Solutions catalog.
    Note: SHL's catalog often requires authentication or Javascript to render fully. 
    This scraper is built targeting a hypothetical server-rendered catalog page, 
    but can be extended with Playwright if JS rendering is mandatory.
    """
    
    def __init__(self, base_url: str = "https://www.shl.com/en/assessments/catalog"):
        self.base_url = base_url
        self.session = requests.Session()
        # Mock headers to prevent basic blocking
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def fetch_catalog_page(self) -> str:
        """Fetches the HTML content of the catalog page."""
        try:
            logger.info(f"Fetching catalog from {self.base_url}")
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch catalog page: {e}")
            raise

    def parse_assessment_card(self, card_soup: BeautifulSoup) -> Dict[str, Any]:
        """Parses individual assessment HTML card into a structured dictionary."""
        # Note: These selectors are based on generic modern web practices.
        # They would need to be updated to match the exact DOM of the actual SHL catalog.
        
        name_elem = card_soup.select_one(".assessment-title")
        desc_elem = card_soup.select_one(".assessment-description")
        url_elem = card_soup.select_one("a.assessment-link")
        
        # Meta items typically structured as key-value tags or lists
        meta_items = card_soup.select(".assessment-meta li")
        metadata = {}
        for item in meta_items:
            key_elem = item.select_one(".meta-key")
            val_elem = item.select_one(".meta-value")
            if key_elem and val_elem:
                key = key_elem.text.strip().lower().replace(" ", "_")
                # Parse comma separated lists into actual lists
                val = val_elem.text.strip()
                if "," in val:
                    val = [v.strip() for v in val.split(",")]
                metadata[key] = val

        return {
            "name": name_elem.text.strip() if name_elem else "Unknown Assessment",
            "url": url_elem["href"] if url_elem else "#",
            "description": desc_elem.text.strip() if desc_elem else "No description available.",
            "test_type": metadata.get("test_type", "General"),
            "skills_measured": metadata.get("skills_measured", []),
            "job_roles": metadata.get("job_roles", []),
            "duration": metadata.get("duration", "Varies"),
            "remote_testing": metadata.get("remote_testing", "Yes"),
            "adaptive": metadata.get("adaptive", "No"),
            "languages": metadata.get("languages", ["English"])
        }

    def scrape(self) -> List[Dict[str, Any]]:
        """Main orchestrator for scraping the catalog."""
        html_content = self.fetch_catalog_page()
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all assessment cards. Selector will need adjustment based on real DOM.
        assessment_cards = soup.select(".assessment-card")
        logger.info(f"Found {len(assessment_cards)} potential assessments.")
        
        assessments = []
        for card in assessment_cards:
            try:
                assessment_data = self.parse_assessment_card(card)
                assessments.append(assessment_data)
            except Exception as e:
                logger.warning(f"Failed to parse a card: {e}")
                
        return assessments

    def export_to_json(self, assessments: List[Dict[str, Any]], filepath: str):
        """Exports the list of assessments to a JSON file."""
        output_path = Path(filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(assessments, f, indent=4, ensure_ascii=False)
        logger.info(f"Successfully exported {len(assessments)} assessments to {filepath}")


if __name__ == "__main__":
    # Example execution
    scraper = SHLCatalogScraper()
    # In a real scenario we'd call: 
    # assessments = scraper.scrape()
    # But since the page requires Auth/JS, we would normally seed the JSON manually or use Playwright.
    pass
