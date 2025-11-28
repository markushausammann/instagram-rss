#!/usr/bin/env python3
"""Interactive tool to select which posts to include in RSS feed."""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from instagram_parser import InstagramParser
from instagram_json_parser import InstagramJSONParser


def load_selection(selection_file: Path):
    """Load previously saved post selection."""
    if selection_file.exists():
        with open(selection_file, 'r') as f:
            return set(json.load(f))
    return set()


def save_selection(selection_file: Path, selected_indices: set):
    """Save post selection to file."""
    with open(selection_file, 'w') as f:
        json.dump(sorted(list(selected_indices)), f, indent=2)


def display_post_preview(post, idx):
    """Display a preview of a single post."""
    print(f"\n{'='*80}")
    print(f"POST #{idx + 1}")
    print(f"{'='*80}")
    print(f"Title: {post.title[:100]}")
    print(f"Date: {post.date}")
    print(f"Images: {len(post.images)}")
    if post.hashtags:
        print(f"Tags: {', '.join(['#' + h for h in post.hashtags])}")
    if post.latitude and post.longitude:
        print(f"Location: {post.latitude}, {post.longitude}")
    print(f"{'='*80}")


def interactive_selection(posts):
    """Interactive mode to select posts one by one."""
    selection_file = Path("selected_posts.json")
    selected = load_selection(selection_file)

    print("\n" + "="*80)
    print("INTERACTIVE POST SELECTION")
    print("="*80)
    print(f"\nTotal posts: {len(posts)}")
    print(f"Currently selected: {len(selected)}")
    print("\nCommands:")
    print("  y/yes    - Select this post")
    print("  n/no     - Skip this post")
    print("  s/skip   - Skip to next unreviewed post")
    print("  d/done   - Finish and save selection")
    print("  q/quit   - Quit without saving")
    print("  stats    - Show selection statistics")

    for idx, post in enumerate(posts):
        # Skip if already reviewed
        if idx in selected:
            continue

        display_post_preview(post, idx)

        while True:
            choice = input(f"\nSelect this post? (y/n/s/d/q/stats): ").strip().lower()

            if choice in ['y', 'yes']:
                selected.add(idx)
                print(f"✓ Added to selection ({len(selected)} total)")
                break
            elif choice in ['n', 'no']:
                print("✗ Skipped")
                break
            elif choice in ['s', 'skip']:
                print("→ Skipping to next unreviewed post")
                break
            elif choice in ['d', 'done']:
                save_selection(selection_file, selected)
                print(f"\n✓ Saved selection: {len(selected)} posts")
                return selected
            elif choice in ['q', 'quit']:
                print("\nExiting without saving")
                sys.exit(0)
            elif choice == 'stats':
                show_statistics(posts, selected)
            else:
                print("Invalid choice. Please use y/n/s/d/q/stats")

    # End of posts
    save_selection(selection_file, selected)
    print(f"\n✓ Finished! Selected {len(selected)} posts")
    return selected


def bulk_selection(posts):
    """Bulk selection mode with filters."""
    selection_file = Path("selected_posts.json")
    selected = load_selection(selection_file)

    print("\n" + "="*80)
    print("BULK POST SELECTION")
    print("="*80)
    print(f"\nTotal posts: {len(posts)}")
    print(f"Currently selected: {len(selected)}")

    while True:
        print("\n" + "-"*80)
        print("Bulk Selection Options:")
        print("  1. Select all posts")
        print("  2. Select by year")
        print("  3. Select posts with hashtags")
        print("  4. Select posts with location")
        print("  5. Select by date range")
        print("  6. Clear all selections")
        print("  7. View selected posts")
        print("  8. Save and continue to interactive mode")
        print("  9. Save and exit")
        print("  0. Exit without saving")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            selected = set(range(len(posts)))
            print(f"✓ Selected all {len(selected)} posts")

        elif choice == '2':
            years = {}
            for idx, post in enumerate(posts):
                year = post.date.split(',')[1].strip().split()[0] if ',' in post.date else 'Unknown'
                if year not in years:
                    years[year] = []
                years[year].append(idx)

            print("\nAvailable years:")
            for year in sorted(years.keys()):
                count = len(years[year])
                in_selection = sum(1 for i in years[year] if i in selected)
                print(f"  {year}: {count} posts ({in_selection} selected)")

            year_input = input("\nEnter years (comma-separated, e.g., 2023,2024): ").strip()
            for year in year_input.split(','):
                year = year.strip()
                if year in years:
                    for idx in years[year]:
                        selected.add(idx)
                    print(f"✓ Added {len(years[year])} posts from {year}")

        elif choice == '3':
            count = 0
            for idx, post in enumerate(posts):
                if post.hashtags:
                    selected.add(idx)
                    count += 1
            print(f"✓ Selected {count} posts with hashtags")

        elif choice == '4':
            count = 0
            for idx, post in enumerate(posts):
                if post.latitude and post.longitude:
                    selected.add(idx)
                    count += 1
            print(f"✓ Selected {count} posts with location data")

        elif choice == '5':
            print("\nEnter date range (format: YYYY)")
            start_year = input("From year: ").strip()
            end_year = input("To year: ").strip()

            count = 0
            for idx, post in enumerate(posts):
                year = post.date.split(',')[1].strip().split()[0] if ',' in post.date else ''
                if start_year <= year <= end_year:
                    selected.add(idx)
                    count += 1
            print(f"✓ Selected {count} posts from {start_year} to {end_year}")

        elif choice == '6':
            confirm = input("Clear all selections? (y/n): ").strip().lower()
            if confirm == 'y':
                selected.clear()
                print("✓ All selections cleared")

        elif choice == '7':
            if not selected:
                print("\nNo posts selected yet")
            else:
                print(f"\n{len(selected)} posts selected:")
                for idx in sorted(list(selected))[:20]:
                    post = posts[idx]
                    print(f"  #{idx + 1}: {post.title[:60]} ({post.date})")
                if len(selected) > 20:
                    print(f"  ... and {len(selected) - 20} more")

        elif choice == '8':
            save_selection(selection_file, selected)
            print(f"\n✓ Saved {len(selected)} posts")
            print("\nSwitching to interactive mode...")
            return interactive_selection(posts)

        elif choice == '9':
            save_selection(selection_file, selected)
            print(f"\n✓ Saved selection: {len(selected)} posts")
            return selected

        elif choice == '0':
            print("\nExiting without saving")
            sys.exit(0)

        else:
            print("Invalid choice")


def show_statistics(posts, selected):
    """Show statistics about selected posts."""
    print("\n" + "="*80)
    print("SELECTION STATISTICS")
    print("="*80)
    print(f"Total posts: {len(posts)}")
    print(f"Selected: {len(selected)}")
    print(f"Not selected: {len(posts) - len(selected)}")

    if selected:
        selected_posts = [posts[i] for i in selected if i < len(posts)]
        years = {}
        with_hashtags = sum(1 for p in selected_posts if p.hashtags)
        with_location = sum(1 for p in selected_posts if p.latitude and p.longitude)

        for post in selected_posts:
            year = post.date.split(',')[1].strip().split()[0] if ',' in post.date else 'Unknown'
            years[year] = years.get(year, 0) + 1

        print(f"\nSelected posts by year:")
        for year in sorted(years.keys()):
            print(f"  {year}: {years[year]} posts")

        print(f"\nWith hashtags: {with_hashtags}")
        print(f"With location: {with_location}")

    print("="*80)


def main():
    """Main entry point."""
    EXPORT_DIR = Path("insta-export")

    if not EXPORT_DIR.exists():
        print(f"Error: Export directory not found: {EXPORT_DIR}")
        sys.exit(1)

    # Detect format and parse
    json_file = EXPORT_DIR / "your_instagram_activity" / "media" / "posts_1.json"
    html_file = EXPORT_DIR / "your_instagram_activity" / "media" / "posts_1.html"

    print("Loading Instagram posts...")

    if json_file.exists():
        parser = InstagramJSONParser(EXPORT_DIR)
    elif html_file.exists():
        parser = InstagramParser(EXPORT_DIR)
    else:
        print("Error: Could not find posts_1.json or posts_1.html")
        sys.exit(1)

    try:
        posts = parser.parse_posts()
    except Exception as e:
        print(f"Error parsing posts: {e}")
        sys.exit(1)

    if not posts:
        print("No posts found in export")
        sys.exit(1)

    print(f"Found {len(posts)} posts")

    # Choose mode
    print("\nSelection Mode:")
    print("  1. Bulk selection (filters)")
    print("  2. Interactive selection (one by one)")

    mode = input("\nChoose mode (1/2): ").strip()

    if mode == '1':
        bulk_selection(posts)
    elif mode == '2':
        interactive_selection(posts)
    else:
        print("Invalid mode")
        sys.exit(1)


if __name__ == "__main__":
    main()
