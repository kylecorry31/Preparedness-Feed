from . import atom, rss
from datetime import datetime
from bs4 import BeautifulSoup

def get_items():
    feed_url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.atom"
    items = atom.load_feed(feed_url)
    for item in items:
        item['source'] = "USGS"
        item['summary'] = item['raw_summary']
        soup = BeautifulSoup(item['summary'], 'html.parser')
        item['summary'] = '\n'.join(soup.stripped_strings)
        item['type'] = "Significant Earthquake"

    feed_url = "https://water.usgs.gov/alerts/project_alert.xml"
    water_items = rss.load_feed(feed_url)
    for item in water_items:
        item['source'] = "USGS"
        item['type'] = "Water"
        item['link'] = item['link'].replace('http://', 'https://')

    items += water_items
    
    # Remove items older than 1 week
    items = [item for item in items if item['pub_date'] > int((datetime.now().timestamp()) - (7 * 24 * 3600))]

    # Volcano
    # https://volcanoes.usgs.gov/rss/vhpcaprss.xml
    
    return items
