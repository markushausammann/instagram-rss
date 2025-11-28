"""Generate RSS feed from Instagram posts."""
from pathlib import Path
from datetime import datetime
from typing import List
import re
from instagram_parser import InstagramPost
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Register namespaces for proper XML generation
ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
ET.register_namespace('content', 'http://purl.org/rss/1.0/modules/content/')


class RSSGenerator:
    """Generates an RSS 2.0 feed from Instagram posts."""

    def __init__(self, base_url: str):
        """Initialize RSS generator with base URL."""
        self.base_url = base_url.rstrip('/')

    def _truncate_title(self, text: str, max_length: int = 100) -> str:
        """Truncate title to max_length characters, ending at word boundary."""
        if len(text) <= max_length:
            return text

        # Truncate at word boundary
        truncated = text[:max_length].rsplit(' ', 1)[0]
        return truncated + '...'

    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        # Find all hashtags (word characters after #)
        hashtags = re.findall(r'#(\w+)', text)
        # Remove duplicates while preserving order
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_hashtags.append(tag)
        return unique_hashtags

    def generate_feed(self, posts: List[InstagramPost], output_path: Path):
        """Generate RSS feed XML file."""
        rss = ET.Element('rss', version='2.0')
        rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
        rss.set('xmlns:content', 'http://purl.org/rss/1.0/modules/content/')

        channel = ET.SubElement(rss, 'channel')

        # Channel metadata
        ET.SubElement(channel, 'title').text = 'Instagram Archive'
        ET.SubElement(channel, 'link').text = self.base_url
        ET.SubElement(channel, 'description').text = 'Posts from Instagram export'
        ET.SubElement(channel, 'language').text = 'en'

        # Self link
        atom_link = ET.SubElement(channel, 'atom:link')
        atom_link.set('href', f'{self.base_url}/feed.xml')
        atom_link.set('rel', 'self')
        atom_link.set('type', 'application/rss+xml')

        # Add items (posts)
        for idx, post in enumerate(posts):
            self._add_item(channel, post, idx)

        # Pretty print and save
        xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')

        # Remove extra blank lines
        xml_lines = [line for line in xml_str.split('\n') if line.strip()]
        xml_str = '\n'.join(xml_lines)

        output_path.write_text(xml_str, encoding='utf-8')
        print(f"✓ RSS feed generated: {output_path}")

    def _add_item(self, channel: ET.Element, post: InstagramPost, idx: int):
        """Add a single post as RSS item."""
        item = ET.SubElement(channel, 'item')

        # Title (truncated for RSS)
        full_title = post.title or f'Instagram Post {idx + 1}'
        title = self._truncate_title(full_title, max_length=100)
        ET.SubElement(item, 'title').text = title

        # Link
        post_url = f'{self.base_url}/posts/post-{idx + 1}.html'
        ET.SubElement(item, 'link').text = post_url

        # GUID
        guid = ET.SubElement(item, 'guid')
        guid.set('isPermaLink', 'true')
        guid.text = post_url

        # Publication date
        pub_date = self._parse_date(post.date)
        if pub_date:
            ET.SubElement(item, 'pubDate').text = pub_date

        # Description with images
        description = self._create_description(post, idx)
        ET.SubElement(item, 'description').text = description

        # Content (full HTML)
        content_html = self._create_content_html(post)
        content = ET.SubElement(item, 'content:encoded')
        content.text = content_html

        # Add hashtags as categories
        for hashtag in post.hashtags:
            category = ET.SubElement(item, 'category')
            category.text = hashtag

    def _create_description(self, post: InstagramPost, idx: int) -> str:
        """Create description text for RSS item."""
        parts = []

        if post.title:
            parts.append(post.title)

        if post.images:
            parts.append(f"{len(post.images)} image(s)")

        if post.date:
            parts.append(f"Posted: {post.date}")

        return " | ".join(parts) if parts else f"Instagram Post {idx + 1}"

    def _create_content_html(self, post: InstagramPost) -> str:
        """Create full HTML content for RSS item."""
        html_parts = []

        # Add caption/title as body text
        if post.title:
            html_parts.append(f'<p>{post.title}</p>')

        # Add hashtags as styled tags
        if post.hashtags:
            tags = ' '.join([f'<span style="display: inline-block; background: #e1f5fe; color: #01579b; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 14px;">#{tag}</span>' for tag in post.hashtags])
            html_parts.append(f'<div style="margin: 15px 0;">{tags}</div>')

        # Add images
        for img_path in post.images:
            # Convert relative path to absolute URL
            img_filename = Path(img_path).name
            img_url = f"{self.base_url}/images/{img_filename}"
            html_parts.append(f'<p><img src="{img_url}" style="max-width: 100%;" /></p>')

        # Add location if available
        if post.latitude and post.longitude:
            html_parts.append(f'<p>📍 Location: {post.latitude}, {post.longitude}</p>')

        return '\n'.join(html_parts)

    def _parse_date(self, date_str: str) -> str:
        """Parse Instagram date to RFC 822 format for RSS."""
        if not date_str:
            return ''

        try:
            # Try to parse Instagram date format
            # Example: "Aug 22, 2025 8:18 am"
            dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
            # Convert to RFC 822 format
            return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
        except ValueError:
            try:
                # Try alternative format
                dt = datetime.strptime(date_str, "%b %d, %Y %I:%M %p")
                return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')
            except ValueError:
                # Return empty if can't parse
                return ''
