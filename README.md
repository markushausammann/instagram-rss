# Instagram to Substack via RSS

Generate a static website with RSS feed from your Instagram export, which Substack can then import.

## How It Works

1. Parses your Instagram export (JSON or HTML format)
2. Generates a static website with all your posts
3. Creates an RSS feed that Substack can import
4. You serve the site (locally for testing, or deploy for production)
5. Substack imports posts from the RSS feed

## Features

- ✅ Supports both JSON and HTML Instagram exports
- ✅ Extracts and displays hashtags as styled tags
- ✅ Preserves special characters (umlauts, accents, emojis)
- ✅ Includes location data when available
- ✅ Post selection tool to control what appears in RSS feed
- ✅ Clean, responsive design

## Setup

Install dependencies:
```bash
pip3 install -r requirements.txt
```

## Usage

### 1. (Optional) Select which posts to include in RSS feed

```bash
python3 select_posts.py
```

This interactive tool lets you:
- **Bulk selection**: Select all, by year, by hashtags, by location, etc.
- **Interactive mode**: Review posts one-by-one
- Save your selection to `selected_posts.json`

The static site will include all posts, but only selected posts will appear in the RSS feed that Substack imports.

### 2. Generate the static site

```bash
python3 generate_site.py
```

This will create a `docs/` directory with:
- `index.html` - Homepage listing all posts
- `posts/` - Individual post pages
- `images/` - All your Instagram images
- `feed.xml` - RSS feed for Substack (filtered by your selection)

### 3. Test locally

```bash
./serve.sh
```

Or manually:
```bash
cd docs
python3 -m http.server 8000
```

Then visit:
- Website: http://localhost:8000
- RSS feed: http://localhost:8000/feed.xml

### 4. Deploy to make publicly accessible

To use with Substack, you need to deploy the site somewhere public. Options:

**Free hosting options:**
- [GitHub Pages](https://pages.github.com/) - Free, easy
- [Netlify](https://www.netlify.com/) - Free tier, drag & drop
- [Vercel](https://vercel.com/) - Free tier
- [Cloudflare Pages](https://pages.cloudflare.com/) - Free

**GitHub Pages deployment:**

This repo can be deployed directly to GitHub Pages:

1. Push this entire repo to GitHub
2. Go to repo Settings → Pages
3. Under "Build and deployment", select:
   - Source: Deploy from a branch
   - Branch: main
   - Folder: `/docs`
4. GitHub will provide your site URL (e.g., `https://yourusername.github.io/instagram-archive/`)
5. Your RSS feed will be at: `https://yourusername.github.io/instagram-archive/feed.xml`

**Important**: Update `BASE_URL` in `generate_site.py` to your GitHub Pages URL before deploying!

### 5. Import to Substack

1. Go to your Substack Settings → Import
2. Choose "Import from RSS"
3. Enter your RSS feed URL (e.g., `https://yourusername.github.io/instagram-archive/feed.xml`)
4. Substack will import all posts from the feed

## Instagram Export Structure

Make sure your Instagram export is in the `insta-export/` directory:
```
insta-export/
├── media/
│   └── posts/
│       └── YYYYMM/
│           └── *.jpg, *.webp
└── your_instagram_activity/
    └── media/
        └── posts_1.json  (or posts_1.html)
```

**Note**: The tool automatically detects JSON or HTML format.

## Customization

Edit `generate_site.py` to change:
- `OUTPUT_DIR` - Where to generate the site (default: `docs/`)
- `BASE_URL` - Your production URL (update before deploying)
