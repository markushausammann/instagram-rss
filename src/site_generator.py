"""Generate a static website from Instagram posts."""
from pathlib import Path
from datetime import datetime
from typing import List
import shutil
from instagram_parser import InstagramPost, InstagramParser


class SiteGenerator:
    """Generates a static website from Instagram posts."""

    def __init__(self, output_dir: Path, export_dir: Path):
        """Initialize the site generator."""
        self.output_dir = Path(output_dir)
        self.export_dir = Path(export_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories
        self.posts_dir = self.output_dir / "posts"
        self.images_dir = self.output_dir / "images"
        self.posts_dir.mkdir(exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)

    def generate_site(self, posts: List[InstagramPost], parser: InstagramParser, rss_posts: List[InstagramPost] = None, base_url: str = "http://localhost:8000"):
        """Generate the complete static site."""
        print(f"\nGenerating site in {self.output_dir}...")

        # Use all posts for RSS if not specified
        if rss_posts is None:
            rss_posts = posts

        # Copy images and update post image paths
        for post in posts:
            self._copy_post_images(post, parser)

        # Generate individual post pages
        for idx, post in enumerate(posts):
            self._generate_post_page(post, idx)

        # Generate index page
        self._generate_index_page(posts)

        # Generate RSS feed with selected posts only
        from rss_generator import RSSGenerator
        rss_gen = RSSGenerator(base_url)
        rss_gen.generate_feed(rss_posts, self.output_dir / "feed.xml")

        print(f"✓ Site generated successfully!")
        print(f"✓ {len(posts)} posts in static site")
        print(f"✓ {len(rss_posts)} posts in RSS feed")
        print(f"✓ RSS feed: {self.output_dir}/feed.xml")

    def _truncate_title(self, text: str, max_length: int = 60) -> str:
        """Truncate title smartly at sentence/phrase boundaries."""
        if len(text) <= max_length:
            return text

        # First, try to cut at first sentence (period, exclamation, question mark)
        # but only if we get at least a few words (15 chars minimum)
        for delimiter in ['. ', '! ', '? ']:
            pos = text.find(delimiter)
            if 15 <= pos <= max_length:
                return text[:pos + 1]  # Include the punctuation

        # Next, try to cut at comma if we get a decent amount of text
        comma_pos = text.find(', ')
        if 15 <= comma_pos <= max_length:
            return text[:comma_pos]

        # Fall back to word boundary truncation
        if len(text) > max_length:
            truncated = text[:max_length].rsplit(' ', 1)[0]
            return truncated + '...'

        return text

    def _copy_post_images(self, post: InstagramPost, parser: InstagramParser):
        """Copy post images to output directory and update paths."""
        new_image_paths = []

        for img_path in post.images:
            src_path = parser.get_full_image_path(img_path)

            if not src_path.exists():
                continue

            # Create a unique filename
            dest_filename = src_path.name
            dest_path = self.images_dir / dest_filename

            # Copy if doesn't exist
            if not dest_path.exists():
                shutil.copy2(src_path, dest_path)

            # Store relative path for HTML
            new_image_paths.append(f"../images/{dest_filename}")

        # Update post with new paths
        post.images = new_image_paths

    def _generate_post_page(self, post: InstagramPost, idx: int):
        """Generate an individual post page."""
        post_id = f"post-{idx + 1}"
        post_file = self.posts_dir / f"{post_id}.html"

        # Parse date
        date_str = post.date or "Unknown date"

        # Truncate title if too long, but keep full text for body
        full_text = post.title or 'Instagram Post'
        title = self._truncate_title(full_text, max_length=60)

        # Generate images HTML
        images_html = ""
        for img_path in post.images:
            images_html += f'        <img src="{img_path}" alt="Instagram post image" style="max-width: 100%; margin: 30px 0; display: block;">\n'

        # Generate hashtags HTML
        hashtags_html = ""
        if post.hashtags:
            tags = ' '.join([f'<span style="display: inline-block; background: #e1f5fe; color: #01579b; padding: 4px 8px; margin: 2px; border-radius: 4px; font-size: 14px;">#{tag}</span>' for tag in post.hashtags])
            hashtags_html = f"""
        <div style="margin: 20px 0;">
            {tags}
        </div>
"""

        # Generate location HTML
        location_html = ""
        if post.latitude and post.longitude:
            location_html = f"""
        <p style="color: #666; font-size: 14px;">
            📍 Location: {post.latitude}, {post.longitude}
        </p>
"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{post.title or 'Instagram Post'}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            margin-bottom: 10px;
        }}
        .meta {{
            color: #666;
            margin-bottom: 30px;
        }}
        img {{
            display: block;
            margin: 20px auto;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <a href="../index.html">← Back to all posts</a>

    <article>
        <h1>{title}</h1>
        <div class="meta">
            <time>{date_str}</time>
        </div>

        <p style="font-style: italic; color: #666; font-size: 14px; margin-bottom: 10px;">
            Imported from Instagram.
        </p>

        <p style="font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
            {full_text}
        </p>

{hashtags_html}
{images_html}
{location_html}
    </article>
</body>
</html>
"""

        post_file.write_text(html, encoding='utf-8')

    def _generate_index_page(self, posts: List[InstagramPost]):
        """Generate the index page with all posts."""
        posts_html = ""

        for idx, post in enumerate(posts):
            post_id = f"post-{idx + 1}"

            # Truncate title for index page
            title = self._truncate_title(post.title or 'Instagram Post', max_length=60)

            # Get first image for thumbnail
            thumb = post.images[0] if post.images else ""
            thumb_html = f'<img src="{thumb.replace("../", "")}" style="max-width: 200px; margin-right: 20px;">' if thumb else ""

            # Generate hashtags for index
            hashtags_index_html = ""
            if post.hashtags:
                tags = ' '.join([f'<span style="display: inline-block; background: #e1f5fe; color: #01579b; padding: 3px 6px; margin: 2px; border-radius: 3px; font-size: 12px;">#{tag}</span>' for tag in post.hashtags])
                hashtags_index_html = f'<div style="margin-top: 8px;">{tags}</div>'

            posts_html += f"""
        <article style="border-bottom: 1px solid #eee; padding: 20px 0; display: flex; gap: 20px;">
            {thumb_html}
            <div>
                <h2 style="margin-top: 0;">
                    <a href="posts/{post_id}.html">{title}</a>
                </h2>
                <p style="color: #666;">{post.date}</p>
                <p>{len(post.images)} image(s)</p>
                {hashtags_index_html}
            </div>
        </article>
"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instagram Archive</title>
    <link rel="alternate" type="application/rss+xml" title="RSS Feed" href="feed.xml">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{
            border-bottom: 3px solid #333;
            padding-bottom: 10px;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .rss-link {{
            background: #ff6600;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
        }}
        .rss-link:hover {{
            background: #cc5200;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <h1>Instagram Archive</h1>

    <a href="feed.xml" class="rss-link">📡 RSS Feed</a>

    <p style="color: #666;">
        {len(posts)} posts from Instagram export
    </p>

    <div>
{posts_html}
    </div>
</body>
</html>
"""

        index_file = self.output_dir / "index.html"
        index_file.write_text(html, encoding='utf-8')
