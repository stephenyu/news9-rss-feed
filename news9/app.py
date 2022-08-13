import requests
from bs4 import BeautifulSoup
from dateutil import parser
from datetime import datetime
from rfeed import *
from flask import Flask
# import redis
# r = redis.Redis(host='redis', port=6379, db=0)

app = Flask(__name__)

def get_article_date(article_url):
    response = requests.get(article_url)
    parsed_html = BeautifulSoup(response.text, "html.parser")

    gallery_date = parsed_html.select('span[class*="DisplayDate"]')

    if (len(gallery_date) == 0):
        dateStr = parsed_html.find(name='time', attrs={'class': 'text--byline'})['datetime']
        date = parser.parse(dateStr)
        return date
    else:
        dateStr = gallery_date[0].string
        date = parser.parse(dateStr)
        return date

def get_news():
    response = requests.get('https://www.9news.com.au/sydney')
    parsed_html = BeautifulSoup(response.text, "html.parser")

    stories = parsed_html.body.findAll(name='div', attrs={'class':'story__details'})

    items = []

    for story in stories[:20]:
        link = story.find(name="a").get('href')
        title = story.find(name="span", attrs={'class': 'story__headline__text'}).text
        abstract = story.find(name="div", attrs={'class': 'story__abstract'}).text

        # possibleDate = r.get(link)

        # if (possibleDate):
        #     date = parser.parse(possibleDate)
        # else:
        date = get_article_date(link)
            # r.set(link, date.isoformat())

        item = Item(
            title = title,
            link = link,
            description=abstract,
            guid = Guid(link),
            pubDate = date)

        items.append(item)

    return items

print(get_news())
# @app.route("/")
# def index():
#    items = get_news()

#    feed = Feed(
#        title = "9news: Sydney",
#        link = "https://www.9news.com.au/sydney",
#        description = "9news Sydney Feed",
#        language = "en-US",
#        lastBuildDate = datetime.now(),
#        items = items)

#    return feed.rss()
