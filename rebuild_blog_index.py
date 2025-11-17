#!/usr/bin/env python3
"""
Script to rebuild blog index pages for static melmelboo site.
Extracts article metadata and regenerates paginated index pages.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from html.parser import HTMLParser
import json

POSTS_PER_PAGE = 6
BLOG_DIR = Path("blog")


class ArticleParser(HTMLParser):
    """Extract metadata from article HTML."""

    def __init__(self):
        super().__init__()
        self.title = ""
        self.excerpt = ""
        self.image = ""
        self.date = ""
        self.author = ""
        self.url = ""
        self.in_title = False
        self.in_content = False
        self.content_text = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Extract title
        if tag == "h1" and attrs_dict.get("class") == "post-title":
            self.in_title = True

        # Extract content for excerpt
        if tag == "section" and "post-content" in attrs_dict.get("class", ""):
            self.in_content = True

        # Extract featured image
        if tag == "meta":
            if attrs_dict.get("property") == "og:image":
                self.image = attrs_dict.get("content", "")
            elif attrs_dict.get("property") == "article:published_time":
                self.date = attrs_dict.get("content", "")
            elif attrs_dict.get("property") == "og:url":
                self.url = attrs_dict.get("content", "")
            elif attrs_dict.get("name") == "description":
                # Fallback to meta description for excerpt
                if not self.excerpt:
                    self.excerpt = attrs_dict.get("content", "")

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
        if self.in_content:
            # Collect content text for excerpt
            text = data.strip()
            if text:
                self.content_text += " " + text

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_title = False
        if tag == "section" and self.in_content:
            self.in_content = False
            # Use first 200 chars of content as excerpt if not set
            if not self.excerpt and self.content_text:
                self.excerpt = self.content_text[:200].strip()


def extract_article_metadata(article_path):
    """Extract metadata from an article's index.html."""
    html_file = article_path / "index.html"
    if not html_file.exists():
        return None

    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = ArticleParser()
        parser.feed(content)

        # Get relative URL from path
        rel_url = str(article_path.relative_to(BLOG_DIR)) + "/"

        # Parse date
        date_obj = None
        if parser.date:
            try:
                date_obj = datetime.fromisoformat(parser.date.replace('Z', '+00:00'))
            except:
                pass

        return {
            'title': parser.title or "Untitled",
            'excerpt': parser.excerpt[:200] if parser.excerpt else "",
            'image': parser.image,
            'date': date_obj,
            'date_str': date_obj.strftime("%d %B %Y") if date_obj else "",
            'url': rel_url,
            'slug': article_path.name
        }
    except Exception as e:
        print(f"Error parsing {article_path}: {e}")
        return None


def collect_articles():
    """Collect all article metadata."""
    articles = []

    # Find all article directories (exclude system dirs)
    exclude_dirs = {'page', 'author', 'tag', 'public', 'assets', 'rss'}

    for item in BLOG_DIR.iterdir():
        if item.is_dir() and item.name not in exclude_dirs:
            metadata = extract_article_metadata(item)
            if metadata:
                articles.append(metadata)

    # Sort by date (newest first)
    from datetime import timezone
    min_date = datetime.min.replace(tzinfo=timezone.utc)
    articles.sort(key=lambda x: x['date'] if x['date'] else min_date, reverse=True)

    return articles


def generate_index_page(articles, page_num, total_pages):
    """Generate HTML for a blog index page."""

    start_idx = (page_num - 1) * POSTS_PER_PAGE
    end_idx = start_idx + POSTS_PER_PAGE
    page_articles = articles[start_idx:end_idx]

    posts_html = []
    for article in page_articles:
        # Use original blog format with image and columns
        image_html = f'<img style="width:92%;" alt="{article["title"]}" src="{article["image"]}" />' if article["image"] else ""

        # Make article URLs absolute for paginated pages
        article_url = f"/blog/{article['url']}" if page_num > 1 else article['url']

        post_html = f"""<article class="post tag-getting-started row">
  <header class="col-lg-4 post-loop-header">
    <a href="{article_url}">
      {image_html}
    </a>
  </header>
  <section class="post-excerpt col-lg-8">
      <h2 class="post-title">
        <a href="{article_url}">
          {article['title']}
        </a>
      </h2>
      <p>
        <a href="{article_url}">
          {article['excerpt']}...
        </a>
      </p>
      <p class="read-more">
        <a href="{article_url}">
          Lire la suite →
        </a>
      </p>
  </section>
</article>"""
        posts_html.append(post_html)

    # Generate pagination
    pagination = ""
    if total_pages > 1:
        # Page 1 should link to /blog/ not /blog/page/1/
        if page_num > 1:
            prev_url = "/blog/" if page_num == 2 else f"/blog/page/{page_num - 1}/"
            prev_page = f'<a class="older-posts" href="{prev_url}"></a>'
        else:
            prev_page = ""

        if page_num < total_pages:
            next_page = f'<a class="newer-posts" href="/blog/page/{page_num + 1}/"></a>'
        else:
            next_page = ""

        page_number = f'<span class="page-number">Page {page_num} of {total_pages}</span>'

        pagination = f"""
    <nav class="pagination" role="navigation">
        {prev_page}
        {page_number}
        {next_page}
    </nav>"""

    # Read template from original backup or existing blog/index.html header/footer
    template_file = Path("/tmp/blog-index-template.html")
    if not template_file.exists():
        template_file = BLOG_DIR / "index.html"

    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()

        # Fix relative paths for paginated pages
        if page_num > 1:
            # Fix CSS and asset paths for nested pages (blog/page/2/)
            # From blog/page/2/ -> blog/assets/ needs ../../assets/
            template = template.replace('href="assets/', 'href="../../assets/')
            template = template.replace('src="assets/', 'src="../../assets/')
            # From blog/page/2/ -> ../images/ becomes ../../images/ (going to root/images/)
            template = template.replace('href="../images/', 'href="../../../images/')
            template = template.replace('src="../images/', 'src="../../../images/')
            template = template.replace('href="../css/', 'href="../../../css/')
            template = template.replace('src="../js/', 'src="../../../js/')

        # Extract header (everything before posts-loop div content)
        header_match = re.search(r'(.*?<div class="posts-loop">\s*)', template, re.DOTALL)
        header = header_match.group(1) if header_match else ""

        # Extract footer (everything after </div> that closes posts-loop, before closing </body>)
        # Look for the closing div after pagination or articles
        footer_match = re.search(r'</div>\s*(</main>.*?</body>.*?</html>)', template, re.DOTALL)
        footer = "\n</div>\n" + footer_match.group(1) if footer_match else "\n</div>\n</main>\n</body>\n</html>"

        # Combine
        return header + "\n".join(posts_html) + pagination + footer

    return None


def main():
    """Main function to rebuild blog index."""
    print("Collecting articles...")
    articles = collect_articles()
    print(f"Found {len(articles)} articles")

    if not articles:
        print("No articles found!")
        return

    # Calculate total pages
    total_pages = (len(articles) + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE
    print(f"Generating {total_pages} pages...")

    # Generate main index
    print("Generating blog/index.html...")
    index_html = generate_index_page(articles, 1, total_pages)
    if index_html:
        with open(BLOG_DIR / "index.html", 'w', encoding='utf-8') as f:
            f.write(index_html)

    # Generate paginated pages
    page_dir = BLOG_DIR / "page"
    page_dir.mkdir(exist_ok=True)

    for page_num in range(2, total_pages + 1):
        page_path = page_dir / str(page_num)
        page_path.mkdir(exist_ok=True)

        print(f"Generating blog/page/{page_num}/index.html...")
        page_html = generate_index_page(articles, page_num, total_pages)
        if page_html:
            with open(page_path / "index.html", 'w', encoding='utf-8') as f:
                f.write(page_html)

    print("Done! Blog index rebuilt successfully.")


if __name__ == "__main__":
    main()
