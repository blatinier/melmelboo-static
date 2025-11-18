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
                pass

    # Sort by date descending (most recent first)
    articles.sort(key=lambda x: x['date'], reverse=True)

    # Split by year
    p52_2015 = [a for a in articles if a['year'] == 2015]
    p52_2016 = [a for a in articles if a['year'] == 2016]

    return p52_2015, p52_2016


def generate_html_rows(articles):
    """Generate HTML rows with 3 images per row"""
    html_parts = []
    html_parts.append('    <div class="row">')

    for i, article in enumerate(articles):
        if i > 0 and i % 3 == 0:
            html_parts.append('    </div>')
            html_parts.append('    <div class="row">')

        html_parts.append(f'''      <div class="col-lg-4 col-xs-12 row-images">
        <img src="{article['image']}" alt="{article['title']}"
             title="{article['title']}" style="width:100%" />
      </div>''')

    html_parts.append('    </div>')
    return '\n'.join(html_parts)


def generate_projects_page():
    p52_2015, p52_2016 = extract_projet52_articles()

    print(f"Generating page with {len(p52_2015)} articles from 2015 and {len(p52_2016)} from 2016")

    html_2015 = generate_html_rows(p52_2015)
    html_2016 = generate_html_rows(p52_2016)

    page_content = f'''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />

    <title>Mes projets photographiques - Melmelboo</title>
    <meta name="keywords" content="blog, melmelboo, frippes, ecolo, ecologie, recyclage, naturel, astuces, bricolage, truc, bloubiboulga" />
    <meta name="description" content="Mes projets photographiques" />

    <meta name="HandheldFriendly" content="True" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <link rel="shortcut icon" href="../images/favicon.ico">

    <link rel="stylesheet" type="text/css" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="../css/screen.css" />
    <link rel="stylesheet" type="text/css" href="../css/isso.css" />
    <link rel="stylesheet" type="text/css" href="../css/slick.css"/>
    <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Merriweather:300,700,700italic,300italic%7COpen+Sans:700,400" />
    <link rel='stylesheet' href='//fonts.googleapis.com/css?subset=latin%2Clatin-ext%2Ccyrillic%2Ccyrillic-ext&#038;family=Lato%3A300%2C300italic%2C400%2C400italic%2C700%2C700italic%2C900%2C900italic%7CQuicksand%3A300%2C300italic%2C400%2C400italic%2C700%2C700italic%2C900%2C900italic+rel%3D%27stylesheet%27+type%3D%27text%2Fcss&#038;ver=4.1.1' type='text/css' media='all' />
    <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Open+Sans+Condensed:300" />
    <link rel="stylesheet" type="text/css" href="../css/shadowbox.css" />
    <link rel="canonical" href="//www.melmelboo.fr/projects" />
    <meta name="referrer" content="origin" />

    <meta property="og:site_name" content="Melmelboo" />
    <meta property="og:type" content="website" />
    <meta property="og:title" content="Mes projets photographiques - Melmelboo" />
    <meta property="og:description" content="Mes projets photographiques" />
    <meta property="og:url" content="https://www.melmelboo.fr/projects" />
    <meta name="twitter:card" content="summary" />
    <meta name="twitter:title" content="Mes projets photographiques - Melmelboo" />
    <meta name="twitter:description" content="Mes projets photographiques" />
    <meta name="twitter:url" content="https://www.melmelboo.fr/projects" />

    <script type="application/ld+json">
{{
    "@context": "https://schema.org",
    "@type": "Website",
    "publisher": "Melmelboo",
    "url": "https://www.melmelboo.fr/projects",
    "description": "Mes projets photographiques"
}}
    </script>
    <link rel="alternate" type="application/rss+xml" title="Melmelboo" href="https://www.melmelboo.fr/blog/rss/" />
<script type="text/javascript">
  var _paq = _paq || [];
  _paq.push(["setDomains", ["*.melmelboo.fr","*.www.melmelboo.fr"]]);
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  (function() {{
    var u="//stats.melmelboo.fr/";
    _paq.push(['setTrackerUrl', u+'piwik.php']);
    _paq.push(['setSiteId', 1]);
    var d=document, g=d.createElement('script'), s=d.getElementsByTagName('script')[0];
    g.type='text/javascript'; g.async=true; g.defer=true; g.src=u+'piwik.js'; s.parentNode.insertBefore(g,s);
  }})();
</script>
</head>
<body class="home-template nav-closed">
<noscript><p><img src="//stats.melmelboo.fr/piwik.php?idsite=1" style="border:0;" alt="" /></p></noscript>
<!-- End Piwik Code -->
<div class="site-wrapper container-fluid">
<div class="row">
  <button type="button" data-toggle="collapse"
          data-target="#site-menu" id="menu-drop">
    <img src="../images/icon-menu.svg" alt="menu" />
  </button>
  <div class="col-lg-3 collapse" id="site-menu">
    <nav class="col-lg-3 sidebar navbar-fixed-top nav-menu">
      <div class="container-fluid">
      <img id="logo" src="../images/header.jpg" alt="Melmelboo"
           onclick="javascript:window.location='/'" />
      <ul class="nav nav-sidebar nav-stacked" id="main-menu">
        <li class="visible-md-block visible-lg-block"><br /></li>
        <li role="presentation">
            <a title="Le blog" href="/blog/">Blog</a>
        </li>
        <li class="visible-md-block visible-lg-block"><br /></li>
        <li role="presentation">
            <a title="Moi !" href="/blog/qui-suis-je/">Qui suis-je ?</a>
        </li>
        <li role="presentation">
          <a class="current" title="En image !" href="/projects">Projet photo</a>
        </li>
        <li role="presentation">
            <a title="Tour du monde" href="/blog/tour-du-monde">Tour du monde</a>
        </li>
        <li role="presentation">
            <a title="Contactez moi !" href="/contact-me">Me Contacter</a>
        </li>
        <li role="presentation">
          <input type="image" id="submit-search"
                 src="../images/search.svg" alt="Search" />
          <input type="text" id="search" placeholder="rechercher" />
        </li>
      </ul>
      <ul class="social">
        <li>
          <a title="Instagram" href="//instagram.com/hellomelmelboo">
            <img class="social_icon"
                 src="../images/social/instagram.png"
                 alt="Instagram" />
          </a>
        </li>
        <li>
          <a title="Facebook" href="//www.facebook.com/melmelboo">
            <img class="social_icon"
                 src="../images/social/facebook.png"
                 alt="Facebook" />
          </a>
        </li>
        <li>
          <a title="Hellocoton" href="http://www.hellocoton.fr/mapage/melmelboo">
            <img class="social_icon"
                 src="../images/social/hellocoton.png"
                 alt="Hellocoton" />
          </a>
        </li>
        <li>
          <a title="Pinterest" href="//www.pinterest.com/melmelboo">
            <img class="social_icon"
                 src="../images/social/pinterest.png"
                 alt="Pinterest" />
          </a>
        </li>
        <li>
          <a title="Flux RSS" href="/blog/rss">
            <img class="social_icon"
                 src="../images/social/feed.png"
                 alt="RSS" />
          </a>
        </li>
      </ul>
      </div>
    </nav>
  </div>
  <main class="content col-lg-8">
<article class="post page">
  <header class="post-header">
    <h1 class="post-title">Mes projets photographiques</h1>
  </header>
  <section class="post-content">
<ul class="nav nav-tabs" role="tablist">
  <li class="active">
    <a class="sub-title" href="#p52_2016" role="tab"
       style="margin: 0;"
       data-toggle="tab">Projet 52 - 2016</a>
  </li>
  <li>
    <a class="sub-title" href="#p52_2015" role="tab"
       style="margin: 0;"
       data-toggle="tab">Projet 52 - 2015</a>
  </li>
  <li>
    <a class="sub-title" href="#children_month" role="tab"
       style="margin: 0;"
       data-toggle="tab">Au fil des mois</a>
  </li>
</ul>
<div class="tab-content" style="margin-top: 20px;">
  <div class="tab-pane active" id="p52_2016">
<p>
Voici donc notre galerie de portraits de famille ! Cette année a été particulière pour nous car notre famille s'est agrandie.
Nous nous sommes donc amusé à nous photographier tous ensemble une fois par semaine pour <strong>le projet 52 - 2016</strong>.
On trouve rigolo de voir s'agrandir et évoluer notre famille au fil des semaines.
Nous comptons imprimer un livre à emporter avec nous en voyage et qui clôturera joliement cette série 2016.
N'hésitez pas à cliquer sur les photographies pour les agrandir.</p>
<h2 class="sub-title">Un portrait de famille, chaque semaine, en 2016</h2>
{html_2016}
  </div>
  <div class="tab-pane" id="p52_2015">
<p>Charlie n'a pas encore un an quand je commence cette série qui rend compte d'instants anodins de notre quotidien.
Elle change si vite ! Je veux capturer les indices de cette évolution rapide, c'est pourquoi je choisis
d'immortaliser un de ces instants chaque semaine pour <strong>le projet 52 - 2015</strong>.
Et puis je dois bien avouer que je la trouve très photogénique cette petite magicienne du bonheur...
c'est un régale de la photographier ! Depuis, nous feuilletons régulièrement le chouette livre tiré de ce projet.</p>
<h2 class="sub-title">Un portrait de Charlie, chaque semaine, en 2015</h2>
{html_2015}
  </div>
  <div class="tab-pane" id="children_month">
<p>À la naissance de ma fille, Charlie, je décide de la photographier chaque mois pendant un an à sa date anniversaire.
Toujours sur le même tapis -qui est son espace de jeu dans le salon- afin de l'observer grandir.
Le résultat est un tableau de douze photographies témoignant de sa première année de vie.
Tout simplement ma <strong>Charlie au fil des mois</strong>.</p>
<p>Comme pour sa sœur, je souhaite conserver un témoignage succinct de la première année de vie de mon fils, Gaspard.
Je décide donc de le photographier chaque mois sur la couverture aux cent vœux de Charlie qui a une très forte
signification pour nous et qu'on utilise très souvent comme espace de jeu. Une année résumée en douze clichés
sélectionnés parmis tous les autres. Le regard amoureux d'une maman sur son tout petit.
Tout simplement mon <strong>Gaspard au fil des mois</strong>.</p>
<h2 class="sub-title">Un mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_un_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_au_fil_des_mois02b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Deux mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width:100%" src="//www.melmelboo.fr/img/articles/2014/Charlie_2_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width:100%" src="//www.melmelboo.fr/img/articles/2017/Gaspard_2_mois02b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Trois mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie123_03.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_trois_mois02b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Quatre mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_4_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_4_mois01b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Cinq mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_5_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_5_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Six mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_6_mois04.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_6mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Sept mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_7mois03.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_sept_mois01b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Huit mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie_8_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_8_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Neuf mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2014/Charlie123_09.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_9_mois01b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Dix mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2015/Charlie_dix_mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_10_mois01b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Onze mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2015/Charlie11mois01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2017/Gaspard_11_mois02b.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>

<h2 class="sub-title">Douze mois</h2>

<div class="row">
<div class="col-xs-6">
  <img style="width: 100%;" src="//www.melmelboo.fr/img/articles/2015/Anniversaire_1an_Charlie01.JPG" alt="Charlie et Gaspard au fil des mois, la première année" />
</div>
</div>
  </div>
</div>
  </section>
</article>
</main>
</div>
</div>
<script type="text/javascript" src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
<script async type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
<script type="text/javascript" src="../js/shadowbox.js"></script>
<script type="text/javascript" src="../js/search.js"></script>
<script type="text/javascript">
    Shadowbox.init();
    $(function(){{
        $(".post-content img").each(function(index){{
            $(this).wrap('<a href="'+$(this).attr("src")+'" title="'+$(this).attr("alt")+'" rel="shadowbox[Gallerie]" />');
        }});
    }});
</script>
</body>
</html>
'''

    # Write to file
    os.makedirs("/home/blatinier/git/melmelboo-static/projects", exist_ok=True)
    with open("/home/blatinier/git/melmelboo-static/projects/index.html", 'w', encoding='utf-8') as f:
        f.write(page_content)

    print(f"Generated /home/blatinier/git/melmelboo-static/projects/index.html")


if __name__ == "__main__":
    generate_projects_page()
