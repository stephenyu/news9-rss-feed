import requests
from bs4 import BeautifulSoup
from datetime import datetime
import dateutil.parser
from urllib.parse import urlparse
from urllib.parse import parse_qs
from rfeed import *
from flask import Flask
import redis

APP_PREFIX = "skimfeed"

app = Flask(__name__)
r = redis.Redis(host='redis', port=6379, db=0)

def get_date(url):
    possibleDate = r.get(APP_PREFIX + url)

    if (possibleDate):
        date = dateutil.parser.isoparse(possibleDate)
        return date
    else:
        date = datetime.now()
        r.set(APP_PREFIX + url, date.isoformat())
        return date

def extract_url(skimfeed_url):
    parsed = urlparse(skimfeed_url)
    targetUrl = parse_qs(parsed.query)['u'][0]

    parsedTarget = urlparse(targetUrl)
    hostname = parsedTarget.hostname

    return hostname, targetUrl

def get_items(parsed_list):
    ulEle = parsed_list[0].find(name="ul")
    listItems = ulEle.find_all(name="li")

    items = []
    for liEle in listItems[:30]:
        anchors = liEle.find_all(name="a")

        primaryLink = anchors[0]
        link = primaryLink.get('href')
        title = primaryLink.text
        hostname, target = extract_url(link)
        date = get_date(link)

        itemTitle = "{} ({})".format(title, hostname)
        description = title

        try:
           if (anchors[1]):
              ycombinator = anchors[1].get('href')
              hostname, ycombinatorComments = extract_url(ycombinator)
              description = "YCombinator Comments: <a href='{}'>Link</a>".format(ycombinatorComments)
        except IndexError:
           description = title

        item = Item(
            title = itemTitle,
            link = target,
            description = description,
            guid = Guid(link),
            pubDate = date)

        items.append(item)

    return items


def get_articles():
    response = requests.get('https://skimfeed.com/techpop.html')
    parsed_html = BeautifulSoup(response.text, "html.parser")

    popular_news = parsed_html.body.findAll(name='div', attrs={'id':'popboxy'})
    latest_news = parsed_html.body.findAll(name='div', attrs={'id':'newboxy'})

    popular_items = get_items(popular_news)
    latest_items = get_items(latest_news)

    return popular_items + latest_items

@app.route("/")
def index():
   items = get_articles()

   feed = Feed(
       title = "Skimfeed",
       link = 'https://skimfeed.com/techpop.html',
       description = "Skimfeed RSS: Popular and Latest",
       language = "en-US",
       lastBuildDate = datetime.now(),
       items = items)

   return feed.rss()
