# Project Structure

```
instaSubstack/
├── .gitignore              # Git ignore rules
├── README.md               # Main documentation
├── requirements.txt        # Python dependencies
├── generate_site.py        # Main script to generate site
├── select_posts.py         # Interactive post selection tool
├── serve.sh                # Quick local server script
├── selected_posts.json     # Your post selection (gitignored)
├── src/                    # Source code
│   ├── instagram_parser.py       # HTML format parser
│   ├── instagram_json_parser.py  # JSON format parser
│   ├── site_generator.py         # Static site generator
│   └── rss_generator.py          # RSS feed generator
├── site/                   # Generated static site (deploy this)
│   ├── index.html
│   ├── feed.xml
│   ├── posts/
│   └── images/
└── insta-export/           # Your Instagram export (gitignored)
    ├── media/
    └── your_instagram_activity/
```

## Key Files

- **generate_site.py**: Run this to generate the static site
- **select_posts.py**: Run this to choose which posts appear in RSS feed
- **site/**: Deploy this directory to hosting (GitHub Pages, Netlify, etc.)
- **feed.xml**: The RSS feed that Substack imports

## What Gets Committed

✅ Source code (src/)
✅ Scripts (generate_site.py, select_posts.py)
✅ Documentation (README.md)
✅ Generated site (site/)
❌ Instagram export (insta-export/)
❌ Post selection (selected_posts.json)
