#!/usr/bin/env python3
"""Generate static site and RSS feed from Instagram export."""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from instagram_parser import InstagramParser
from instagram_json_parser import InstagramJSONParser
from site_generator import SiteGenerator


def main():
    """Main entry point."""
    EXPORT_DIR = Path("insta-export")
    OUTPUT_DIR = Path("site")
    BASE_URL = "http://localhost:8000"

    if not EXPORT_DIR.exists():
        print(f"Error: Export directory not found: {EXPORT_DIR}")
        sys.exit(1)

    # Detect format and parse Instagram posts
    json_file = EXPORT_DIR / "your_instagram_activity" / "media" / "posts_1.json"
    html_file = EXPORT_DIR / "your_instagram_activity" / "media" / "posts_1.html"

    print("Parsing Instagram posts...")

    if json_file.exists():
        print("Detected JSON format export")
        parser = InstagramJSONParser(EXPORT_DIR)
    elif html_file.exists():
        print("Detected HTML format export")
        parser = InstagramParser(EXPORT_DIR)
    else:
        print("Error: Could not find posts_1.json or posts_1.html")
        sys.exit(1)

    try:
        posts = parser.parse_posts()
    except Exception as e:
        print(f"Error parsing posts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    if not posts:
        print("No posts found in export")
        sys.exit(1)

    print(f"Found {len(posts)} posts")

    # Load post selection if it exists
    selection_file = Path("selected_posts.json")
    if selection_file.exists():
        with open(selection_file, 'r') as f:
            selected_indices = set(json.load(f))

        if selected_indices:
            selected_posts = [posts[i] for i in sorted(selected_indices) if i < len(posts)]
            print(f"Using selection: {len(selected_posts)} posts selected for RSS feed")
            print(f"(All {len(posts)} posts will be in the static site)")
        else:
            selected_posts = posts
            print("No posts selected, using all posts")
    else:
        selected_posts = posts
        print("No selection file found, using all posts")
        print("Run 'python3 select_posts.py' to choose which posts to include in RSS feed")

    # Generate site
    generator = SiteGenerator(OUTPUT_DIR, EXPORT_DIR)
    generator.generate_site(posts, parser, selected_posts, base_url=BASE_URL)

    print(f"\n{'='*60}")
    print("Site generated successfully!")
    print(f"{'='*60}")
    print(f"\nTo view the site:")
    print(f"  1. cd site")
    print(f"  2. python3 -m http.server 8000")
    print(f"  3. Open http://localhost:8000 in your browser")
    print(f"\nRSS feed URL: http://localhost:8000/feed.xml")
    print(f"\nTo use with Substack:")
    print(f"  1. Make the site publicly accessible (deploy to a hosting service)")
    print(f"  2. In Substack, go to Settings > Import")
    print(f"  3. Provide the RSS feed URL")


if __name__ == "__main__":
    main()
