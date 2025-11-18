#!/usr/bin/env python3
import os
import re
from html.parser import HTMLParser
from datetime import datetime

class ArticleMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.image = ""
        self.date = ""
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "h1" and attrs_dict.get("class") == "post-title":
            self.in_title = True
        if tag == "meta":
            if attrs_dict.get("property") == "og:image":
                self.image = attrs_dict.get("content", "")
            elif attrs_dict.get("property") == "article:published_time":
                self.date = attrs_dict.get("content", "")

    def handle_data(self, data):
        if self.in_title:
            self.title = data.strip()

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_title = False


def extract_projet52_articles():
    """Extract all projet-52 articles with their metadata"""
    blog_dir = "/home/blatinier/git/melmelboo-static/blog"
    articles = []

    # Find all articles with projet-52 tag
    for root, dirs, files in os.walk(blog_dir):
        if "index.html" in files:
            filepath = os.path.join(root, "index.html")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'projet-52' in content.lower() or 'tag-projet-52' in content:
                        parser = ArticleMetadataParser()
                        parser.feed(content)

                        if parser.date:
                            try:
                                date = datetime.fromisoformat(parser.date.replace('Z', '+00:00'))
                                articles.append({
                                    'title': parser.title,
                                    'image': parser.image,
                                    'date': date,
                                    'year': date.year
                                })
                            except:
                                pass
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    # Sort by date
    articles.sort(key=lambda x: x['date'], reverse=True)

    # Split by year
    p52_2015 = [a for a in articles if a['year'] == 2015]
    p52_2016 = [a for a in articles if a['year'] == 2016]

    return p52_2015, p52_2016


if __name__ == "__main__":
    p52_2015, p52_2016 = extract_projet52_articles()
    print(f"Found {len(p52_2015)} articles from 2015")
    print(f"Found {len(p52_2016)} articles from 2016")

    # Generate HTML for 2015
    print("\n=== 2015 ===")
    for i, article in enumerate(p52_2015[:5]):  # First 5 only
        print(f"{article['title']}: {article['image']}")

    # Generate HTML for 2016
    print("\n=== 2016 ===")
    for i, article in enumerate(p52_2016[:5]):  # First 5 only
        print(f"{article['title']}: {article['image']}")
