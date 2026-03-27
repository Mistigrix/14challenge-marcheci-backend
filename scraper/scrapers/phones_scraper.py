import logging
import re
from bs4 import BeautifulSoup
from .base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = 'https://www.jumia.ci'

class PhonesScraper(BaseScraper):
    source_name = 'jumia.ci'

    def scrape(self) -> list[dict]:
        products = []
        url = f'{BASE_URL}/telephone-tablette/'

        while url:
            logger.info('Scraping page: %s', url)
            try:
                response = self.get(url)
            except Exception:
                break

            soup = BeautifulSoup(response.text, 'html.parser')

            for article in soup.select('article.prd'):
                try:
                    products.append(self._parse_article(article))
                except Exception as e:
                    logger.warning('Failed to parse article: %s', e)

            next_link = soup.find('link', rel='next')
            url = next_link['href'] if next_link else None

        logger.info('Scraped %d products from %s', len(products), self.source_name)
        return products

    def _parse_article(self, article) -> dict:
        core = article.select_one('a.core')

        title_tag = article.select_one('div.name')
        title = title_tag.get_text(strip=True) if title_tag else core.get('data-gtm-name', '')

        relative_url = core['href'] 
        product_url = f'{BASE_URL}{relative_url}'

        price = None
        price_tag = article.select_one('div.prc')
        if price_tag:
            raw = re.sub(r'[^\d]', '', price_tag.get_text())
            price = float(raw) if raw else None

        image_url = ''
        img_tag = article.select_one('img.img')
        if img_tag:
            image_url = img_tag.get('data-src') or img_tag.get('src', '')

        brand = core.get('data-gtm-brand', '')

        return {
            'title': title,
            'description': brand,
            'price': price,
            'currency': 'FCFA',
            'image_url': image_url,
            'product_url': product_url,
            'category_name': 'Téléphones & Tablettes',
            'rating': None,
            'in_stock': True,
        }
