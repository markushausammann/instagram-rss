"""Parser for Instagram JSON export files."""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from datetime import datetime


@dataclass
class InstagramPost:
    """Represents an Instagram post."""
    title: str
    images: List[str]  # Relative paths to images
    date: str
    timestamp: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    tagged_users: List[str] = None
    hashtags: List[str] = None

    def __post_init__(self):
        if self.tagged_users is None:
            self.tagged_users = []
        if self.hashtags is None:
            self.hashtags = []


class InstagramJSONParser:
    """Parser for Instagram JSON export data."""

    def __init__(self, export_dir: Path):
        """Initialize parser with export directory path."""
        self.export_dir = Path(export_dir)
        self.posts_json = self.export_dir / "your_instagram_activity" / "media" / "posts_1.json"

    def _fix_encoding(self, text: str) -> str:
        """Fix double-encoded UTF-8 text (common in Instagram exports)."""
        if not text:
            return text
        try:
            # Try to fix UTF-8 interpreted as Latin-1
            return text.encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            # If it fails, return original
            return text

    def _extract_hashtags(self, text: str) -> tuple[str, List[str]]:
        """Extract hashtags from text and return cleaned text + hashtags list."""
        if not text:
            return text, []

        # Find all hashtags
        hashtags = re.findall(r'#(\w+)', text)

        # Remove duplicates while preserving order
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_hashtags.append(tag)

        # Remove hashtags from text
        clean_text = re.sub(r'\s*#\w+', '', text).strip()

        return clean_text, unique_hashtags

    def parse_posts(self) -> List[InstagramPost]:
        """Parse all posts from the JSON file."""
        if not self.posts_json.exists():
            raise FileNotFoundError(f"Posts file not found: {self.posts_json}")

        with open(self.posts_json, 'r', encoding='utf-8') as f:
            data = json.load(f)

        posts = []
        for post_data in data:
            post = self._parse_post(post_data)
            if post:
                posts.append(post)

        # Sort by timestamp, newest first
        posts.sort(key=lambda p: p.timestamp, reverse=True)

        return posts

    def _parse_post(self, post_data: dict) -> Optional[InstagramPost]:
        """Parse a single post from JSON data."""
        # Get title from post level or first media item
        title = self._fix_encoding(post_data.get('title', ''))

        # Get media items
        media_items = post_data.get('media', [])
        if not media_items:
            return None

        # Get timestamp from post level, or fallback to first media item
        timestamp = post_data.get('creation_timestamp', 0)
        if not timestamp and media_items:
            timestamp = media_items[0].get('creation_timestamp', 0)

        # If still no timestamp, use first media's timestamp or 0
        if not timestamp:
            timestamp = 0

        # Format date
        date = self._format_timestamp(timestamp)

        images = []
        latitude = None
        longitude = None

        for media in media_items:
            # Get title from media if not at post level
            if not title:
                title = self._fix_encoding(media.get('title', ''))

            # Get image URI
            uri = media.get('uri', '')
            if uri:
                images.append(uri)

            # Check for location data in photo_metadata
            media_metadata = media.get('media_metadata', {})
            photo_metadata = media_metadata.get('photo_metadata', {})
            exif_data = photo_metadata.get('exif_data', [])

            for exif in exif_data:
                if exif.get('latitude') and not latitude:
                    latitude = exif.get('latitude')
                if exif.get('longitude') and not longitude:
                    longitude = exif.get('longitude')

        # Skip if no images
        if not images:
            return None

        # Extract hashtags from title and clean the title
        clean_title, hashtags = self._extract_hashtags(title)

        return InstagramPost(
            title=clean_title,
            images=images,
            date=date,
            timestamp=timestamp,
            latitude=latitude,
            longitude=longitude,
            hashtags=hashtags
        )

    def _format_timestamp(self, timestamp: int) -> str:
        """Convert Unix timestamp to readable date string."""
        if not timestamp:
            return "Unknown date"

        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%b %d, %Y %I:%M %p")
        except (ValueError, OSError):
            return "Unknown date"

    def get_full_image_path(self, relative_path: str) -> Path:
        """Convert relative image path to full path."""
        return self.export_dir / relative_path
