"""Parser for Instagram export HTML files."""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from bs4 import BeautifulSoup


@dataclass
class InstagramPost:
    """Represents an Instagram post."""
    title: str
    images: List[str]  # Relative paths to images
    date: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tagged_users: List[str] = None
    hashtags: List[str] = None

    def __post_init__(self):
        if self.tagged_users is None:
            self.tagged_users = []
        if self.hashtags is None:
            self.hashtags = []


class InstagramParser:
    """Parser for Instagram export data."""

    def __init__(self, export_dir: Path):
        """Initialize parser with export directory path."""
        self.export_dir = Path(export_dir)
        self.posts_html = self.export_dir / "your_instagram_activity" / "media" / "posts_1.html"

    def parse_posts(self) -> List[InstagramPost]:
        """Parse all posts from the HTML file."""
        if not self.posts_html.exists():
            raise FileNotFoundError(f"Posts file not found: {self.posts_html}")

        with open(self.posts_html, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        posts = []
        # Find all post containers
        post_divs = soup.find_all('div', class_='pam _3-95 _2ph- _a6-g uiBoxWhite noborder')

        for post_div in post_divs:
            post = self._parse_post_div(post_div)
            if post:
                posts.append(post)

        return posts

    def _parse_post_div(self, post_div) -> Optional[InstagramPost]:
        """Parse a single post div element."""
        # Extract title
        title_elem = post_div.find('h2', class_='_3-95 _2pim _a6-h _a6-i')
        title = title_elem.get_text() if title_elem else ""

        # Extract date
        date_elem = post_div.find('div', class_='_3-94 _a6-o')
        date = date_elem.get_text() if date_elem else ""

        # Extract images
        content_div = post_div.find('div', class_='_3-95 _a6-p')
        images = []
        if content_div:
            img_tags = content_div.find_all('img', class_='_a6_o _3-96')
            for img in img_tags:
                src = img.get('src')
                if src:
                    images.append(src)

        # Extract location data
        latitude = None
        longitude = None
        tables = post_div.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label_div = cells[0].find('div', class_='_a6-q')
                    value_div = cells[1].find('div', class_='_a6-q') if len(cells) > 1 else None

                    if label_div and value_div:
                        label = label_div.get_text().strip()
                        value = value_div.get_text().strip()

                        if label == 'Latitude' and value:
                            try:
                                latitude = float(value)
                            except ValueError:
                                pass
                        elif label == 'Longitude' and value:
                            try:
                                longitude = float(value)
                            except ValueError:
                                pass

        # Skip empty posts
        if not images and not title:
            return None

        return InstagramPost(
            title=title,
            images=images,
            date=date,
            latitude=latitude,
            longitude=longitude
        )

    def get_full_image_path(self, relative_path: str) -> Path:
        """Convert relative image path to full path."""
        return self.export_dir / relative_path
